"""
Final Manifest Builder - Refactored to use database-centric architecture
Builds final manifest from database data without file dependencies.
"""

import json
from typing import Dict, List, Any, Optional

try:
    from .business_logic_layer import AudiobookService
    from .data_access_layer import repository_factory
except ImportError:
    from business_logic_layer import AudiobookService
    from data_access_layer import repository_factory

class ManifestBuilder:
    """Manifest builder using the new architecture."""
    
    def __init__(self):
        self.audiobook_service = AudiobookService(repository_factory)
    
    def build_final_manifest(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Build final manifest from database data."""
        try:
            # Get complete audiobook information
            audiobook_info = self.audiobook_service.get_audiobook_info(book_id)
            if not audiobook_info:
                print(f"Book {book_id} not found in database")
                return None
            
            book = audiobook_info['book']
            chapters = audiobook_info['chapters']
            processing_status = audiobook_info['processing_status']
            
            # Build final chapters list
            final_chapters = []
            for chapter in chapters:
                chapter_data = {
                    "index": chapter.get("chapter_index", 0),
                    "title": chapter["title"],
                    "start_page": chapter["start_page"],
                    "end_page": chapter["end_page"],
                    "has_summary": bool(chapter.get("summary_text")),
                    "has_audio": bool(chapter.get("audio_data")),
                    "processing_status": chapter.get("processing_status", "pending")
                }
                final_chapters.append(chapter_data)
            
            # Build final manifest
            manifest = {
                "book_id": book_id,
                "title": book.get("title", ""),
                "author": book.get("author", ""),
                "genre": book.get("genre", ""),
                "year": book.get("year", ""),
                "page_count": book.get("page_count", 0),
                "has_cover": bool(book.get("cover_image_data")),
                "chapters": final_chapters,
                "processing_status": processing_status,
                "created_at": book.get("created_at"),
                "updated_at": book.get("updated_at")
            }
            
            return manifest
            
        except Exception as e:
            print(f"Error building manifest: {e}")
            return None
    
    def get_processing_summary(self, book_id: str) -> Dict[str, Any]:
        """Get processing summary for a book."""
        try:
            audiobook_info = self.audiobook_service.get_audiobook_info(book_id)
            if not audiobook_info:
                return {"error": "Book not found"}
            
            book = audiobook_info['book']
            chapters = audiobook_info['chapters']
            processing_status = audiobook_info['processing_status']
            
            # Count processing status
            total_chapters = len(chapters)
            completed = sum(1 for ch in chapters if ch.get('processing_status') == 'completed')
            summarized = sum(1 for ch in chapters if ch.get('processing_status') == 'summarized')
            pending = total_chapters - completed - summarized
            
            return {
                "book_id": book_id,
                "title": book.get("title", ""),
                "total_chapters": total_chapters,
                "completed_chapters": completed,
                "summarized_chapters": summarized,
                "pending_chapters": pending,
                "overall_status": processing_status.get('overall_status', 'pending'),
                "completion_percentage": (completed / total_chapters * 100) if total_chapters > 0 else 0
            }
            
        except Exception as e:
            return {"error": f"Failed to get processing summary: {e}"}
    
    def export_audiobook_data(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Export complete audiobook data for backup or transfer."""
        try:
            audiobook_info = self.audiobook_service.get_audiobook_info(book_id)
            if not audiobook_info:
                return None
            
            book = audiobook_info['book']
            chapters = audiobook_info['chapters']
            
            # Prepare export data (exclude large binary data for JSON export)
            export_data = {
                "book": {
                    "book_id": book["book_id"],
                    "title": book["title"],
                    "author": book["author"],
                    "genre": book["genre"],
                    "year": book["year"],
                    "page_count": book["page_count"],
                    "has_cover": bool(book.get("cover_image_data")),
                    "created_at": book["created_at"],
                    "updated_at": book["updated_at"]
                },
                "chapters": []
            }
            
            for chapter in chapters:
                chapter_data = {
                    "chapter_index": chapter["chapter_index"],
                    "title": chapter["title"],
                    "start_page": chapter["start_page"],
                    "end_page": chapter["end_page"],
                    "summary_text": chapter.get("summary_text", ""),
                    "has_audio": bool(chapter.get("audio_data")),
                    "processing_status": chapter.get("processing_status", "pending"),
                    "created_at": chapter["created_at"],
                    "updated_at": chapter["updated_at"]
                }
                export_data["chapters"].append(chapter_data)
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting audiobook data: {e}")
            return None

def main():
    """Command line interface for manifest building."""
    import argparse
    parser = argparse.ArgumentParser(description="Build final manifest for audiobook")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    parser.add_argument("--export", action="store_true", help="Export audiobook data to JSON")
    args = parser.parse_args()
    
    builder = ManifestBuilder()
    
    if args.export:
        # Export audiobook data
        export_data = builder.export_audiobook_data(args.book_id)
        if export_data:
            output_file = f"audiobook_export_{args.book_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"Exported audiobook data to {output_file}")
        else:
            print("Failed to export audiobook data")
    else:
        # Build final manifest
        manifest = builder.build_final_manifest(args.book_id)
        if manifest:
            print(f"Final manifest for book {args.book_id}:")
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
            
            # Show processing summary
            summary = builder.get_processing_summary(args.book_id)
            print(f"\nProcessing Summary:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print(f"Failed to build manifest for book {args.book_id}")

if __name__ == "__main__":
    main()
