"""
Text-to-Speech Engine - Refactored to use database-centric architecture
Generates audio from chapter summaries and stores them in the database.
No more file-based storage - everything goes to database.
"""

import os
import sys
import io
import pyttsx3
from typing import Optional

try:
    from .business_logic_layer import AudiobookService
    from .data_access_layer import repository_factory
except ImportError:
    from business_logic_layer import AudiobookService
    from data_access_layer import repository_factory

class TTSEngine:
    """Text-to-Speech engine using the new architecture."""
    
    def __init__(self):
        self.audiobook_service = AudiobookService(repository_factory)
        self.engine = None
    
    def _initialize_engine(self, voice: str = 'female'):
        """Initialize the TTS engine with specified voice."""
        # Always create a fresh engine instance to avoid hangs across chapters on Windows
        self.engine = pyttsx3.init()
        
        # Set voice
        voices = self.engine.getProperty('voices')
        if voice == 'female':
            for v in voices:
                if 'female' in getattr(v, 'name', '').lower():
                    self.engine.setProperty('voice', v.id)
                    break
        else:
            if voices:
                self.engine.setProperty('voice', voices[0].id)
        
        # Set slower speech rate for better audiobook experience
        self.engine.setProperty('rate', 150)  # 150 words per minute
    
    def generate_audio_data(self, text: str, voice: str = 'female') -> Optional[bytes]:
        """Generate audio data from text and return as bytes."""
        try:
            self._initialize_engine(voice)
            
            # Create a temporary file-like object to capture audio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate audio to temporary file
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            # Read the generated audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return audio_data
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
        finally:
            # Ensure engine resources are released after each generation
            try:
                if self.engine:
                    self.engine.stop()
            except Exception:
                pass
            self.engine = None
    
    def process_book_chapters(self, book_id: str, max_chapters: int = None) -> bool:
        """Process all chapters for a book and generate audio."""
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
            print(f"Generating audio for {len(chapters_to_process)} chapters...")
            
            # Process each chapter
            for i, chapter in enumerate(chapters_to_process):
                try:
                    print(f"Generating audio for chapter {i+1}/{len(chapters_to_process)}: {chapter['title']}")
                    
                    # Get summary text from database
                    summary_text = chapter.get('summary_text', '')
                    
                    if not summary_text.strip():
                        print(f"Warning: No summary text found for chapter {chapter['title']}")
                        summary_text = f"Chapter {chapter['title']} - No summary available"
                    
                    # Generate audio data
                    audio_data = self.generate_audio_data(summary_text, voice='female')
                    
                    if audio_data:
                        # Update chapter with audio data in database
                        success = self.audiobook_service.chapter_service.update_chapter_audio(
                            book_id, chapter['chapter_index'], audio_data, 'audio/wav'
                        )
                        
                        if success:
                            print(f"Audio saved for chapter {chapter['title']}")
                        else:
                            print(f"Failed to save audio for chapter {chapter['title']}")
                    else:
                        print(f"Failed to generate audio for chapter {chapter['title']}")
                        
                except Exception as e:
                    print(f"Error processing chapter {chapter['title']}: {e}")
            
            print(f"Completed generating audio for {len(chapters_to_process)} chapters")
            return True
            
        except Exception as e:
            print(f"Audio generation failed: {e}")
            return False
    
    def get_chapter_audio(self, book_id: str, chapter_index: int) -> Optional[bytes]:
        """Get audio data for a specific chapter."""
        return self.audiobook_service.chapter_service.get_chapter_audio(book_id, chapter_index)[0]
    
    def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine:
            self.engine.stop()
            self.engine = None

def main():
    """Command line interface for TTS generation."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate audio for chapters")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    parser.add_argument("--max_chapters", type=int, default=None, help="Max chapters to process (None for all)")
    args = parser.parse_args()
    
    tts_engine = TTSEngine()
    try:
        success = tts_engine.process_book_chapters(args.book_id, args.max_chapters)
        
        if success:
            print(f"Successfully generated audio for book {args.book_id}")
        else:
            print(f"Failed to generate audio for book {args.book_id}")
    finally:
        tts_engine.cleanup()

if __name__ == "__main__":
    main()
