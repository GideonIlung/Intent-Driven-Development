"""trace-check, fence and conform."""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

from . import graph, parse
from .common import ROOT, Ctx, config, rel

Issue = tuple[str, int, str]


def trace_check(ctx: Ctx) -> tuple[list[Issue], list[Issue], dict]:
    cfg = config()["limits"]
    m = ctx.model
    err: list[Issue] = list(ctx.base.errors) + list(ctx.delta.errors)
    warn: list[Issue] = []
    e = lambda f, l, msg: err.append((rel(f), l, msg))  # noqa: E731
    w = lambda f, l, msg: warn.append((rel(f), l, msg))  # noqa: E731

    # duplicates + delta sanity
    seen: dict[str, parse.Scenario] = {}
    for s in ctx.delta.scenarios:
        if s.tag in seen:
            e(s.file, s.line, f"@{s.tag} used twice")
        seen[s.tag] = s
        base_tags = {b.tag for b in ctx.base.scenarios}
        if s.section in ("ADDED",) and s.tag in base_tags:
            e(s.file, s.line, f"@{s.tag} already in specs; use MODIFIED or the next free tag")
        if s.section == "MODIFIED" and s.tag not in base_tags:
            w(s.file, s.line, f"@{s.tag} MODIFIED but not in specs")
    for n in ctx.delta.nodes:
        if n.section == "ADDED" and n.id in {b.id for b in ctx.base.nodes}:
            e(n.src, n.line, f"{n.id} already in specs; use MODIFIED")

    # scenarios
    tinfo = graph.tag_info(m)
    for s in m.scenarios.values():
        if not s.steps:
            e(s.file, s.line, f"@{s.tag} has no steps")
            continue
        for st in s.steps:
            if not st.box:
                e(s.file, st.line, f"@{s.tag} step has no [BOX] tag")
            elif st.box not in m.nodes:
                e(s.file, st.line, f"@{s.tag} step box {st.box} not in nodes")
        when = next((st for st in s.steps if st.kw == "When"), None)
        if not when:
            e(s.file, s.line, f"@{s.tag} has no When step")
        elif when.box in m.nodes and m.nodes[when.box].shape != "entry":
            e(s.file, when.line, f"@{s.tag} first When step box {when.box} is not an entry box")
        if s.tag not in tinfo:
            e(s.file, s.line, f"@{s.tag} has no pseudo lines (no path)")
        elif when and when.box:
            ti = tinfo[s.tag]
            if when.box not in ti["boxes"]:
                e(s.file, when.line, f"@{s.tag} path does not start at entry {when.box}")
            else:
                reach, todo = {when.box}, [when.box]
                while todo:
                    a = todo.pop()
                    for x, y in ti["edges"]:
                        if x == a and y not in reach:
                            reach.add(y)
                            todo.append(y)
                lost = ti["boxes"] - reach
                if lost:
                    e(s.file, s.line, f"@{s.tag} path broken: {', '.join(sorted(lost))} not reachable from {when.box}")

    # pseudo
    total = tagged = 0
    for p in m.procs.values():
        if p.box not in m.nodes:
            e(p.file, p.line, f"{p.name}: box {p.box} not in nodes")
        body = [ln for ln in p.lines if not ln.structural and not ln.code.strip().startswith("//")]
        if len(p.lines) > cfg["proc_lines"]:
            w(p.file, p.line, f"{p.name}: {len(p.lines)} lines, consider splitting")
        for ln in body:
            total += 1
            if ln.tags:
                tagged += 1
            else:
                e(p.file, ln.line, f"{p.name}: untagged line (uncovered)")
            for t in ln.tags:
                if t not in m.scenarios:
                    e(p.file, ln.line, f"@{t} used in pseudo but no such scenario")
            for b, meth in ln.calls:
                if b not in m.nodes:
                    e(p.file, ln.line, f"{b}.{meth} called but {b} not in nodes")
                elif f"{b}.{meth}" not in m.procs:
                    e(p.file, ln.line, f"{b}.{meth} called but {b} has no {meth} procedure")

    # nodes
    called = {b for (_, b) in graph.edges(m)}
    owners = {p.box for p in m.procs.values()}
    on_path = set().union(*(i["boxes"] for i in tinfo.values())) if tinfo else set()
    for n in m.nodes.values():
        if n.id not in owners and n.id not in called:
            e(n.src, n.line, f"{n.id} is an orphan: no procedure and nobody calls it")
        elif n.id not in on_path:
            w(n.src, n.line, f"{n.id} is on no scenario path")

    # flags + size
    d_scen = ctx.delta.scenarios
    d_removed = ctx.delta.removed_tags | ctx.delta.removed_nodes | ctx.delta.removed_procs
    touched = ctx.touched()
    main = rel(ctx.main)
    if "refactor" in ctx.flags and (d_scen or ctx.delta.removed_tags):
        e(main, 1, "--refactor: scenario delta must be empty")
    if "hotfix" in ctx.flags:
        if len(touched) > cfg["hotfix_boxes"]:
            e(main, 1, f"--hotfix: {len(touched)} boxes touched (max {cfg['hotfix_boxes']})")
        if len(d_scen) > cfg["hotfix_scenarios"]:
            e(main, 1, f"--hotfix: {len(d_scen)} scenarios (max {cfg['hotfix_scenarios']})")
    if "migrate" in ctx.flags:
        bad = [b for b in touched if b in m.nodes and m.nodes[b].shape not in ("store", "file")]
        if bad:
            e(main, 1, f"--migrate: only store/file boxes may change, not {', '.join(sorted(bad))}")
    if "remove" in ctx.flags and (d_scen or ctx.delta.nodes or ctx.delta.procs):
        e(main, 1, "--remove: delta must be REMOVED only")
    if ctx.mode == "change" and len(touched) > cfg["boxes"]:
        w(main, 1, f"{len(touched)} boxes touched (> {cfg['boxes']}): split the change")
    if ctx.mode == "change" and len(d_scen) > cfg["scenarios"]:
        w(main, 1, f"{len(d_scen)} scenarios (> {cfg['scenarios']}): split the change")

    stats = {
        "scenarios": len(m.scenarios),
        "boxes": len(m.nodes),
        "on_path": len(on_path & set(m.nodes)),
        "arrows": len(graph.edges(m)),
        "lines": total,
        "tagged": tagged,
        "delta": len(d_scen) + len(ctx.delta.nodes) + len(ctx.delta.procs) + len(d_removed),
    }
    return err, warn, stats


def format_report(err, warn, stats) -> str:
    out = []
    if not err:
        out.append(
            f"✓ {stats['scenarios']} scenarios, {stats['on_path']}/{stats['boxes']} boxes on a path, "
            f"{stats['arrows']} arrows, {stats['tagged']}/{stats['lines']} lines tagged"
        )
    for f, l, msg in err:
        out.append(f"✗ {f}:{l}  {msg}")
    for f, l, msg in warn:
        out.append(f"! {f}:{l}  {msg}")
    return "\n".join(out)


# ---------- fence ----------

def fence_files(ctx: Ctx, story: dict) -> list[str]:
    files = []
    for b in story["boxes"]:
        n = ctx.model.nodes.get(b)
        if n and n.file:
            files.append(n.file)
    return sorted(set(files))


def changed_files() -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain", "-uall"], capture_output=True, text=True, cwd=ROOT).stdout
    files = []
    for line in out.splitlines():
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        files.append(path)
    return files


def fence_verify(ctx: Ctx, story: dict) -> list[str]:
    allowed = fence_files(ctx, story)
    dirs = {str(Path(f).parent) for f in allowed}
    always = config()["fence"]["always"]
    bad = []
    for f in changed_files():
        if f.startswith(".idd/") or ".gen." in f or f in allowed:
            continue
        if any(f.startswith(a) or f == a for a in always):
            continue
        if Path(f).name == "__init__.py" and str(Path(f).parent) in dirs:
            continue
        if f.startswith("specs/") or f.startswith("tests/features/"):
            bad.append(f + "  (ralph never edits this)")
            continue
        bad.append(f)
    return bad


# ---------- conform (python only) ----------

def _py_calls(ctx: Ctx) -> dict[str, set[tuple[str, str]]]:
    """'BOX.METHOD' -> calls to other boxes found in real code."""
    stem_box = {}
    for n in ctx.model.nodes.values():
        if n.file.endswith(".py"):
            stem_box[Path(n.file).stem] = n.id
    found: dict[str, set[tuple[str, str]]] = {}
    for n in ctx.model.nodes.values():
        f = ROOT / n.file if n.file else None
        if not f or f.suffix != ".py" or not f.exists():
            continue
        tree = ast.parse(f.read_text())
        alias: dict[str, str] = {}
        names: dict[str, tuple[str, str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    stem = a.name.split(".")[-1]
                    if stem in stem_box:
                        alias[a.asname or stem] = stem_box[stem]
            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[-1]
                for a in node.names:
                    if a.name in stem_box:
                        alias[a.asname or a.name] = stem_box[a.name]
                    elif mod in stem_box:
                        names[a.asname or a.name] = (stem_box[mod], a.name.upper())
        for k, v in list(stem_box.items()):
            alias.setdefault(k, v)
        funcs = [x for x in tree.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for cls in [x for x in tree.body if isinstance(x, ast.ClassDef)]:
            funcs += [x for x in cls.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for fn in funcs:
            calls = set()
            for c in ast.walk(fn):
                if not isinstance(c, ast.Call):
                    continue
                if isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name):
                    box = alias.get(c.func.value.id)
                    if box:
                        calls.add((box, c.func.attr.upper()))
                elif isinstance(c.func, ast.Name) and c.func.id in names:
                    calls.add(names[c.func.id])
            found[f"{n.id}.{fn.name.upper()}"] = {x for x in calls if x[0] != n.id}
    return found


def conform(ctx: Ctx, procs: list[str] | None = None) -> list[str]:
    real = _py_calls(ctx)
    out = []
    for name, p in sorted(ctx.model.procs.items()):
        if procs is not None and name not in procs:
            continue
        if name not in real:
            n = ctx.model.nodes.get(p.box)
            if n and n.file.endswith(".py") and (ROOT / n.file).exists():
                out.append(f"{name}: no function {p.method.lower()} in {n.file}")
            continue
        want = {c for c in p.calls() if c[0] != p.box}
        have = real[name]
        for b, m in sorted(want - have):
            out.append(f"{name}: pseudo calls {b}.{m}, code does not")
        for b, m in sorted(have - want):
            out.append(f"{name}: code calls {b}.{m}, pseudo does not")
    return out
