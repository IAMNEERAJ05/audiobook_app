"""
summarizer.py
Generates summaries for chapters using Gemini Flash 2.1 (free tier).
Reads from SQLite database, summarizes each chapter, and saves results.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
try:
    from .database import db
except ImportError:
    from database import db

def get_chapter_text_from_db(book_id, start_page, end_page):
    """Get chapter text from database pages."""
    pages = db.get_chapter_pages(book_id, start_page, end_page)
    return "\n\n".join(p["text_content"] for p in pages if p.get("text_content"))

def summarize_chapter(chapter, chapter_text, model):
    prompt = f"""
You are a narrator. Summarize the chapter '{chapter['title']}'
in a descriptive, emotional style suitable for audiobook narration.
Keep it 150–220 words.
Return only JSON:
{{
"chapter_title": "{chapter['title']}",
"summary": "...",
"tone": "emotional|calm|dramatic"
}}
Text:
"""
    prompt += chapter_text[:12000]
    response = model.generate_content(prompt)
    raw = response.text
    # Try to parse JSON
    import re
    try:
        summary_json = json.loads(raw)
    except Exception:
        m = re.search(r"(\{.*\})", raw, flags=re.S)
        if m:
            summary_json = json.loads(m.group(1))
        else:
            summary_json = {"chapter_title": chapter['title'], "summary": raw.strip(), "tone": "unknown"}
    return summary_json

def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY missing from .env")
    genai.configure(api_key=api_key)
    model_name = "gemini-2.5-flash"  # Use current free tier model
    model = genai.GenerativeModel(model_name)

    import argparse
    parser = argparse.ArgumentParser(description="Summarize chapters for audiobook")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    parser.add_argument("--max_chapters", type=int, default=None, help="Max chapters to summarize (None for all)")
    args = parser.parse_args()
    book_id = args.book_id
    max_chapters = args.max_chapters
    
    # Get chapters from database
    chapters = db.get_book_chapters(book_id)
    if not chapters:
        print(f"No chapters found for book {book_id}")
        return
    
    # Create output directory for JSON files (backward compatibility)
    base_dir = Path(f"data/books/{book_id}")
    out_dir = base_dir / "chapters"
    out_dir.mkdir(exist_ok=True)

    chapters_to_process = chapters if max_chapters is None else chapters[:max_chapters]
    print(f"Processing {len(chapters_to_process)} chapters for book {book_id}")
    
    for i, ch in enumerate(chapters_to_process):
        # Handle Unicode characters safely for Windows console
        try:
            print(f"Summarizing chapter {i+1}/{len(chapters_to_process)}: {ch['title']} (pages {ch['start_page']}-{ch['end_page']})")
        except UnicodeEncodeError:
            # Fallback: encode to ASCII with replacement characters
            safe_title = ch['title'].encode('ascii', 'replace').decode('ascii')
            print(f"Summarizing chapter {i+1}/{len(chapters_to_process)}: {safe_title} (pages {ch['start_page']}-{ch['end_page']})")
        
        # Get chapter text from database
        chapter_text = get_chapter_text_from_db(book_id, ch['start_page'], ch['end_page'])
        
        if not chapter_text.strip():
            try:
                print(f"Warning: No text found for chapter {ch['title']}")
            except UnicodeEncodeError:
                safe_title = ch['title'].encode('ascii', 'replace').decode('ascii')
                print(f"Warning: No text found for chapter {safe_title}")
            summary_text = f"No content available for {ch['title']}"
        else:
            summary = summarize_chapter(ch, chapter_text, model)
            summary_text = summary.get('summary', f"No summary generated for {ch['title']}")
        
        # Save to database
        summary_path = f"chapters/chapter_{ch['start_page']:03d}.json"
        db.update_chapter_summary(book_id, ch['chapter_index'], summary_path, summary_text)
        
        # Also save to JSON file for backward compatibility
        summary_data = {
            "chapter_title": ch['title'],
            "summary": summary_text,
            "tone": "emotional|calm|dramatic"
        }
        out_path = out_dir / f"chapter_{ch['start_page']:03d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved summary to database and {out_path}")
    
    print(f"Completed summarizing {len(chapters_to_process)} chapters")

if __name__ == "__main__":
    main()
