"""
Migration Script - Move existing file-based data to database
This script migrates all existing audiobook data from filesystem to database.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

from .data_access_layer import DatabaseConnection, repository_factory
from .business_logic_layer import AudiobookService

class DataMigrator:
    """Migrates existing file-based data to database."""
    
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.audiobook_service = AudiobookService(repository_factory)
        self.data_dir = Path("data/books")
    
    def migrate_all_books(self) -> bool:
        """Migrate all existing books to database."""
        try:
            if not self.data_dir.exists():
                print("No existing data directory found. Nothing to migrate.")
                return True
            
            book_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
            print(f"Found {len(book_dirs)} book directories to migrate")
            
            for book_dir in book_dirs:
                book_id = book_dir.name
                print(f"Migrating book: {book_id}")
                
                if not self.migrate_single_book(book_id, book_dir):
                    print(f"Failed to migrate book: {book_id}")
                    return False
            
            print("Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Migration failed: {e}")
            return False
    
    def migrate_single_book(self, book_id: str, book_dir: Path) -> bool:
        """Migrate a single book to database."""
        try:
            # Check if book already exists in database
            existing_book = self.audiobook_service.book_service.get_book(book_id)
            if existing_book:
                print(f"Book {book_id} already exists in database, skipping...")
                return True
            
            # Load manifest
            manifest_path = book_dir / "manifest.json"
            if not manifest_path.exists():
                print(f"No manifest found for {book_id}, skipping...")
                return True
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Create book entry
            title = manifest.get('title', book_id)
            author = manifest.get('author', 'Unknown Author')
            genre = manifest.get('genre', 'Unknown Genre')
            year = manifest.get('year', 'Unknown Year')
            
            # Load pages
            pages_path = book_dir / "pages.json"
            pages = []
            if pages_path.exists():
                with open(pages_path, 'r', encoding='utf-8') as f:
                    pages = json.load(f)
            
            # Create book in database
            if not self.audiobook_service.create_audiobook(
                book_id, title, author, genre, year, len(pages)
            ):
                print(f"Failed to create book {book_id} in database")
                return False
            
            # Add pages to database
            if pages:
                if not self.audiobook_service.add_pages_to_book(book_id, pages):
                    print(f"Failed to add pages for book {book_id}")
                    return False
            
            # Add chapters to database
            chapters = manifest.get('chapters', [])
            if chapters:
                if not self.audiobook_service.add_chapters_to_book(book_id, chapters):
                    print(f"Failed to add chapters for book {book_id}")
                    return False
            
            # Migrate cover image
            cover_path = book_dir / "cover.png"
            if cover_path.exists():
                with open(cover_path, 'rb') as f:
                    cover_data = f.read()
                self.audiobook_service.book_service.update_book(book_id, {
                    'cover_image_data': cover_data,
                    'cover_image_type': 'image/png'
                })
            
            # Migrate chapter summaries
            chapters_dir = book_dir / "chapters"
            if chapters_dir.exists():
                for chapter_file in chapters_dir.glob("chapter_*.json"):
                    try:
                        with open(chapter_file, 'r', encoding='utf-8') as f:
                            summary_data = json.load(f)
                        
                        # Extract chapter index from filename
                        chapter_num = int(chapter_file.stem.split('_')[-1])
                        
                        # Find corresponding chapter in database
                        db_chapters = self.audiobook_service.chapter_service.get_chapters(book_id)
                        for db_chapter in db_chapters:
                            if db_chapter['start_page'] == chapter_num:
                                summary_text = summary_data.get('summary', '')
                                if summary_text:
                                    self.audiobook_service.chapter_service.update_chapter_summary(
                                        book_id, db_chapter['chapter_index'], summary_text
                                    )
                                break
                    except Exception as e:
                        print(f"Error migrating chapter summary {chapter_file}: {e}")
            
            # Migrate audio files
            audio_dir = book_dir / "audio"
            if audio_dir.exists():
                for audio_file in audio_dir.glob("chapter_*.wav"):
                    try:
                        with open(audio_file, 'rb') as f:
                            audio_data = f.read()
                        
                        # Extract chapter number from filename
                        chapter_num = int(audio_file.stem.split('_')[-1])
                        
                        # Find corresponding chapter in database
                        db_chapters = self.audiobook_service.chapter_service.get_chapters(book_id)
                        for db_chapter in db_chapters:
                            if db_chapter['start_page'] == chapter_num:
                                self.audiobook_service.chapter_service.update_chapter_audio(
                                    book_id, db_chapter['chapter_index'], audio_data, 'audio/wav'
                                )
                                break
                    except Exception as e:
                        print(f"Error migrating audio file {audio_file}: {e}")
            
            print(f"Successfully migrated book: {book_id}")
            return True
            
        except Exception as e:
            print(f"Error migrating book {book_id}: {e}")
            return False
    
    def backup_original_data(self, backup_dir: str = "data_backup") -> bool:
        """Create a backup of original data before migration."""
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            if self.data_dir.exists():
                import shutil
                shutil.copytree(self.data_dir, backup_path / "books")
                print(f"Original data backed up to: {backup_path}")
                return True
            else:
                print("No original data to backup")
                return True
                
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """Verify that migration was successful."""
        try:
            # Get all books from database
            books = self.audiobook_service.get_all_audiobooks()
            print(f"Found {len(books)} books in database after migration")
            
            for audiobook_info in books:
                book = audiobook_info['book']
                chapters = audiobook_info['chapters']
                processing_status = audiobook_info['processing_status']
                
                print(f"Book: {book['title']}")
                print(f"  - Chapters: {len(chapters)}")
                print(f"  - Status: {processing_status.get('overall_status', 'unknown')}")
                
                # Check for audio data
                audio_chapters = [ch for ch in chapters if ch.get('audio_data')]
                print(f"  - Audio chapters: {len(audio_chapters)}")
            
            return True
            
        except Exception as e:
            print(f"Verification failed: {e}")
            return False

def main():
    """Main migration function."""
    print("Starting migration from file-based storage to database...")
    
    migrator = DataMigrator()
    
    # Create backup
    print("Creating backup of original data...")
    if not migrator.backup_original_data():
        print("Backup failed, aborting migration")
        return False
    
    # Perform migration
    print("Starting migration...")
    if not migrator.migrate_all_books():
        print("Migration failed")
        return False
    
    # Verify migration
    print("Verifying migration...")
    if not migrator.verify_migration():
        print("Migration verification failed")
        return False
    
    print("Migration completed successfully!")
    print("You can now safely delete the original data/books directory if desired.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
