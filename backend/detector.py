"""
detector.py
Functions for TOC validation, fuzzy matching, and heuristic fallback for chapter detection.
"""
import difflib
import json
from pathlib import Path

def validate_toc(manifest_path, pages_path):
    """
    Compare TOC page numbers vs extracted page count, fuzzy match titles, adjust offset if needed.
    """
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    with open(pages_path, encoding="utf-8") as f:
        pages = json.load(f)
    toc = manifest.get("chapters", [])
    page_count = len(pages)
    # Fuzzy match titles
    for ch in toc:
        title = ch.get("title", "")
        matches = [p["text"] for p in pages if difflib.SequenceMatcher(None, title, p["text"]).ratio() > 0.6]
        ch["fuzzy_matches"] = matches[:2]
    # Offset logic placeholder
    # ...
    return toc

def heuristic_fallback(pages_path):
    """
    Detect headings if TOC missing, build chapters list.
    """
    with open(pages_path, encoding="utf-8") as f:
        pages = json.load(f)
    chapters = []
    for i, p in enumerate(pages):
        text = p.get("text", "")
        if text.strip().startswith("Chapter") or text.isupper():
            chapters.append({"index": len(chapters)+1, "title": text.splitlines()[0], "start_page": i+1})
    return chapters
