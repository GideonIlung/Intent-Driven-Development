"""Apply a change delta (or a confirmed review) to specs/<cap>/."""
from __future__ import annotations

import re

from . import parse
from .common import Ctx, rel


def _write(ctx: Ctx, model: parse.Model) -> list[str]:
    d = ctx.spec_dir
    d.mkdir(parents=True, exist_ok=True)
    sc = [f"# {ctx.cap} scenarios", ""]
    for t in sorted(model.scenarios, key=parse.tag_key):
        sc += ["```gherkin", model.scenarios[t].raw, "```", ""]
    nd = [f"# {ctx.cap} nodes", "", "| ID | shape | label | file |", "|---|---|---|---|"]
    for n in sorted(model.nodes.values(), key=lambda n: n.id):
        nd.append(f"| {n.id} | {n.shape} | {n.label} | {n.file} |")
    ps = [f"# {ctx.cap} pseudo", ""]
    for p in sorted(model.procs.values(), key=lambda p: p.name):
        ps += [f"### {p.name}", "```pascal pseudo", p.raw, "```", ""]
    for name, lines in (("scenarios.md", sc), ("nodes.md", nd), ("pseudo.md", ps)):
        (d / name).write_text("\n".join(lines).rstrip() + "\n")
    return [rel(d / f) for f in ("scenarios.md", "nodes.md", "pseudo.md")]


def merge(ctx: Ctx, baseline: bool = False) -> str:
    model = ctx.model
    dropped = []
    if baseline:
        report = ctx.main.read_text() if ctx.main.exists() else ""
        ok = set()
        for ln in report.splitlines():
            if "CONFIRM" in ln:
                ok |= set(parse.TAG_RE.findall(ln))
        dropped = sorted(set(model.scenarios) - ok, key=parse.tag_key)
        for t in dropped:
            model.scenarios.pop(t)
        if (ctx.spec_dir / "scenarios.md").exists():
            base = parse.parse_dir(ctx.spec_dir, delta=False)
            model = parse.effective(base, ctx.delta)
            for t in dropped:
                model.scenarios.pop(t, None)
    files = _write(ctx, model)
    msg = f"merged into {rel(ctx.spec_dir)}: {len(model.scenarios)} scenarios, {len(model.nodes)} boxes, {len(model.procs)} procedures"
    if dropped:
        msg += f"\nnot confirmed, left out: {' '.join('@' + t for t in dropped)}"
    return msg
