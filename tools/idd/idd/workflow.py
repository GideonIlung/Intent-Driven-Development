"""init, status, handoff."""
from __future__ import annotations

import json
import re
import shutil

from . import check, parse
from .common import MAIN_FILE, MODES, ROOT, Ctx, IddError, load_ctx, rel, set_meta

FILES = {
    "change": ["intent.md", "scenarios.md", "nodes.md", "pseudo.md"],
    "review": ["report.md", "scenarios.md", "nodes.md", "pseudo.md"],
    "investigate": ["report.md", "scenarios.md", "nodes.md", "pseudo.md"],
    "spike": ["notes.md"],
}


def init(mode: str, slug: str, flags: list[str], cap: str | None) -> str:
    if mode not in MODES:
        raise IddError(f"mode must be one of {', '.join(MODES)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise IddError("slug: lowercase letters, digits and dashes only")
    d = ROOT / "work" / MODES[mode] / slug
    if d.exists():
        raise IddError(f"{rel(d)} already exists")
    d.mkdir(parents=True)
    for f in FILES[mode]:
        src = ROOT / "templates" / f
        text = src.read_text() if src.exists() else f"# <slug>\n"
        (d / f).write_text(text.replace("<slug>", slug))
    cap = cap or slug.split("-")[0]
    main = d / MAIN_FILE[mode]
    meta = {"mode": mode, "capability": cap, "status": "draft" if mode == "change" else "open"}
    if mode == "change":
        meta["flags"] = [f"--{x.lstrip('-')}" for x in flags]
        (d / "progress.md").write_text(f"# progress: {slug}\n\n")
    set_meta(main, **meta)
    if mode == "spike":
        (d / "scratch").mkdir()
    if mode in ("review", "investigate"):
        (d / "probes").mkdir()
    green = mode == "change" and not (ROOT / "specs" / cap).exists()
    return f"{rel(d)} created (capability: {cap}{', greenfield' if green else ''})"


def _has_findings(ctx: Ctx, heading: str) -> bool:
    return bool(parse.section_text(ctx.main.read_text(), heading)) if ctx.main.exists() else False


def status(ctx: Ctx) -> str:
    m = ctx.model
    if ctx.mode == "change":
        prd = ctx.dir / "prd.gen.json"
        if prd.exists():
            stories = json.loads(prd.read_text())["stories"]
            left = [s["id"] for s in stories if not s["done"]]
            return f"shipping: {len(stories) - len(left)}/{len(stories)} stories done" + (f", next {left[0]}" if left else ", next: finish")
        no_scen = not ctx.delta.scenarios and not ctx.delta.removed_tags
        if no_scen and not ({"refactor", "remove", "migrate"} & set(ctx.flags)):
            return "next: scenarios"
        steps = {st.box for s in ctx.delta.scenarios for st in s.steps if st.box}
        calls = {b for p in ctx.delta.procs for b, _ in p.calls()}
        if (steps | calls) - set(m.nodes):
            return "next: nodes (missing: " + ", ".join(sorted((steps | calls) - set(m.nodes))) + ")"
        if not ctx.delta.procs and not ctx.delta.removed_procs:
            return "next: pseudo"
        err, _, _ = check.trace_check(ctx)
        return f"fix: {len(err)} trace-check errors" if err else "next: ship"
    if ctx.mode == "review":
        if not m.procs:
            return "next: extract (scripts/idd extract <slug> <path>)"
        if any(all(ln.structural or ln.code.strip().startswith("//") for ln in p.lines[1:]) for p in m.procs.values()):
            return "next: pseudo (stubs still empty)"
        if not m.scenarios:
            return "next: scenarios"
        probes = [f for f in (ctx.dir / "probes").glob("*") if f.is_file()] if (ctx.dir / "probes").exists() else []
        if not probes:
            return "next: probe"
        if not _has_findings(ctx, "Findings"):
            return "next: report"
        return "next: finish"
    if ctx.mode == "investigate":
        if "X" not in m.scenarios:
            return "next: write @X failing scenario"
        if not _has_findings(ctx, "Root cause"):
            return "next: trace + probe (repeat until root cause proven)"
        return "next: finish"
    if not _has_findings(ctx, "Answer"):
        return "next: hack, log in notes.md, then fill ## Answer"
    return "next: finish"


def handoff(ctx: Ctx) -> str:
    if ctx.mode != "investigate":
        raise IddError("handoff is for investigations")
    x = ctx.model.scenarios.get("X")
    if not x:
        raise IddError("no @X scenario to hand off")
    slug = f"{ctx.slug}-fix"
    msg = init("change", slug, ["hotfix"], ctx.cap)
    d = ROOT / "work" / "changes" / slug
    existing = {s.tag for s in parse.parse_dir(ctx.spec_dir, delta=False).scenarios}
    tag = parse.next_tag(existing)
    raw = re.sub(r"@X\b", f"@{tag}", x.raw)
    (d / "scenarios.md").write_text(f"# {slug}\n\n## ADDED\n\n```gherkin\n{raw}\n```\n\n## MODIFIED\n\n## REMOVED\n")
    report = ctx.main.read_text()
    intent = d / "intent.md"
    text = intent.read_text()
    why = parse.section_text(report, "Symptom") or "see investigation"
    cause = parse.section_text(report, "Root cause")
    path = parse.section_text(report, "Path")
    text = text.replace("## Why\n", f"## Why\n{why}\n\nRoot cause: {cause}\n", 1)
    text = text.replace("## Touched boxes\n", f"## Touched boxes\n{path}\n", 1)
    intent.write_text(text)
    return f"{msg}\nseeded with @{tag} (was @X). next: review intent.md, then /change-continue {slug}"
