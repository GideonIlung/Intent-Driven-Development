"""Shared paths, config, work-folder lookup and change context."""
from __future__ import annotations

import json
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

from . import parse

MODES = {"change": "changes", "review": "reviews", "investigate": "investigations", "spike": "spikes"}
MAIN_FILE = {"change": "intent.md", "review": "report.md", "investigate": "report.md", "spike": "notes.md"}


class IddError(Exception):
    pass


def _root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


ROOT = _root()
CACHE = ROOT / ".idd"

DEFAULTS = {
    "gate": {
        "story": 'python -m pytest -q -W ignore::pytest.PytestUnknownMarkWarning -m "{markers}"',
        "skeleton": "python -m compileall -q {files}",
        "full": "python -m pytest -q -W ignore::pytest.PytestUnknownMarkWarning",
        "lint": "",
    },
    "limits": {"boxes": 9, "scenarios": 6, "proc_lines": 15, "hotfix_boxes": 2, "hotfix_scenarios": 1, "group": 3},
    "conform": {"strict": False},
    "fence": {"always": ["tests/steps/", "tests/conftest.py", "work/"]},
}


def config() -> dict:
    cfg = {k: dict(v) for k, v in DEFAULTS.items()}
    f = ROOT / "idd.toml"
    if f.exists():
        for k, v in tomllib.loads(f.read_text()).items():
            cfg.setdefault(k, {}).update(v)
    return cfg


def cache(*parts: str) -> Path:
    p = CACHE.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def find_work(slug: str | None, mode: str | None = None) -> tuple[Path, str]:
    cands = []
    for m, d in MODES.items():
        if mode and m != mode:
            continue
        base = ROOT / "work" / d
        if base.is_dir():
            cands += [(p, m) for p in sorted(base.iterdir()) if p.is_dir() and (slug is None or p.name == slug)]
    if not cands:
        raise IddError(f"no open work folder{' named ' + slug if slug else ''}")
    if len(cands) > 1:
        raise IddError("several open work folders, pass a slug: " + ", ".join(p.name for p, _ in cands))
    return cands[0]


FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def read_meta(path: Path) -> dict:
    if not path.exists():
        return {}
    m = FM_RE.match(path.read_text())
    meta: dict = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        meta[k.strip()] = v
    return meta


def set_meta(path: Path, **kv) -> None:
    text = path.read_text()
    m = FM_RE.match(text)
    lines = m.group(1).splitlines() if m else []
    body = text[m.end():] if m else text
    for k, v in kv.items():
        val = "[" + ", ".join(v) + "]" if isinstance(v, list) else str(v)
        for i, l in enumerate(lines):
            if l.split(":", 1)[0].strip() == k:
                lines[i] = f"{k}: {val}"
                break
        else:
            lines.append(f"{k}: {val}")
    path.write_text("---\n" + "\n".join(lines) + "\n---\n" + body)


@dataclass
class Ctx:
    slug: str
    dir: Path
    mode: str
    meta: dict
    cap: str
    flags: list[str]
    base: parse.Parsed
    delta: parse.Parsed
    model: parse.Model

    @property
    def main(self) -> Path:
        return self.dir / MAIN_FILE[self.mode]

    @property
    def spec_dir(self) -> Path:
        return ROOT / "specs" / self.cap

    def delta_tags(self) -> set[str]:
        return {s.tag for s in self.delta.scenarios}

    def delta_procs(self) -> list[parse.Proc]:
        return list(self.delta.procs)

    def grown(self) -> set[str]:
        f = CACHE / "slice" / f"{self.slug}.json"
        return set(json.loads(f.read_text())) if f.exists() else set()

    def touched(self) -> set[str]:
        t = {n.id for n in self.delta.nodes} | {p.box for p in self.delta.procs}
        t |= self.delta.removed_nodes | {n.split(".")[0] for n in self.delta.removed_procs}
        if self.main.exists():
            t |= parse.section_ids(self.main.read_text(), "Touched boxes")
        t |= self.grown()
        return t


def load_ctx(slug: str | None = None, mode: str | None = None) -> Ctx:
    d, m = find_work(slug, mode)
    meta = read_meta(d / MAIN_FILE[m])
    cap = meta.get("capability") or d.name.split("-")[0]
    if isinstance(cap, list):
        cap = cap[0]
    flags = meta.get("flags") or []
    flags = [flags] if isinstance(flags, str) else flags
    flags = [f.lstrip("-") for f in flags if f]
    spec = ROOT / "specs" / cap
    base = parse.parse_dir(spec, delta=False) if m in ("change", "investigate") else parse.Parsed()
    delta = parse.parse_dir(d, delta=True)
    return Ctx(d.name, d, m, meta, cap, flags, base, delta, parse.effective(base, delta))


def rel(p: str | Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(p)
