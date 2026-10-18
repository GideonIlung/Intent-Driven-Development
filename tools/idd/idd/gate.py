"""Run tests (story or full), trim failures, and the combined Ralph check."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from .common import ROOT, Ctx, cache, config

FAIL_RE = re.compile(r"(FAILED|ERROR|Error|Traceback|AssertionError|^E\s)")


def story_cmd(ctx: Ctx, s: dict) -> str:
    g = config()["gate"]
    if s["kind"] == "skeleton":
        files = " ".join(f for f in _files(ctx, s) if f.endswith(".py")) or "."
        return g["skeleton"].format(files=files)
    if s["kind"] == "remove" or not s["tags"]:
        return g["full"]
    return g["story"].format(markers=" or ".join(s["tags"]))


def _files(ctx: Ctx, s: dict) -> list[str]:
    from .check import fence_files
    return fence_files(ctx, s)


def trim(out: str, head: int = 40, tail: int = 30) -> str:
    lines = out.splitlines()
    first = next((i for i, l in enumerate(lines) if FAIL_RE.search(l)), None)
    keep = lines[first:first + head] if first is not None else []
    rest = [l for l in lines[-tail:] if l not in keep]
    return "\n".join(keep + (["..."] if keep and rest else []) + rest)


def project_env() -> dict:
    """Environment for YOUR tests: drop the harness venv so your own python/pytest is used."""
    env = dict(os.environ)
    venvs = {str(Path(sys.prefix)), env.pop("VIRTUAL_ENV", "")} - {""}
    keep = [p for p in env.get("PATH", "").split(os.pathsep) if not any(p.startswith(v) for v in venvs)]
    env["PATH"] = os.pathsep.join(keep)
    for k in ("UV_PROJECT", "UV_PROJECT_ENVIRONMENT", "PYTHONHOME"):
        env.pop(k, None)
    return env


def run(cmd: str) -> tuple[int, str]:
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, env=project_env())
    return p.returncode, p.stdout + p.stderr


def gate(ctx: Ctx, s: dict | None, full: bool = False) -> tuple[bool, str]:
    g = config()["gate"]
    cmds = [g["full"]] if full or s is None else [story_cmd(ctx, s)]
    if g.get("lint"):
        cmds.append(g["lint"])
    log = []
    for c in cmds:
        code, out = run(c)
        log.append(f"$ {c}\n{out}")
        if code != 0:
            t = trim(out)
            name = s["id"] if s else "full"
            cache("errors", f"{ctx.slug}-{name}.txt").write_text(f"$ {c}  (exit {code})\n{t}\n")
            return False, f"$ {c}  (exit {code})\n{t}"
    return True, "\n".join(log)
