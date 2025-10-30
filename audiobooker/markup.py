import os, re
from typing import List, Tuple, Optional
from .paths import out_paths_for_pdf
from .pdf_reader import PdfReader  # reuse class

def load_markup(pdf_path: str) -> Optional[List[Tuple[int, int, str]]]:
    mp = out_paths_for_pdf(pdf_path)["chapters_txt"]
    if not os.path.exists(mp):
        return None
    chapters = []
    with open(mp, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*\|\s*(.+?)\s*$", line)
            if not m:
                raise ValueError(f"Bad markup at line {lineno}: {line}")
            s, e, title = int(m.group(1)), int(m.group(2)), m.group(3)
            if s > e:
                raise ValueError(f"Bad range at line {lineno}: {line}")
            chapters.append((s, e, title))
    return chapters or None

def save_markup_draft(pdf_path: str, draft: List[Tuple[int, int, str]]) -> str:
    mp = out_paths_for_pdf(pdf_path)["chapters_txt"]
    with open(mp, "w", encoding="utf-8") as f:
        f.write("# Format: START-END|Title\n")
        for (s, e, title) in draft:
            f.write(f"{s}-{e}|{title}\n")
    return mp

def make_markup_draft(pdf_path: str):
    reader = PdfReader(pdf_path)
    heading_rx = re.compile(r"(?i)\b(chapter|глава|розділ|section)\b\s*\d*")
    starts = []
    for i, page in enumerate(reader.pages, 1):
        txt = (page.extract_text() or "")[:1000]
        if heading_rx.search(txt):
            head = txt.split("\n", 1)[0].strip()
            starts.append((i, head))
    if not starts:
        return [(1, len(reader.pages), "Book")]
    draft = []
    for idx, (start_pg, headline) in enumerate(starts):
        end_pg = (starts[idx + 1][0] - 1) if idx + 1 < len(starts) else len(reader.pages)
        draft.append((start_pg, end_pg, headline or f"Chapter {idx+1}"))
    return draft
