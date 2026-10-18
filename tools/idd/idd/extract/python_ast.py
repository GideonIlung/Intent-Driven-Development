"""Python modules → boxes, functions → procedure stubs, calls → arrows. Zero tokens."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from ..common import ROOT, Ctx, IddError, cache, rel

ENTRY = re.compile(r"^(cli|main|app|__main__|run|server)$")
STORE = re.compile(r"(store|db|repo|dao|cache|storage|io)$")
COND = re.compile(r"(valid|check|rule|policy|guard)")


def _files(path: Path) -> list[Path]:
    base = path if path.is_dir() else path.parent
    return sorted(f for f in base.rglob("*.py") if "test" not in f.parts and f.name != "__init__.py")


def _shape(stem: str, tree: ast.Module) -> str:
    main_guard = any(isinstance(n, ast.If) and "__main__" in ast.unparse(n.test) for n in tree.body)
    if main_guard or ENTRY.match(stem):
        return "entry"
    if STORE.search(stem):
        return "store"
    if COND.search(stem):
        return "cond"
    return "op"


def extract(ctx: Ctx, path: str) -> str:
    target = (ROOT / path).resolve()
    if not target.exists():
        raise IddError(f"{path} not found")
    files = _files(target)
    if not files:
        raise IddError(f"no .py files under {path} (R and other languages not supported yet)")
    ids: dict[Path, str] = {}
    for f in files:
        bid = re.sub(r"[^A-Z0-9_]", "_", f.stem.upper())
        if bid in ids.values():
            bid = re.sub(r"[^A-Z0-9_]", "_", f"{f.parent.name}_{f.stem}".upper())
        ids[f] = bid
    stem_box = {f.stem: b for f, b in ids.items()}
    nodes, procs, arrows = [], [], set()
    for f, bid in ids.items():
        tree = ast.parse(f.read_text())
        alias: dict[str, str] = {k: v for k, v in stem_box.items()}
        names: dict[str, tuple[str, str]] = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    st = a.name.split(".")[-1]
                    if st in stem_box:
                        alias[a.asname or st] = stem_box[st]
            elif isinstance(n, ast.ImportFrom):
                mod = (n.module or "").split(".")[-1]
                for a in n.names:
                    if a.name in stem_box:
                        alias[a.asname or a.name] = stem_box[a.name]
                    elif mod in stem_box:
                        names[a.asname or a.name] = (stem_box[mod], a.name.upper())
        nodes.append((bid, _shape(f.stem, tree), f.stem.replace("_", " "), rel(f)))
        funcs = [x for x in tree.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for cls in [x for x in tree.body if isinstance(x, ast.ClassDef)]:
            funcs += [x for x in cls.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and not x.name.startswith("__")]
        for fn in funcs:
            if fn.name.startswith("_"):
                continue
            calls = []
            for c in ast.walk(fn):
                if not isinstance(c, ast.Call):
                    continue
                if isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) and c.func.value.id in alias:
                    calls.append((alias[c.func.value.id], c.func.attr.upper()))
                elif isinstance(c.func, ast.Name) and c.func.id in names:
                    calls.append(names[c.func.id])
            calls = [c for c in dict.fromkeys(calls) if c[0] != bid]
            arrows |= {(bid, c[0]) for c in calls}
            args = ", ".join(a.arg for a in fn.args.args if a.arg not in ("self", "cls"))
            procs.append((f"{bid}.{fn.name.upper()}", args, calls))
    nt = ["| ID | shape | label | file |", "|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in nodes]
    (ctx.dir / "nodes.md").write_text(f"# {ctx.slug}\n\n## ADDED\n" + "\n".join(nt) + "\n")
    blocks = [f"# {ctx.slug}\n\n## ADDED\n"]
    for name, args, calls in procs:
        body = [f"procedure {name}({args})"]
        if calls:
            body.append("  // calls: " + ", ".join(f"{b}.{m}" for b, m in calls))
        body += ["  // TODO: describe body as is, tag each line", "end procedure"]
        blocks.append(f"### {name}\n```pascal pseudo\n" + "\n".join(body) + "\n```\n")
    (ctx.dir / "pseudo.md").write_text("\n".join(blocks))
    cache("boxmap.gen.json").write_text(json.dumps({a: d for a, _, _, d in nodes}, indent=1))
    big = " (>9: pick an entry point and hop count)" if len(nodes) > 9 else ""
    return f"extracted {len(nodes)} boxes{big}, {len(procs)} procedures, {len(arrows)} arrows → {rel(ctx.dir)}/nodes.md, pseudo.md"
