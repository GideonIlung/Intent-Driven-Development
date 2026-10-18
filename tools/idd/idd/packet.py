"""Ralph context packet: one story, smallest useful context."""
from __future__ import annotations

from . import check, graph, parse, stories
from .common import ROOT, Ctx, cache, config, rel
from .gate import story_cmd

AGENT = ROOT / ".agents" / "agents" / "ralph.md"


def _strip_fm(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        return text[end + 4:].lstrip() if end != -1 else text
    return text


def build(ctx: Ctx, sid: str, attempt: int) -> str:
    m = ctx.model
    s = stories.get(ctx, sid)
    out = [_strip_fm(AGENT.read_text()) if AGENT.exists() else "you ralph. build one story. stop.", ""]
    out += [f"# story {sid} ({s['kind']}) of change {ctx.slug}", f"attempt {attempt}", ""]
    if s["tags"]:
        out.append("## scenarios")
        for t in s["tags"]:
            out += ["```gherkin", m.scenarios[t].raw, "```"]
    procs = s["procedures"]
    if procs:
        out.append("## pseudo (build these)" if s["kind"] != "remove" else "## remove these procedures")
        for name in procs:
            p = m.procs.get(name) or next((x for x in ctx.base.procs if x.name == name), None)
            if p:
                out += [f"### {name}", "```pascal pseudo", p.raw, "```"]
    called = {f"{b}.{mm}" for n in procs if n in m.procs for b, mm in m.procs[n].calls()} - set(procs)
    callers = {p.name for p in m.procs.values() if p.name not in procs and any(f"{b}.{mm}" in procs for b, mm in p.calls())}
    sig = sorted(called | callers)
    if sig:
        out.append("## neighbour signatures (exist or come later, do not build)")
        out += [f"- `{m.procs[n].header}`" for n in sig if n in m.procs]
    fence = check.fence_files(ctx, s)
    out += ["## fence (only edit these, plus tests/steps/ and __init__.py beside them)"]
    out += [f"- {f}" for f in fence] or ["- (no file column in nodes: ask via SPEC-QUESTION)"]
    for b in s["boxes"]:
        n = m.nodes.get(b)
        if n:
            out.append(f"- box {b} ({n.shape}): {n.label} → {n.file or '?'}")
    out += ["## gate", f"`{story_cmd(ctx, s)}`"]
    if s["tags"]:
        out.append(f"step defs: tests/steps/, feature file: tests/features/{ctx.cap}.feature (generated, read-only)")
    prog = ctx.dir / "progress.md"
    if prog.exists():
        notes = [l for l in prog.read_text().splitlines() if l.strip().startswith("-")][-5:]
        if notes:
            out += ["## notes from earlier stories"] + notes
    err = ROOT / ".idd" / "errors" / f"{ctx.slug}-{sid}.txt"
    if attempt > 1 and err.exists():
        out += ["## last attempt failed with", "```", err.read_text()[-4000:], "```"]
    out.append("\nprogress note → append to " + rel(prog))
    f = cache("packets", f"{ctx.slug}-{sid}-{attempt}.md")
    f.write_text("\n".join(out) + "\n")
    return rel(f)
