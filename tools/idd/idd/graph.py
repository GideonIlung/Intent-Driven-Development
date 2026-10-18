"""Call graph derived from pseudo code, per-tag paths, and the context slice."""
from __future__ import annotations

import hashlib
import json

from . import parse
from .common import Ctx, cache, rel


def edges(model: parse.Model) -> dict[tuple[str, str], set[str]]:
    """(caller box, callee box) -> methods called. Same-box calls are not arrows."""
    out: dict[tuple[str, str], set[str]] = {}
    for p in model.procs.values():
        for b, meth in p.calls():
            if b != p.box:
                out.setdefault((p.box, b), set()).add(meth)
    return out


def tag_info(model: parse.Model) -> dict[str, dict]:
    info: dict[str, dict] = {}
    for p in model.procs.values():
        for ln in p.lines:
            for t in ln.tags:
                i = info.setdefault(t, {"procs": set(), "boxes": set(), "edges": set()})
                i["procs"].add(p.name)
                i["boxes"].add(p.box)
                for b, meth in ln.calls:
                    i["boxes"].add(b)
                    if b != p.box:
                        i["edges"].add((p.box, b))
    return info


def neighbours(model: parse.Model, boxes: set[str]) -> set[str]:
    out = set()
    for a, b in edges(model):
        if a in boxes:
            out.add(b)
        if b in boxes:
            out.add(a)
    return out - boxes


def proc_depth(model: parse.Model) -> dict[str, int]:
    memo: dict[str, int] = {}

    def depth(name: str, seen: frozenset) -> int:
        if name in memo:
            return memo[name]
        p = model.procs.get(name)
        if not p or name in seen:
            return 0
        d = 0
        for b, m in p.calls():
            callee = f"{b}.{m}"
            if callee != name:
                d = max(d, 1 + depth(callee, seen | {name}))
        memo[name] = d
        return d

    for n in model.procs:
        depth(n, frozenset())
    return memo


def write_cache(ctx: Ctx) -> None:
    src = "".join(
        f.read_text() for d in (ctx.spec_dir, ctx.dir) for f in sorted(d.glob("*.md")) if f.exists()
    ) if ctx.spec_dir.exists() else "".join(f.read_text() for f in sorted(ctx.dir.glob("*.md")))
    h = hashlib.sha1(src.encode()).hexdigest()
    f = cache(f"graph-{ctx.slug}.gen.json")
    if f.exists() and json.loads(f.read_text()).get("hash") == h:
        return
    data = {
        "hash": h,
        "nodes": {n.id: {"shape": n.shape, "label": n.label, "file": n.file} for n in ctx.model.nodes.values()},
        "edges": [[a, b, sorted(m)] for (a, b), m in sorted(edges(ctx.model).items())],
    }
    f.write_text(json.dumps(data, indent=1))


def slice_text(ctx: Ctx) -> str:
    """Markdown slice for the agent: touched in full, neighbours as signatures, rest omitted."""
    write_cache(ctx)
    m = ctx.model
    touched = ctx.touched()
    if ctx.mode == "investigate":
        for s in ctx.delta.scenarios:
            touched |= {st.box for st in s.steps if st.box}
    nb = neighbours(m, touched)
    missing = sorted(b for b in touched if b not in m.nodes)
    out = [f"# slice: {ctx.slug}", ""]
    out.append(f"- touched: {', '.join(sorted(touched)) or 'none'}")
    out.append(f"- neighbour: {', '.join(sorted(nb)) or 'none'}")
    out.append(f"- not loaded: {len(set(m.nodes) - touched - nb)} box")
    if missing:
        out.append(f"- MISSING from specs: {', '.join(missing)} (baseline via /review-new, or treat as new)")
    out += ["", "## Boxes", "| ID | shape | label | file |", "|---|---|---|---|"]
    for b in sorted(touched | nb):
        if b in m.nodes:
            n = m.nodes[b]
            out.append(f"| {n.id} | {n.shape} | {n.label} | {n.file} |")
    out += ["", "## Touched procedures"]
    for p in sorted(m.procs.values(), key=lambda p: p.name):
        if p.box in touched:
            out += [f"### {p.name}", "```pascal pseudo", p.raw, "```"]
    out += ["", "## Neighbour signatures"]
    for p in sorted(m.procs.values(), key=lambda p: p.name):
        if p.box in nb:
            out.append(f"- `{p.header}`")
    tags = sorted({s.tag for s in m.scenarios.values() if {st.box for st in s.steps} & touched}, key=parse.tag_key)
    out += ["", f"## Scenarios on touched boxes: {' '.join('@' + t for t in tags) or 'none'}"]
    return "\n".join(out) + "\n"


def grow(ctx: Ctx, box: str) -> None:
    f = cache("slice", f"{ctx.slug}.json")
    cur = ctx.grown() | {box}
    f.write_text(json.dumps(sorted(cur)))
