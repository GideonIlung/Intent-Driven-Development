"""Tags → stories (prd.gen.json), story state."""
from __future__ import annotations

import json

from . import graph, parse
from .common import Ctx, IddError, config


def build(ctx: Ctx) -> dict:
    m = ctx.model
    cap = config()["limits"]["group"]
    delta_procs = {p.name: p for p in ctx.delta.procs}
    tags = ctx.delta_tags() | {t for p in delta_procs.values() for t in p.tags()}
    tags = sorted((t for t in tags if t in m.scenarios), key=parse.tag_key)
    procs_of = {t: {n for n, p in delta_procs.items() if t in p.tags()} for t in tags}

    # union tags that share delta procedures
    parent = {t: t for t in tags}

    def find(t):
        while parent[t] != t:
            parent[t] = parent[parent[t]]
            t = parent[t]
        return t

    # entry procedures (CLI.MAIN) touch every path: ignore them when grouping
    hub = {n for n in delta_procs if m.nodes.get(n.split(".")[0]) and m.nodes[n.split(".")[0]].shape == "entry"}
    for a in tags:
        for b in tags:
            if a < b and (procs_of[a] & procs_of[b]) - hub:
                parent[find(b)] = find(a)
    groups: dict[str, list[str]] = {}
    for t in tags:
        groups.setdefault(find(t), []).append(t)
    chunks = []
    for g in groups.values():
        g = sorted(g, key=parse.tag_key)
        chunks += [g[i:i + cap] for i in range(0, len(g), cap)]

    depth = graph.proc_depth(m)

    def boxes_for(procs: set[str], tg: list[str]) -> list[str]:
        b = {n.split(".")[0] for n in procs}
        for t in tg:
            b |= {p.split(".")[0] for p in procs_of.get(t, set())}
        return sorted(b)

    stories = []
    added = [p for p in ctx.delta.procs if p.section == "ADDED"]
    if added:
        names = {p.name for p in added}
        stories.append({"id": "S0", "kind": "skeleton", "tags": [], "procedures": sorted(names),
                        "boxes": sorted({p.box for p in added})})
    def key(g):
        ps = set().union(*(procs_of[t] for t in g)) if g else set()
        return (max((depth.get(p, 0) for p in ps), default=0), parse.tag_key(g[0]))
    for g in sorted(chunks, key=key):
        ps = set().union(*(procs_of[t] for t in g))
        stories.append({"id": f"S{len(stories) + (0 if added else 1)}", "kind": "build", "tags": g,
                        "procedures": sorted(ps), "boxes": boxes_for(ps, g)})
    if ctx.delta.removed_procs or ctx.delta.removed_nodes:
        b = {n.split(".")[0] for n in ctx.delta.removed_procs} | ctx.delta.removed_nodes
        stories.append({"id": f"S{len(stories) + (0 if added else 1)}", "kind": "remove", "tags": [],
                        "procedures": sorted(ctx.delta.removed_procs), "boxes": sorted(b)})
    for s in stories:
        s["files"] = sorted({m.nodes[b].file for b in s["boxes"] if b in m.nodes and m.nodes[b].file})
        s["parallel_with"] = [o["id"] for o in stories if o is not s and not set(o["boxes"]) & set(s["boxes"])]
        s["done"] = False
    return {"slug": ctx.slug, "capability": ctx.cap, "stories": stories}


def write(ctx: Ctx) -> dict:
    f = ctx.dir / "prd.gen.json"
    prd = build(ctx)
    if f.exists():
        old = {(s["kind"], tuple(s["tags"])): s["done"] for s in json.loads(f.read_text())["stories"]}
        for s in prd["stories"]:
            s["done"] = old.get((s["kind"], tuple(s["tags"])), False)
    f.write_text(json.dumps(prd, indent=2))
    return prd


def load(ctx: Ctx) -> dict:
    f = ctx.dir / "prd.gen.json"
    if not f.exists():
        raise IddError("no prd.gen.json: run scripts/idd stories <slug>")
    return json.loads(f.read_text())


def get(ctx: Ctx, sid: str) -> dict:
    for s in load(ctx)["stories"]:
        if s["id"] == sid:
            return s
    raise IddError(f"no story {sid}")


def next_story(ctx: Ctx) -> str:
    return next((s["id"] for s in load(ctx)["stories"] if not s["done"]), "")


def mark_done(ctx: Ctx, sid: str) -> None:
    prd = load(ctx)
    for s in prd["stories"]:
        if s["id"] == sid:
            s["done"] = True
    (ctx.dir / "prd.gen.json").write_text(json.dumps(prd, indent=2))
