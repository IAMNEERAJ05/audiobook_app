"""
tts_engine.py
Generates audio from chapter summaries using pyttsx3 (offline TTS).
Reads from SQLite database, saves output as .wav files in data/books/{book_id}/audio/.
"""
import os
import sys
import json
from pathlib import Path
import pyttsx3

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
try:
    from .database import db
except ImportError:
    from database import db

def generate_audio(summary_text, output_path, voice='female'):
    engine = pyttsx3.init()
    # Set voice
    voices = engine.getProperty('voices')
    if voice == 'female':
        for v in voices:
            if 'female' in v.name.lower():
                engine.setProperty('voice', v.id)
                break
    else:
        engine.setProperty('voice', voices[0].id)
    # Set slower speech rate
    engine.setProperty('rate', 150)  # 150 words per minute is a natural pace
    engine.save_to_file(summary_text, str(output_path))
    engine.runAndWait()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate audio for chapters")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    parser.add_argument("--max_chapters", type=int, default=None, help="Max chapters to process (None for all)")
    args = parser.parse_args()
    book_id = args.book_id
    max_chapters = args.max_chapters
    
    # Get chapters from database
    chapters = db.get_book_chapters(book_id)
    if not chapters:
        print(f"No chapters found for book {book_id}")
        return
    
    # Create audio directory
    audio_dir = Path(f"data/books/{book_id}/audio")
    audio_dir.mkdir(exist_ok=True)
    
    chapters_to_process = chapters if max_chapters is None else chapters[:max_chapters]
    print(f"Generating audio for {len(chapters_to_process)} chapters...")
    
    # Iterate through chapters
    for i, chapter in enumerate(chapters_to_process):
        chapter_index = chapter['chapter_index']
        chapter_title = chapter['title']
        summary_text = chapter.get('summary_text', '')
        
        # Handle Unicode characters safely for Windows console
        try:
            print(f"Generating audio for chapter {i+1}/{len(chapters_to_process)}: {chapter_title}")
        except UnicodeEncodeError:
            # Fallback: encode to ASCII with replacement characters
            safe_title = chapter_title.encode('ascii', 'replace').decode('ascii')
            print(f"Generating audio for chapter {i+1}/{len(chapters_to_process)}: {safe_title}")
        
        if not summary_text.strip():
            try:
                print(f"Warning: No summary text found for chapter {chapter_title}")
            except UnicodeEncodeError:
                safe_title = chapter_title.encode('ascii', 'replace').decode('ascii')
                print(f"Warning: No summary text found for chapter {safe_title}")
            summary_text = f"Chapter {chapter_title} - No summary available"
        
        # Generate audio file
        audio_filename = f"chapter_{chapter['start_page']:03d}.wav"
        audio_path = audio_dir / audio_filename
        
        try:
            generate_audio(summary_text, audio_path, voice='female')
            
            # Update database with audio path
            db.update_chapter_audio(book_id, chapter_index, f"audio/{audio_filename}")
            
            print(f"Saved audio to {audio_path}")
        except Exception as e:
            try:
                print(f"Error generating audio for chapter {chapter_title}: {e}")
            except UnicodeEncodeError:
                safe_title = chapter_title.encode('ascii', 'replace').decode('ascii')
                print(f"Error generating audio for chapter {safe_title}: {e}")
    
    print(f"Completed generating audio for {len(chapters_to_process)} chapters")

if __name__ == "__main__":
    main()
