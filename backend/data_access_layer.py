"""
Data Access Layer (DAL)
Handles all database operations with proper OOP patterns.
This layer abstracts database operations from business logic.
"""

import sqlite3
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

class DatabaseConnection:
    """Singleton database connection manager."""
    _instance = None
    _connection = None
    
    def __new__(cls, db_path="data/audiobooks.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path="data/audiobooks.db"):
        if self._connection is None:
            self.db_path = db_path
            self._connection = sqlite3.connect(db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        cursor = self._connection.cursor()
        
        # Books table - stores book metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                genre TEXT,
                year TEXT,
                page_count INTEGER,
                cover_image_data BLOB,  -- Store cover as BLOB
                cover_image_type TEXT,  -- MIME type (image/png, image/jpeg)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chapters table - stores chapter information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT NOT NULL,
                chapter_index INTEGER NOT NULL,
                title TEXT NOT NULL,
                start_page INTEGER NOT NULL,
                end_page INTEGER NOT NULL,
                summary_text TEXT,  -- Store summary directly in DB
                audio_data BLOB,    -- Store audio as BLOB
                audio_format TEXT,  -- audio/wav, audio/mp3, etc.
                processing_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                UNIQUE(book_id, chapter_index)
            )
        ''')
        
        # Pages table - stores page content
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
        
        # Processing logs table - for tracking processing status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT NOT NULL,
                stage TEXT NOT NULL,  -- extraction, summarization, audio_generation
                status TEXT NOT NULL, -- pending, in_progress, completed, failed
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (book_id)
            )
        ''')
        
        self._connection.commit()
    
    def get_connection(self):
        """Get database connection."""
        return self._connection
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

class BaseRepository(ABC):
    """Abstract base class for repositories."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection.get_connection()
    
    @abstractmethod
    def create(self, entity: Dict[str, Any]) -> int:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: Any) -> Optional[Dict[str, Any]]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def update(self, entity_id: Any, updates: Dict[str, Any]) -> bool:
        """Update entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        """Delete entity."""
        pass

class BookRepository(BaseRepository):
    """Repository for book operations."""
    
    def create(self, book_data: Dict[str, Any]) -> int:
        """Create a new book."""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO books (book_id, title, author, genre, year, page_count, cover_image_data, cover_image_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            book_data['book_id'],
            book_data['title'],
            book_data.get('author'),
            book_data.get('genre'),
            book_data.get('year'),
            book_data.get('page_count'),
            book_data.get('cover_image_data'),
            book_data.get('cover_image_type')
        ))
        self.db.commit()
        return cursor.lastrowid
    
    def get_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Get book by ID."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all books."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM books ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, book_id: str, updates: Dict[str, Any]) -> bool:
        """Update book."""
        cursor = self.db.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [book_id]
        cursor.execute(f'UPDATE books SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE book_id = ?', values)
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete(self, book_id: str) -> bool:
        """Delete book and all related data."""
        cursor = self.db.cursor()
        # Delete in order to respect foreign key constraints
        cursor.execute('DELETE FROM pages WHERE book_id = ?', (book_id,))
        cursor.execute('DELETE FROM chapters WHERE book_id = ?', (book_id,))
        cursor.execute('DELETE FROM processing_logs WHERE book_id = ?', (book_id,))
        cursor.execute('DELETE FROM books WHERE book_id = ?', (book_id,))
        self.db.commit()
        return cursor.rowcount > 0
    
    def get_with_stats(self) -> List[Dict[str, Any]]:
        """Get books with processing statistics."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT b.*, 
                   COUNT(c.id) as chapter_count,
                   COUNT(CASE WHEN c.processing_status = 'completed' THEN 1 END) as completed_chapters
            FROM books b
            LEFT JOIN chapters c ON b.book_id = c.book_id
            GROUP BY b.book_id
            ORDER BY b.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

class ChapterRepository(BaseRepository):
    """Repository for chapter operations."""
    
    def create(self, chapter_data: Dict[str, Any]) -> int:
        """Create a new chapter."""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO chapters (book_id, chapter_index, title, start_page, end_page, summary_text, audio_data, audio_format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chapter_data['book_id'],
            chapter_data['chapter_index'],
            chapter_data['title'],
            chapter_data['start_page'],
            chapter_data['end_page'],
            chapter_data.get('summary_text'),
            chapter_data.get('audio_data'),
            chapter_data.get('audio_format')
        ))
        self.db.commit()
        return cursor.lastrowid
    
    def get_by_id(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """Get chapter by ID."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """Get all chapters for a book."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM chapters 
            WHERE book_id = ? 
            ORDER BY chapter_index
        ''', (book_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, chapter_id: int, updates: Dict[str, Any]) -> bool:
        """Update chapter."""
        cursor = self.db.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [chapter_id]
        cursor.execute(f'UPDATE chapters SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', values)
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete(self, chapter_id: int) -> bool:
        """Delete chapter."""
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM chapters WHERE id = ?', (chapter_id,))
        self.db.commit()
        return cursor.rowcount > 0
    
    def update_summary(self, book_id: str, chapter_index: int, summary_text: str) -> bool:
        """Update chapter summary."""
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE chapters 
            SET summary_text = ?, processing_status = 'summarized', updated_at = CURRENT_TIMESTAMP
            WHERE book_id = ? AND chapter_index = ?
        ''', (summary_text, book_id, chapter_index))
        self.db.commit()
        return cursor.rowcount > 0
    
    def update_audio(self, book_id: str, chapter_index: int, audio_data: bytes, audio_format: str = 'audio/wav') -> bool:
        """Update chapter audio."""
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE chapters 
            SET audio_data = ?, audio_format = ?, processing_status = 'completed', updated_at = CURRENT_TIMESTAMP
            WHERE book_id = ? AND chapter_index = ?
        ''', (audio_data, audio_format, book_id, chapter_index))
        self.db.commit()
        return cursor.rowcount > 0

class PageRepository(BaseRepository):
    """Repository for page operations."""
    
    def create(self, page_data: Dict[str, Any]) -> int:
        """Create a new page."""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO pages (book_id, page_number, text_content)
            VALUES (?, ?, ?)
        ''', (
            page_data['book_id'],
            page_data['page_number'],
            page_data['text_content']
        ))
        self.db.commit()
        return cursor.lastrowid
    
    def get_by_id(self, page_id: int) -> Optional[Dict[str, Any]]:
        """Get page by ID."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """Get all pages for a book."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM pages 
            WHERE book_id = ? 
            ORDER BY page_number
        ''', (book_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_chapter(self, book_id: str, start_page: int, end_page: int) -> List[Dict[str, Any]]:
        """Get pages for a specific chapter."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM pages 
            WHERE book_id = ? AND page_number >= ? AND page_number <= ?
            ORDER BY page_number
        ''', (book_id, start_page, end_page))
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, page_id: int, updates: Dict[str, Any]) -> bool:
        """Update page."""
        cursor = self.db.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [page_id]
        cursor.execute(f'UPDATE pages SET {set_clause} WHERE id = ?', values)
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete(self, page_id: int) -> bool:
        """Delete page."""
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))
        self.db.commit()
        return cursor.rowcount > 0

class ProcessingLogRepository(BaseRepository):
    """Repository for processing log operations."""
    
    def create(self, log_data: Dict[str, Any]) -> int:
        """Create a new processing log."""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO processing_logs (book_id, stage, status, message)
            VALUES (?, ?, ?, ?)
        ''', (
            log_data['book_id'],
            log_data['stage'],
            log_data['status'],
            log_data.get('message')
        ))
        self.db.commit()
        return cursor.lastrowid
    
    def get_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """Get log by ID."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM processing_logs WHERE id = ?', (log_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a book."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM processing_logs 
            WHERE book_id = ? 
            ORDER BY created_at DESC
        ''', (book_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, log_id: int, updates: Dict[str, Any]) -> bool:
        """Update log."""
        cursor = self.db.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [log_id]
        cursor.execute(f'UPDATE processing_logs SET {set_clause} WHERE id = ?', values)
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete(self, log_id: int) -> bool:
        """Delete log."""
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM processing_logs WHERE id = ?', (log_id,))
        self.db.commit()
        return cursor.rowcount > 0

# Factory for creating repositories
class RepositoryFactory:
    """Factory for creating repository instances."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
    
    def get_book_repository(self) -> BookRepository:
        """Get book repository."""
        return BookRepository(self.db_connection)
    
    def get_chapter_repository(self) -> ChapterRepository:
        """Get chapter repository."""
        return ChapterRepository(self.db_connection)
    
    def get_page_repository(self) -> PageRepository:
        """Get page repository."""
        return PageRepository(self.db_connection)
    
    def get_processing_log_repository(self) -> ProcessingLogRepository:
        """Get processing log repository."""
        return ProcessingLogRepository(self.db_connection)

# Global instances
db_connection = DatabaseConnection()
repository_factory = RepositoryFactory(db_connection)

# Export for easy importing
__all__ = [
    'DatabaseConnection', 'RepositoryFactory', 'BookRepository', 'ChapterRepository', 
    'PageRepository', 'ProcessingLogRepository', 'BaseRepository',
    'db_connection', 'repository_factory'
]
