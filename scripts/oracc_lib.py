"""Shared helpers for reading the Oracc aemw/amarna corpus JSON."""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "raw" / "aemw" / "amarna"
DERIVED = ROOT / "data" / "derived"


def load_catalogue():
    return json.loads((CORPUS / "catalogue.json").read_text())


def corpus_files():
    return {p.stem: p for p in (CORPUS / "corpusjson").glob("P*.json")}


def parse_ea(designation: str):
    m = re.match(r"EA ([0-9]+)([a-z]?)", designation)
    return (int(m.group(1)), m.group(2)) if m else None


def words(pid_or_path):
    """Flat list of word ('l') nodes for one text, in document order."""
    path = pid_or_path if isinstance(pid_or_path, Path) else (
        CORPUS / "corpusjson" / f"{pid_or_path}.json"
    )
    data = json.loads(path.read_text())
    out = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("node") == "l":
                out.append(node)
            for child in node.get("cdl", []):
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(data.get("cdl", []))
    return out


def fold(s: str) -> str:
    """Aggressive normalization for cross-source name matching:
    strip diacritics, aleph/ayin, subscripts, case, non-letters."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower()
    s = s.replace("ʾ", "").replace("ʿ", "")  # ʾ ʿ
    return re.sub(r"[^a-z]", "", s)
