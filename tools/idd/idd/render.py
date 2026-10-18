"""view.gen.html: diagram, scenarios and pseudo code joined by path colour."""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date

from . import check, graph, parse
from .common import ROOT, Ctx, rel

PALETTE = ["#1D9E75", "#D85A30", "#7F77DD", "#BA7517", "#378ADD", "#D4537E", "#639922", "#E24B4A"]
SHAPE = {"entry": ('(["', '"])'), "op": ('["', '"]'), "cond": ('{{"', '"}}'), "store": ('[("', '")]'), "file": ('[/"', '"/]')}
TOKEN = re.compile(
    r'(?P<str>"[^"]*")|(?P<call>\b[A-Z][A-Z0-9_]*\.[A-Z][A-Z0-9_]*\b)'
    r"|(?P<kw>\b(?:procedure|end|if|then|else|for|each|in|while|do|return|not|and|or|requires|ensures)\b)"
    r"|(?P<cm>//.*$)"
)


def colours(tags: list[str]) -> dict[str, str]:
    return {t: PALETTE[i % len(PALETTE)] for i, t in enumerate(tags)}


def mermaid(model: parse.Model, tag: str | None, colour: str | None, info: dict) -> str:
    lines = ["flowchart TD"]
    for n in sorted(model.nodes.values(), key=lambda n: n.id):
        a, b = SHAPE.get(n.shape, SHAPE["op"])
        label = html.escape(n.label).replace('"', "'")
        lines.append(f'  n_{n.id}{a}<b>{n.id}</b><br/>{label}{b}')
    es = sorted(graph.edges(model).items())
    for (x, y), meths in es:
        lab = ", ".join(sorted(m.lower() for m in meths))
        lines.append(f"  n_{x} -->|{lab}| n_{y}")
    if tag and tag in info:
        on, path = info[tag]["boxes"], info[tag]["edges"]
        lines.append(f"  classDef on stroke:{colour},stroke-width:3px")
        lines.append("  classDef dim opacity:0.3")
        if on & set(model.nodes):
            lines.append("  class " + ",".join(f"n_{b}" for b in sorted(on & set(model.nodes))) + " on")
        off = set(model.nodes) - on
        if off:
            lines.append("  class " + ",".join(f"n_{b}" for b in sorted(off)) + " dim")
        for i, ((x, y), _) in enumerate(es):
            style = f"stroke:{colour},stroke-width:3px" if (x, y) in path else "opacity:0.2"
            lines.append(f"  linkStyle {i} {style}")
    return "\n".join(lines)


def code_html(code: str) -> str:
    out, pos = [], 0
    for m in TOKEN.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        out.append(f'<span class="{m.lastgroup}">{html.escape(m.group())}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return "".join(out)


def dots(tags, col) -> str:
    return "".join(f'<i style="background:{col[t]}" title="@{t}"></i>' for t in sorted(tags, key=parse.tag_key) if t in col)


def render(ctx: Ctx, archive: bool = False) -> str:
    m = ctx.model
    tags = sorted(m.scenarios, key=parse.tag_key)
    col = colours(tags)
    info = graph.tag_info(m)
    err, warn, stats = check.trace_check(ctx)
    delta_tags = ctx.delta_tags()
    delta_procs = {p.name for p in ctx.delta.procs}
    focus = bool(delta_tags or delta_procs) and ctx.mode == "change"

    views = {"all": mermaid(m, None, None, info)}
    for t in tags:
        views[t] = mermaid(m, t, col[t], info)

    chips = ['<button class="chip on" data-v="all">All paths</button>']
    for t in tags:
        s = m.scenarios[t]
        mark = " delta" if t in delta_tags else ""
        chips.append(
            f'<button class="chip{mark}" data-v="{t}"><i style="background:{col[t]}"></i>@{t} {html.escape(s.name)}</button>'
        )

    scen = []
    for t in tags:
        if focus and t not in delta_tags:
            continue
        s = m.scenarios[t]
        rows = [f'<div class="ln" data-t=" {t} "><b class="kw">@{t}</b> <b>{html.escape(s.name)}</b>'
                f'<em class="sec">{s.section.lower()}</em></div>']
        for st in s.steps:
            box = f'<span class="box">{st.box}</span>' if st.box else ""
            rows.append(f'<div class="ln" data-t=" {t} "><span class="kw">{st.kw}</span> {html.escape(st.text)} {box}</div>')
        scen.append(f'<div class="block" style="--c:{col[t]}">' + "".join(rows) + "</div>")

    pse = []
    for p in sorted(m.procs.values(), key=lambda p: p.name):
        if focus and p.name not in delta_procs and not (p.tags() & delta_tags):
            continue
        rows = []
        for ln in p.lines:
            t = " ".join(sorted(ln.tags))
            rows.append(f'<div class="ln" data-t=" {t} "><span class="g">{dots(ln.tags, col)}</span>{code_html(ln.code)}</div>')
        sec = p.section.lower()
        pse.append(f'<div class="block"><div class="ph">{p.name}<em class="sec">{sec}</em></div>' + "".join(rows) + "</div>")

    removed = sorted(ctx.delta.removed_tags) + sorted(ctx.delta.removed_nodes) + sorted(ctx.delta.removed_procs)
    rem = f'<p class="rem">Removed: {html.escape(", ".join(removed))}</p>' if removed else ""
    status = check.format_report(err, warn, stats)
    flags = " ".join("--" + f for f in ctx.flags)

    page = TEMPLATE
    for k, v in {
        "TITLE": html.escape(ctx.slug),
        "MODE": html.escape(f"{ctx.mode} {flags}".strip()),
        "CAP": html.escape(ctx.cap),
        "STATE": "ok" if not err else "bad",
        "STATUS": html.escape(status),
        "CHIPS": "".join(chips),
        "SCEN": "".join(scen) or '<p class="empty">No scenarios yet. Run /change-continue.</p>',
        "PSEUDO": "".join(pse) or '<p class="empty">No pseudo code yet.</p>',
        "REMOVED": rem,
        "VIEWS": json.dumps(views),
        "DATE": date.today().isoformat(),
    }.items():
        page = page.replace("%%" + k + "%%", v)
    out = ctx.dir / "view.gen.html"
    out.write_text(page)
    if archive:
        dest = ROOT / "archive" / f"{date.today().isoformat()}-{ctx.slug}"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(ctx.dir), dest)
        (dest / "view.gen.html").rename(dest / "view.html")
        return rel(dest / "view.html")
    return rel(out)


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<style>
:root{--bg:#F7F8F6;--ink:#1E2A2F;--muted:#5E6B70;--rule:#D5DAD6;--panel:#FFFFFF;--ok:#1D7A5A;--bad:#B23A2B;
--sans:system-ui,-apple-system,"Segoe UI",sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#1A1F21;--ink:#E3E7E4;--muted:#99A4A0;--rule:#34403F;--panel:#222A2C;--ok:#5DCAA5;--bad:#F09595}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 var(--sans)}
header{padding:20px 24px 12px;border-bottom:1px solid var(--rule)}
h1{font-size:22px;margin:0 0 2px;font-weight:600;letter-spacing:-.01em}
.meta{color:var(--muted);font-size:13px}
pre.status{margin:12px 0 0;font:12px/1.6 var(--mono);white-space:pre-wrap;padding:8px 12px;border-left:3px solid var(--ok);background:var(--panel)}
pre.status.bad{border-color:var(--bad)}
main{padding:16px 24px 40px;max-width:1400px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.chip{font:13px var(--sans);color:var(--ink);background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:5px 10px;cursor:pointer;display:flex;align-items:center;gap:6px}
.chip i{width:9px;height:9px;border-radius:50%;display:inline-block}
.chip.delta{font-weight:600}.chip.on{outline:2px solid var(--ink);outline-offset:-1px}
.chip:focus-visible{outline:2px solid #378ADD}
#dg{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:12px;overflow-x:auto;min-height:200px}
#dg svg{max-width:100%;height:auto}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:16px;margin-top:16px}
@media (max-width:900px){.cols{grid-template-columns:1fr}}
h2{font-size:14px;font-weight:600;margin:0 0 8px;color:var(--muted)}
.block{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:8px 0;margin-bottom:10px;overflow-x:auto}
.ph{font:600 12px var(--mono);padding:0 12px 6px;color:var(--muted)}
.ln{font:12.5px/1.75 var(--mono);white-space:pre;padding:0 12px;border-left:3px solid transparent;transition:opacity .15s}
.ln.dim{opacity:.28}.ln.hit{border-left-color:var(--c,#888)}
.g{display:inline-flex;gap:2px;width:30px;vertical-align:middle}.g i{width:6px;height:6px;border-radius:50%;display:inline-block}
.kw{color:#7F77DD}.call{color:#BA7517}.str{color:#1D9E75}.cm{color:var(--muted)}
.box{font:11px var(--sans);border:1px solid var(--rule);border-radius:4px;padding:0 5px;color:var(--muted)}
.sec{font:11px var(--sans);color:var(--muted);margin-left:8px;font-style:normal}
.rem,.empty{color:var(--muted);font-size:13px}
@media (prefers-reduced-motion:reduce){.ln{transition:none}}
</style></head><body>
<header><h1>%%TITLE%%</h1><div class="meta">%%MODE%% in %%CAP%%, rendered %%DATE%%</div>
<pre class="status %%STATE%%">%%STATUS%%</pre></header>
<main>
<div class="chips" role="toolbar" aria-label="Scenario paths">%%CHIPS%%</div>
<div id="dg" aria-label="System diagram"></div>%%REMOVED%%
<div class="cols"><section><h2>Scenarios</h2>%%SCEN%%</section><section><h2>Pseudo code</h2>%%PSEUDO%%</section></div>
</main>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
<script>
const VIEWS=%%VIEWS%%;const dark=matchMedia('(prefers-color-scheme: dark)').matches;let n=0;
const chipCol={};document.querySelectorAll('.chip i').forEach(i=>chipCol[i.parentNode.dataset.v]=i.style.background);
async function draw(v){const el=document.getElementById('dg');
 if(!window.mermaid){el.innerHTML='<pre>'+VIEWS[v].replace(/</g,'&lt;')+'</pre>';return}
 try{const {svg}=await mermaid.render('m'+(n++),VIEWS[v]);el.innerHTML=svg}catch(e){el.textContent='Diagram failed to render: '+e.message}}
function pick(v){document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('on',c.dataset.v===v));
 document.querySelectorAll('.ln').forEach(l=>{const hit=v==='all'||l.dataset.t.includes(' '+v+' ');
  l.classList.toggle('dim',!hit);l.classList.toggle('hit',hit&&v!=='all');if(v!=='all')l.style.setProperty('--c',chipCol[v])});
 draw(v)}
if(window.mermaid)mermaid.initialize({startOnLoad:false,theme:dark?'dark':'neutral',flowchart:{htmlLabels:true}});
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>pick(c.dataset.v));pick('all');
</script></body></html>"""
