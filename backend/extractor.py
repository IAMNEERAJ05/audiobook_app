# extractor.py
# Extracts pages and text from PDF books
"""
PDF Extractor for Audiobook Generator MVP
Loads a PDF, extracts per-page text, removes repeated headers/footers, saves to SQLite database
"""
import fitz  # PyMuPDF
import os
import json
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv
import google.generativeai as genai
try:
    from .database import db
except ImportError:
    from database import db

def extract_pages(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    header_counts = Counter()
    footer_counts = Counter()
    # First pass: collect headers/footers
    for i in range(doc.page_count):
        page = doc.load_page(i)
        try:
            lines = page.get_text("text").splitlines()
        except Exception:
            lines = page.getText().splitlines() if hasattr(page, 'getText') else []
        if len(lines) > 2:
            header_counts[lines[0].strip()] += 1
            footer_counts[lines[-1].strip()] += 1
    # Detect most common header/footer
    header = header_counts.most_common(1)[0][0] if header_counts else None
    footer = footer_counts.most_common(1)[0][0] if footer_counts else None
    # Second pass: extract text, remove header/footer
    for i in range(doc.page_count):
        page = doc.load_page(i)
        try:
            lines = page.get_text("text").splitlines()
        except Exception:
            lines = page.getText().splitlines() if hasattr(page, 'getText') else []
        # Remove header/footer if detected
        if header and lines and lines[0].strip() == header:
            lines = lines[1:]
        if footer and lines and lines[-1].strip() == footer:
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        pages.append({"page_number": i+1, "text": text})
    return pages

def extract_cover_image(pdf_path, book_id):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    try:
        pix = page.get_pixmap()
    except Exception:
        pix = page.getPixmap() if hasattr(page, 'getPixmap') else None
    if pix is None:
        print("Error: Could not extract cover image from PDF.")
        return
    out_dir = Path(f"data/books/{book_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    cover_path = out_dir / "cover.png"
    pix.save(str(cover_path))
    print(f"Saved cover image to {cover_path}")

def save_pages(pages, book_id):
    # Save pages to database
    db.add_pages(book_id, pages)
    print(f"Saved {len(pages)} pages to database for book {book_id}")
    
    # Also save to JSON for backward compatibility
    out_dir = Path(f"data/books/{book_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "pages.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)
    print(f"Also saved {len(pages)} pages to {out_path}")

def extract_metadata(pages, book_id):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY missing from .env")
    
    # Try to configure Gemini API (fallback to previous logic)
    try:
        genai.configure(api_key=api_key)
        model_name = "gemini-2.5-flash"
        model = genai.GenerativeModel(model_name)
        
        # Use more pages for better chapter detection (first 50 pages instead of 20)
        front_text = "\n\n".join(f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages[:50])
        prompt = f"""
You are analyzing a general narrative book to extract metadata and chapter information.
From the following front pages (title, copyright, table of contents, introduction):

{front_text}

Return a JSON object:
{{
  "title": "...",
  "author": "...",
  "genre": "...",
  "year": "...",
  "chapters": [
    {{"title": "Chapter 1", "start_page": 1, "end_page": 9}},
    {{"title": "Chapter 2", "start_page": 10, "end_page": 18}},
    ...
  ]
}}

IMPORTANT: 
- Look for table of contents, chapter headings, or section breaks
- If no clear chapters found, create logical chapters every 8-15 pages
- Try to identify chapter titles from headings or TOC
- Return at least 5-10 chapters if possible
- If you cannot find TOC, estimate chapters based on content breaks

Return only valid JSON.
"""
        response = model.generate_content(prompt)
        raw_output = response.text
        
        # Save raw Gemini output
        out_dir = Path(f"data/books/{book_id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "meta_raw.json").write_text(raw_output, encoding="utf-8")
        
        # Try to parse JSON
        import re
        try:
            meta_json = json.loads(raw_output)
        except Exception:
            m = re.search(r"(\{.*\})", raw_output, flags=re.S)
            if m:
                meta_json = json.loads(m.group(1))
            else:
                meta_json = {"error": "Could not parse Gemini output", "raw": raw_output}
        
        # Save to database
        title = meta_json.get("title", "Unknown Title")
        author = meta_json.get("author", "Unknown Author")
        genre = meta_json.get("genre", "Unknown Genre")
        year = meta_json.get("year", "Unknown Year")
        
        db.add_book(book_id, title, author, genre, year, len(pages))
        
        chapters = meta_json.get("chapters", [])
        if chapters:
            db.add_chapters(book_id, chapters)
            print(f"Saved {len(chapters)} chapters to database")
        else:
            print("No chapters found, creating default chapters")
            # Create default chapters if none found
            default_chapters = []
            pages_per_chapter = max(10, len(pages) // 10)  # At least 10 pages per chapter
            for i in range(0, len(pages), pages_per_chapter):
                start_page = i + 1
                end_page = min(i + pages_per_chapter, len(pages))
                default_chapters.append({
                    "title": f"Chapter {len(default_chapters) + 1}",
                    "start_page": start_page,
                    "end_page": end_page
                })
            db.add_chapters(book_id, default_chapters)
            print(f"Created {len(default_chapters)} default chapters")
        
        # Also save to JSON for backward compatibility
        (out_dir / "manifest.json").write_text(json.dumps(meta_json, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Saved metadata to database and JSON manifest.")
        
    except Exception as e:
        print(f"[ERROR] Gemini extraction failed: {e}")
        
        # Create minimal book entry in database
        db.add_book(book_id, "Unknown Title", "Unknown Author", "Unknown Genre", "Unknown Year", len(pages))
        
        # Create default chapters
        default_chapters = []
        pages_per_chapter = max(10, len(pages) // 10)
        for i in range(0, len(pages), pages_per_chapter):
            start_page = i + 1
            end_page = min(i + pages_per_chapter, len(pages))
            default_chapters.append({
                "title": f"Chapter {len(default_chapters) + 1}",
                "start_page": start_page,
                "end_page": end_page
            })
        db.add_chapters(book_id, default_chapters)
        
        # Write minimal manifest.json so downstream scripts do not fail
        out_dir = Path(f"data/books/{book_id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        minimal_manifest = {
            "title": "Unknown Title",
            "author": "Unknown Author",
            "genre": "Unknown Genre",
            "year": "Unknown Year",
            "chapters": default_chapters
        }
        (out_dir / "manifest.json").write_text(json.dumps(minimal_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[INFO] Created {len(default_chapters)} default chapters in database and JSON.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract pages and metadata from PDF")
    parser.add_argument("--pdf_path", type=str, required=True, help="Path to PDF file")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    args = parser.parse_args()
    pdf_path = args.pdf_path
    book_id = args.book_id
    extract_cover_image(pdf_path, book_id)
    pages = extract_pages(pdf_path)
    save_pages(pages, book_id)
    print(f"Extracted {len(pages)} pages from {pdf_path}")
    extract_metadata(pages, book_id)

if __name__ == "__main__":
    main()