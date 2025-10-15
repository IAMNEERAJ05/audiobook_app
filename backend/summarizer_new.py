"""
Chapter Summarizer - Refactored to use database-centric architecture
Generates summaries for chapters using AI and stores them in the database.
No more file-based storage - everything goes to database.
"""

import os
import sys
import json
from dotenv import load_dotenv
import google.generativeai as genai

try:
    from .business_logic_layer import AudiobookService
    from .data_access_layer import repository_factory
except ImportError:
    from business_logic_layer import AudiobookService
    from data_access_layer import repository_factory

class ChapterSummarizer:
    """Chapter summarization service using the new architecture."""
    
    def __init__(self):
        self.audiobook_service = AudiobookService(repository_factory)
    
    def summarize_chapter(self, chapter: dict, chapter_text: str, model) -> dict:
        """Summarize a single chapter using AI."""
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
        prompt += chapter_text[:12000]  # Limit text length for API
        
        try:
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
                    summary_json = {
                        "chapter_title": chapter['title'], 
                        "summary": raw.strip(), 
                        "tone": "unknown"
                    }
            return summary_json
            
        except Exception as e:
            print(f"Error summarizing chapter {chapter['title']}: {e}")
            return {
                "chapter_title": chapter['title'],
                "summary": f"Error generating summary for {chapter['title']}",
                "tone": "unknown"
            }
    
    def process_book_chapters(self, book_id: str, max_chapters: int = None) -> bool:
        """Process all chapters for a book."""
        try:
            # Get book information
            book = self.audiobook_service.book_service.get_book(book_id)
            if not book:
                print(f"Book {book_id} not found")
                return False
            
            # Get chapters
            chapters = self.audiobook_service.chapter_service.get_chapters(book_id)
            if not chapters:
                print(f"No chapters found for book {book_id}")
                return False
            
            # Limit chapters if specified
            chapters_to_process = chapters if max_chapters is None else chapters[:max_chapters]
            print(f"Processing {len(chapters_to_process)} chapters for book {book_id}")
            
            # Initialize AI model
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("Warning: GOOGLE_API_KEY missing from environment")
                return self._create_default_summaries(book_id, chapters_to_process)
            
            genai.configure(api_key=api_key)
            model_name = "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name)
            
            # Process each chapter
            for i, chapter in enumerate(chapters_to_process):
                try:
                    print(f"Summarizing chapter {i+1}/{len(chapters_to_process)}: {chapter['title']}")
                    
                    # Get chapter text from database
                    chapter_text = self.audiobook_service.chapter_service.get_chapter_text(
                        book_id, chapter['start_page'], chapter['end_page']
                    )
                    
                    if not chapter_text.strip():
                        print(f"Warning: No text found for chapter {chapter['title']}")
                        summary_text = f"No content available for {chapter['title']}"
                    else:
                        # Generate summary using AI
                        summary_data = self.summarize_chapter(chapter, chapter_text, model)
                        summary_text = summary_data.get('summary', f"No summary generated for {chapter['title']}")
                    
                    # Update chapter with summary in database
                    success = self.audiobook_service.chapter_service.update_chapter_summary(
                        book_id, chapter['chapter_index'], summary_text
                    )
                    
                    if success:
                        print(f"Summary saved for chapter {chapter['title']}")
                    else:
                        print(f"Failed to save summary for chapter {chapter['title']}")
                        
                except Exception as e:
                    print(f"Error processing chapter {chapter['title']}: {e}")
                    # Create fallback summary
                    fallback_summary = f"Chapter {chapter['title']} - Summary generation failed"
                    self.audiobook_service.chapter_service.update_chapter_summary(
                        book_id, chapter['chapter_index'], fallback_summary
                    )
            
            print(f"Completed summarizing {len(chapters_to_process)} chapters")
            return True
            
        except Exception as e:
            print(f"Chapter summarization failed: {e}")
            return False
    
    def _create_default_summaries(self, book_id: str, chapters: list) -> bool:
        """Create default summaries when AI is not available."""
        try:
            for chapter in chapters:
                default_summary = f"Chapter {chapter['title']} - Summary not available (AI service unavailable)"
                self.audiobook_service.chapter_service.update_chapter_summary(
                    book_id, chapter['chapter_index'], default_summary
                )
            print("Created default summaries (AI service unavailable)")
            return True
        except Exception as e:
            print(f"Failed to create default summaries: {e}")
            return False

def main():
    """Command line interface for chapter summarization."""
    import argparse
    parser = argparse.ArgumentParser(description="Summarize chapters for audiobook")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    parser.add_argument("--max_chapters", type=int, default=None, help="Max chapters to summarize (None for all)")
    args = parser.parse_args()
    
    summarizer = ChapterSummarizer()
    success = summarizer.process_book_chapters(args.book_id, args.max_chapters)
    
    if success:
        print(f"Successfully summarized chapters for book {args.book_id}")
    else:
        print(f"Failed to summarize chapters for book {args.book_id}")

if __name__ == "__main__":
    main()
