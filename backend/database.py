"""
database.py
SQLite database management for audiobook app.
Replaces JSON manifest files with proper database storage.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

class AudiobookDB:
    def __init__(self, db_path="data/audiobooks.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Books table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT,
                    genre TEXT,
                    year TEXT,
                    page_count INTEGER,
                    cover_image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chapters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id TEXT NOT NULL,
                    chapter_index INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    start_page INTEGER NOT NULL,
                    end_page INTEGER NOT NULL,
                    summary_path TEXT,
                    audio_path TEXT,
                    summary_text TEXT,
                    processing_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books (book_id),
                    UNIQUE(book_id, chapter_index)
                )
            ''')
            
            # Pages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    text_content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books (book_id),
                    UNIQUE(book_id, page_number)
                )
            ''')
            
            conn.commit()
    
    def add_book(self, book_id, title, author=None, genre=None, year=None, page_count=None, cover_image_path=None):
        """Add a new book to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO books 
                (book_id, title, author, genre, year, page_count, cover_image_path, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (book_id, title, author, genre, year, page_count, cover_image_path))
            conn.commit()
    
    def add_chapters(self, book_id, chapters):
        """Add chapters for a book."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for i, chapter in enumerate(chapters):
                cursor.execute('''
                    INSERT OR REPLACE INTO chapters 
                    (book_id, chapter_index, title, start_page, end_page, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (book_id, i, chapter.get('title', f'Chapter {i+1}'), 
                      chapter.get('start_page', 1), chapter.get('end_page', 1)))
            conn.commit()
    
    def add_pages(self, book_id, pages):
        """Add pages for a book."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for page in pages:
                cursor.execute('''
                    INSERT OR REPLACE INTO pages 
                    (book_id, page_number, text_content)
                    VALUES (?, ?, ?)
                ''', (book_id, page.get('page_number', 1), page.get('text', '')))
            conn.commit()
    
    def update_chapter_summary(self, book_id, chapter_index, summary_path, summary_text):
        """Update chapter with summary information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE chapters 
                SET summary_path = ?, summary_text = ?, processing_status = 'summarized', updated_at = CURRENT_TIMESTAMP
                WHERE book_id = ? AND chapter_index = ?
            ''', (summary_path, summary_text, book_id, chapter_index))
            conn.commit()
    
    def update_chapter_audio(self, book_id, chapter_index, audio_path):
        """Update chapter with audio information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE chapters 
                SET audio_path = ?, processing_status = 'completed', updated_at = CURRENT_TIMESTAMP
                WHERE book_id = ? AND chapter_index = ?
            ''', (audio_path, book_id, chapter_index))
            conn.commit()
    
    def get_book(self, book_id):
        """Get book information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
    
    def get_book_chapters(self, book_id):
        """Get all chapters for a book."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM chapters 
                WHERE book_id = ? 
                ORDER BY chapter_index
            ''', (book_id,))
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    def get_chapter_pages(self, book_id, start_page, end_page):
        """Get page content for a chapter."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM pages 
                WHERE book_id = ? AND page_number >= ? AND page_number <= ?
                ORDER BY page_number
            ''', (book_id, start_page, end_page))
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    def get_all_books(self):
        """Get all books in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books ORDER BY created_at DESC')
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    def get_books_with_chapters(self):
        """Get all books with their chapter counts and processing status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.*, 
                       COUNT(c.id) as chapter_count,
                       COUNT(CASE WHEN c.processing_status = 'completed' THEN 1 END) as completed_chapters
                FROM books b
                LEFT JOIN chapters c ON b.book_id = c.book_id
                GROUP BY b.book_id
                ORDER BY b.created_at DESC
            ''')
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    
    def delete_book(self, book_id):
        """Delete a book and all its associated data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM pages WHERE book_id = ?', (book_id,))
            cursor.execute('DELETE FROM chapters WHERE book_id = ?', (book_id,))
            cursor.execute('DELETE FROM books WHERE book_id = ?', (book_id,))
            conn.commit()
    
    def get_processing_stats(self, book_id):
        """Get processing statistics for a book."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_chapters,
                    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN processing_status = 'summarized' THEN 1 END) as summarized,
                    COUNT(CASE WHEN processing_status = 'pending' THEN 1 END) as pending
                FROM chapters 
                WHERE book_id = ?
            ''', (book_id,))
            result = cursor.fetchone()
            return {
                'total_chapters': result[0],
                'completed': result[1],
                'summarized': result[2],
                'pending': result[3]
            }

# Global database instance
db = AudiobookDB()

if __name__ == "__main__":
    # Test the database
    print("Testing Audiobook Database...")
    
    # Add a test book
    db.add_book("test_book", "Test Book", "Test Author", "Test Genre", "2024")
    db.add_chapters("test_book", [
        {"title": "Chapter 1", "start_page": 1, "end_page": 10},
        {"title": "Chapter 2", "start_page": 11, "end_page": 20}
    ])
    
    # Test queries
    books = db.get_all_books()
    print(f"Books in database: {len(books)}")
    
    chapters = db.get_book_chapters("test_book")
    print(f"Chapters for test book: {len(chapters)}")
    
    print("Database test completed!")
