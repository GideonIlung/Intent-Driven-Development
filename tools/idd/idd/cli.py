"""idd <command>. All mechanical work of the harness."""
from __future__ import annotations

import argparse
import sys

from . import check, graph, merge, packet, render, scaffold, stories, workflow
from .common import IddError, load_ctx
from .extract import python_ast
from .gate import gate as run_gate


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="idd", description="IDD harness scripts")
    sub = p.add_subparsers(dest="cmd", required=True)

    def cmd(name, help_, slug=True, **kw):
        s = sub.add_parser(name, help=help_)
        if slug:
            s.add_argument("slug", nargs="?" if kw.get("optional", True) else None)
        return s

    s = sub.add_parser("init", help="create a work folder from templates")
    s.add_argument("mode", choices=["change", "review", "investigate", "spike"])
    s.add_argument("slug")
    for f in ("refactor", "hotfix", "migrate", "remove"):
        s.add_argument(f"--{f}", action="store_true", help=f"change flag: {f}")
    s.add_argument("--cap", help="capability (default: slug before first dash)")
    cmd("status", "next step for a work folder")
    s = cmd("slice", "touched boxes in full, neighbours as signatures")
    s.add_argument("--from", dest="frm", help="investigate: start box")
    s.add_argument("--grow", help="add one box to the slice")
    s = sub.add_parser("extract", help="python code → nodes + pseudo stubs")
    s.add_argument("slug")
    s.add_argument("path")
    cmd("trace-check", "check scenarios, nodes and pseudo agree")
    s = cmd("render", "write view.gen.html")
    s.add_argument("--archive", action="store_true", help="move work folder to archive/")
    s.add_argument("--overview", action="store_true", help="(same view; for review)")
    cmd("stories", "tags → prd.gen.json")
    cmd("scaffold", "scenarios → tests/features/<cap>.feature")
    cmd("next-story", "print next undone story id")
    for name, help_ in (("packet", "write Ralph packet, print path"), ("check", "fence + gate + conform for a story"),
                        ("fence", "print fence files for a story"), ("story-tags", "print @tags of a story"),
                        ("mark-done", "mark a story done")):
        s = sub.add_parser(name, help=help_)
        s.add_argument("slug")
        s.add_argument("story")
        if name == "packet":
            s.add_argument("--try", dest="attempt", type=int, default=1)
        if name == "fence":
            s.add_argument("--verify", action="store_true")
    s = cmd("gate", "run tests")
    s.add_argument("--full", action="store_true")
    s.add_argument("--story")
    s = cmd("conform", "compare real calls with pseudo calls (python)")
    s = cmd("merge", "apply delta to specs/<cap>/")
    s.add_argument("--baseline", action="store_true", help="review: confirmed scenarios only")
    cmd("handoff", "investigation → hotfix change seeded with @X")

    a = p.parse_args(argv)
    try:
        return run(a)
    except IddError as e:
        print(f"idd: {e}", file=sys.stderr)
        return 2


def run(a) -> int:
    c = a.cmd
    if c == "init":
        flags = [f for f in ("refactor", "hotfix", "migrate", "remove") if getattr(a, f)]
        print(workflow.init(a.mode, a.slug, flags, a.cap))
        return 0
    if c == "extract":
        print(python_ast.extract(load_ctx(a.slug), a.path))
        return 0
    ctx = load_ctx(getattr(a, "slug", None))
    if c == "status":
        print(workflow.status(ctx))
    elif c == "slice":
        if a.grow:
            graph.grow(ctx, a.grow.upper())
            ctx = load_ctx(ctx.slug)
        if a.frm:
            graph.grow(ctx, a.frm.upper())
            ctx = load_ctx(ctx.slug)
        print(graph.slice_text(ctx), end="")
    elif c == "trace-check":
        err, warn, stats = check.trace_check(ctx)
        print(check.format_report(err, warn, stats))
        return 1 if err else 0
    elif c == "render":
        print(render.render(ctx, archive=a.archive))
    elif c == "stories":
        prd = stories.write(ctx)
        for s in prd["stories"]:
            tags = " ".join("@" + t for t in s["tags"]) or "-"
            par = f"  parallel with {', '.join(s['parallel_with'])}" if s["parallel_with"] else ""
            print(f"{s['id']:4} {s['kind']:9} {tags:12} {', '.join(s['boxes'])}{par}")
    elif c == "scaffold":
        for f in scaffold.scaffold(ctx):
            print(f)
    elif c == "next-story":
        print(stories.next_story(ctx))
    elif c == "packet":
        print(packet.build(ctx, a.story, a.attempt))
    elif c == "story-tags":
        print(" ".join("@" + t for t in stories.get(ctx, a.story)["tags"]))
    elif c == "mark-done":
        stories.mark_done(ctx, a.story)
    elif c == "fence":
        s = stories.get(ctx, a.story)
        if a.verify:
            bad = check.fence_verify(ctx, s)
            for f in bad:
                print(f"✗ outside fence: {f}")
            return 1 if bad else 0
        print("\n".join(check.fence_files(ctx, s)))
    elif c == "gate":
        s = stories.get(ctx, a.story) if a.story else None
        ok, out = run_gate(ctx, s, full=a.full or s is None)
        print(("✓ gate green" if ok else "✗ gate red\n" + out))
        return 0 if ok else 1
    elif c == "check":
        s = stories.get(ctx, a.story)
        bad = check.fence_verify(ctx, s)
        if bad:
            print("✗ fence:\n" + "\n".join("  " + b for b in bad))
            from .common import cache
            cache("errors", f"{ctx.slug}-{s['id']}.txt").write_text("edited files outside fence:\n" + "\n".join(bad))
            return 1
        ok, out = run_gate(ctx, s)
        if not ok:
            print("✗ gate red\n" + out)
            return 1
        drift = check.conform(ctx, s["procedures"]) if s["kind"] == "build" else []
        from .common import config
        if drift:
            print("! conform:\n" + "\n".join("  " + d for d in drift))
            if config()["conform"].get("strict"):
                return 1
        print(f"✓ {s['id']} fence ok, gate green" + (", conform ok" if not drift else ""))
    elif c == "conform":
        drift = check.conform(ctx)
        print("\n".join(drift) if drift else "✓ code calls match pseudo calls")
        return 1 if drift else 0
    elif c == "merge":
        print(merge.merge(ctx, baseline=a.baseline))
    elif c == "handoff":
        print(workflow.handoff(ctx))
    return 0
