"""
manifest_final.py
Combines all outputs into a final manifest for the audiobook MVP.
Now uses SQLite database as primary source.
"""
import json
from pathlib import Path
try:
    from .database import db
except ImportError:
    from database import db

def build_final_manifest(book_id):
    # Get book and chapters from database
    book = db.get_book(book_id)
    chapters = db.get_book_chapters(book_id)
    
    if not book:
        print(f"Book {book_id} not found in database")
        return
    
    final_chapters = []
    for ch in chapters:
        ch_num = ch["start_page"]
        summary_path = ch.get("summary_path", f"chapters/chapter_{ch_num:03d}.json")
        audio_path = ch.get("audio_path", f"audio/chapter_{ch_num:03d}.wav")
        
        # Check if files exist
        base_dir = Path(__file__).parent.parent / f"data/books/{book_id}"
        summary_file = base_dir / summary_path
        audio_file = base_dir / audio_path
        
        final_chapters.append({
            "index": ch.get("chapter_index", ch_num),
            "title": ch["title"],
            "start_page": ch["start_page"],
            "end_page": ch["end_page"],
            "summary_path": summary_path if summary_file.exists() else None,
            "audio_path": audio_path if audio_file.exists() else None
        })
    
    manifest_obj = {
        "book_id": book_id,
        "title": book.get("title", ""),
        "author": book.get("author", ""),
        "page_count": book.get("page_count", 0),
        "chapters": final_chapters
    }
    
    # Save to JSON file for backward compatibility
    base_dir = Path(__file__).parent.parent / f"data/books/{book_id}"
    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = base_dir / "manifest_final.json"
    out_path.write_text(json.dumps(manifest_obj, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved final manifest to {out_path}")
    print(f"Book has {len(final_chapters)} chapters with {sum(1 for ch in final_chapters if ch['audio_path'])} audio files")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build final manifest for audiobook")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    args = parser.parse_args()
    build_final_manifest(args.book_id)
