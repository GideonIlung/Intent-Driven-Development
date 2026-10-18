"""Parse scenarios.md, nodes.md and pseudo.md into objects."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

SHAPES = ("entry", "op", "cond", "store", "file")
SEC_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED)\s*$")
TAG_RE = re.compile(r"@([A-Z]{1,3})\b")
SCEN_RE = re.compile(r"^\s*Scenario(?: Outline)?:\s*(.*)$")
STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.*?)\s*(?:\[([A-Z][A-Z0-9_]*)\])?\s*$")
PROC_RE = re.compile(r"^\s*procedure\s+([A-Z][A-Z0-9_]*)\.([A-Z][A-Z0-9_]*)\s*\((.*?)\)")
CALL_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)\.([A-Z][A-Z0-9_]*)\s*\(")
NAME_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)\.([A-Z][A-Z0-9_]*)\b")
ID_RE = re.compile(r"\b([A-Z][A-Z0-9_]+)\b")
OPENER_RE = re.compile(r"^\s*(procedure|if|for|while)\b")
END_RE = re.compile(r"^\s*end\b")
ELSE_RE = re.compile(r"^\s*else\b")


@dataclass
class Step:
    kw: str
    text: str
    box: str | None
    line: int


@dataclass
class Scenario:
    tag: str
    name: str
    steps: list[Step]
    section: str
    file: str
    line: int
    raw: str


@dataclass
class Node:
    id: str
    shape: str
    label: str
    file: str
    section: str
    src: str
    line: int


@dataclass
class PLine:
    line: int
    text: str
    code: str
    tags: set[str]
    calls: list[tuple[str, str]]
    structural: bool


@dataclass
class Proc:
    box: str
    method: str
    params: str
    lines: list[PLine]
    section: str
    file: str
    line: int
    raw: str

    @property
    def name(self) -> str:
        return f"{self.box}.{self.method}"

    @property
    def header(self) -> str:
        return self.lines[0].code.strip() if self.lines else f"procedure {self.name}()"

    def calls(self) -> set[tuple[str, str]]:
        return {c for ln in self.lines for c in ln.calls}

    def tags(self) -> set[str]:
        return {t for ln in self.lines for t in ln.tags}


@dataclass
class Parsed:
    scenarios: list[Scenario] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    procs: list[Proc] = field(default_factory=list)
    removed_tags: set[str] = field(default_factory=set)
    removed_nodes: set[str] = field(default_factory=set)
    removed_procs: set[str] = field(default_factory=set)
    errors: list[tuple[str, int, str]] = field(default_factory=list)


@dataclass
class Model:
    scenarios: dict[str, Scenario] = field(default_factory=dict)
    nodes: dict[str, Node] = field(default_factory=dict)
    procs: dict[str, Proc] = field(default_factory=dict)


def tag_key(t: str) -> tuple[int, str]:
    return (len(t), t)


def next_tag(existing: set[str]) -> str:
    def idx(t: str) -> int:
        n = 0
        for ch in t:
            n = n * 26 + (ord(ch) - 64)
        return n

    def tag(n: int) -> str:
        s = ""
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    top = max((idx(t) for t in existing if t != "X"), default=0)  # @X reserved for investigate
    n = top + 1
    while tag(n) in existing:
        n += 1
    return tag(n)


# ---------- low-level line walk ----------

def _walk(text: str, delta: bool):
    """Yield (lineno, line, section, block) where block is None or (lang, start, lines-list)."""
    section = "ADDED" if delta else "BASE"
    blocks: list[tuple[str, str, int, list[tuple[int, str]]]] = []
    loose: list[tuple[int, str, str]] = []
    fence = None
    cur = None
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if fence is None:
            m = SEC_RE.match(line)
            if m and delta:
                section = m.group(1)
                continue
            fm = re.match(r"^(`{3,}|~{3,})\s*(.*)$", s)
            if fm:
                fence = fm.group(1)
                cur = (fm.group(2).strip().lower(), section, i, [])
                continue
            loose.append((i, line, section))
        else:
            if s and set(s) == {fence[0]} and len(s) >= len(fence):
                blocks.append(cur)
                fence, cur = None, None
                continue
            cur[3].append((i, line))
    if cur:
        blocks.append(cur)
    return blocks, loose


# ---------- scenarios ----------

def parse_scenarios(path: Path, out: Parsed, delta: bool) -> None:
    if not path.exists():
        return
    blocks, loose = _walk(path.read_text(), delta)
    src = str(path)
    for lang, section, start, lines in blocks:
        if section == "REMOVED":
            for _, ln in lines:
                out.removed_tags |= set(TAG_RE.findall(ln))
            continue
        if not lang.startswith("gherkin"):
            continue
        tags: list[str] = []
        cur: Scenario | None = None
        raw: list[str] = []
        for i, ln in lines:
            raw.append(ln)
            if ln.strip().startswith("@"):
                tags += TAG_RE.findall(ln)
                continue
            m = SCEN_RE.match(ln)
            if m:
                if cur:
                    out.scenarios.append(cur)
                if len(tags) != 1:
                    out.errors.append((src, i, f"scenario needs exactly one @tag, found {len(tags) or 'none'}"))
                cur = Scenario(tags[0] if tags else "?", m.group(1).strip(), [], section, src, i, "")
                tags = []
                continue
            m = STEP_RE.match(ln)
            if m and cur:
                cur.steps.append(Step(m.group(1), m.group(2).strip(), m.group(3), i))
        if cur:
            cur.raw = "\n".join(raw).strip("\n")
            out.scenarios.append(cur)
    for _, ln, section in loose:
        if section == "REMOVED":
            out.removed_tags |= set(TAG_RE.findall(ln))


# ---------- nodes ----------

def parse_nodes(path: Path, out: Parsed, delta: bool) -> None:
    if not path.exists():
        return
    _, loose = _walk(path.read_text(), delta)
    src = str(path)
    for i, ln, section in loose:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or cells[0] in ("ID", "") or set(cells[0]) <= set("-: "):
            continue
        if section == "REMOVED":
            out.removed_nodes.add(cells[0])
            continue
        cells += [""] * (4 - len(cells))
        nid, shape, label, f = cells[:4]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", nid):
            out.errors.append((src, i, f"box ID '{nid}' must be UPPERCASE"))
        if shape not in SHAPES:
            out.errors.append((src, i, f"box {nid}: shape '{shape}' not one of {', '.join(SHAPES)}"))
        out.nodes.append(Node(nid, shape, label or nid.lower(), f, section, src, i))


# ---------- pseudo ----------

def _pline(i: int, text: str) -> PLine:
    code, tags = text, set()
    if "//" in text:
        code, comment = text.split("//", 1)
        tags = set(TAG_RE.findall(comment))
    code = code.rstrip()
    st = code.strip()
    structural = st == "" or bool(END_RE.match(code) or ELSE_RE.match(code))
    calls = [] if PROC_RE.match(code) else [(b, m) for b, m in CALL_RE.findall(code)]
    return PLine(i, text, code, tags, calls, structural)


def parse_proc_block(lines: list[tuple[int, str]], section: str, src: str, out: Parsed) -> Proc | None:
    body = [(i, ln) for i, ln in lines if ln.strip()]
    if not body:
        return None
    m = PROC_RE.match(body[0][1])
    if not m:
        out.errors.append((src, body[0][0], "pseudo block must start with: procedure BOX.METHOD(args)"))
        return None
    plines = [_pline(i, ln) for i, ln in body]
    stack: list[set[str]] = []
    for pl in plines:
        if pl.structural and END_RE.match(pl.code):
            if stack:
                pl.tags = set(stack.pop())
            continue
        if pl.structural and ELSE_RE.match(pl.code):
            if stack:
                pl.tags = set(stack[-1])
            continue
        if OPENER_RE.match(pl.code):
            stack.append(pl.tags)
    raw = "\n".join(ln for _, ln in lines).strip("\n")
    return Proc(m.group(1), m.group(2), m.group(3), plines, section, src, body[0][0], raw)


def parse_pseudo(path: Path, out: Parsed, delta: bool) -> None:
    if not path.exists():
        return
    blocks, loose = _walk(path.read_text(), delta)
    src = str(path)
    for lang, section, start, lines in blocks:
        if section == "REMOVED":
            for _, ln in lines:
                m = PROC_RE.match(ln)
                if m:
                    out.removed_procs.add(f"{m.group(1)}.{m.group(2)}")
            continue
        if "pseudo" not in lang:
            continue
        p = parse_proc_block(lines, section, src, out)
        if p:
            out.procs.append(p)
    for _, ln, section in loose:
        if section == "REMOVED":
            out.removed_procs |= {f"{b}.{m}" for b, m in NAME_RE.findall(ln)}


def parse_dir(d: Path, delta: bool) -> Parsed:
    out = Parsed()
    parse_scenarios(d / "scenarios.md", out, delta)
    parse_nodes(d / "nodes.md", out, delta)
    parse_pseudo(d / "pseudo.md", out, delta)
    return out


def effective(base: Parsed, delta: Parsed) -> Model:
    m = Model()
    for s in base.scenarios:
        m.scenarios[s.tag] = s
    for n in base.nodes:
        m.nodes[n.id] = n
    for p in base.procs:
        m.procs[p.name] = p
    for s in delta.scenarios:
        m.scenarios[s.tag] = s
    for n in delta.nodes:
        m.nodes[n.id] = n
    for p in delta.procs:
        m.procs[p.name] = p
    for t in delta.removed_tags:
        m.scenarios.pop(t, None)
    for nid in delta.removed_nodes:
        m.nodes.pop(nid, None)
    for name in delta.removed_procs:
        m.procs.pop(name, None)
    return m


def section_ids(text: str, heading: str) -> set[str]:
    out, on = set(), False
    for ln in text.splitlines():
        if ln.startswith("## "):
            on = ln[3:].strip().lower() == heading.lower()
            continue
        if on:
            out |= set(ID_RE.findall(ln))
    return out


def section_text(text: str, heading: str) -> str:
    out, on = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            on = ln[3:].strip().lower() == heading.lower()
            continue
        if on:
            out.append(ln)
    return "\n".join(out).strip()
