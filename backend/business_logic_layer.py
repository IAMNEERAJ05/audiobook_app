"""
Business Logic Layer (BLL)
Contains all business logic and domain operations.
This layer uses the Data Access Layer for database operations.
"""

from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import base64
import json
from datetime import datetime

try:
    from .data_access_layer import (
        RepositoryFactory, 
        BookRepository, 
        ChapterRepository, 
        PageRepository, 
        ProcessingLogRepository
    )
except ImportError:
    from data_access_layer import (
        RepositoryFactory, 
        BookRepository, 
        ChapterRepository, 
        PageRepository, 
        ProcessingLogRepository
    )

class BookService:
    """Service for book-related business logic."""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.book_repo = repository_factory.get_book_repository()
        self.chapter_repo = repository_factory.get_chapter_repository()
        self.page_repo = repository_factory.get_page_repository()
        self.log_repo = repository_factory.get_processing_log_repository()
    
    def create_book(self, book_id: str, title: str, author: str = None, 
                   genre: str = None, year: str = None, page_count: int = None,
                   cover_image_path: str = None) -> bool:
        """Create a new book with metadata."""
        try:
            # Load cover image if provided
            cover_data = None
            cover_type = None
            if cover_image_path and Path(cover_image_path).exists():
                with open(cover_image_path, 'rb') as f:
                    cover_data = f.read()
                cover_type = f"image/{Path(cover_image_path).suffix[1:]}"
            
            book_data = {
                'book_id': book_id,
                'title': title,
                'author': author,
                'genre': genre,
                'year': year,
                'page_count': page_count,
                'cover_image_data': cover_data,
                'cover_image_type': cover_type
            }
            
            self.book_repo.create(book_data)
            self._log_processing(book_id, 'book_creation', 'completed', f"Book '{title}' created successfully")
            return True
            
        except Exception as e:
            self._log_processing(book_id, 'book_creation', 'failed', f"Failed to create book: {str(e)}")
            return False
    
    def get_book(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Get book information."""
        return self.book_repo.get_by_id(book_id)
    
    def get_all_books(self) -> List[Dict[str, Any]]:
        """Get all books with processing statistics."""
        return self.book_repo.get_with_stats()
    
    def update_book(self, book_id: str, updates: Dict[str, Any]) -> bool:
        """Update book information."""
        return self.book_repo.update(book_id, updates)
    
    def delete_book(self, book_id: str) -> bool:
        """Delete book and all associated data."""
        try:
            self._log_processing(book_id, 'book_deletion', 'in_progress', "Starting book deletion")
            success = self.book_repo.delete(book_id)
            if success:
                self._log_processing(book_id, 'book_deletion', 'completed', "Book deleted successfully")
            else:
                self._log_processing(book_id, 'book_deletion', 'failed', "Book not found")
            return success
        except Exception as e:
            self._log_processing(book_id, 'book_deletion', 'failed', f"Failed to delete book: {str(e)}")
            return False
    
    def get_book_cover(self, book_id: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Get book cover image data and type."""
        book = self.get_book(book_id)
        if book and book.get('cover_image_data'):
            return book['cover_image_data'], book.get('cover_image_type')
        return None, None
    
    def _log_processing(self, book_id: str, stage: str, status: str, message: str):
        """Log processing activity."""
        self.log_repo.create({
            'book_id': book_id,
            'stage': stage,
            'status': status,
            'message': message
        })

class ChapterService:
    """Service for chapter-related business logic."""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.chapter_repo = repository_factory.get_chapter_repository()
        self.page_repo = repository_factory.get_page_repository()
        self.log_repo = repository_factory.get_processing_log_repository()
    
    def create_chapters(self, book_id: str, chapters: List[Dict[str, Any]]) -> bool:
        """Create chapters for a book."""
        try:
            for i, chapter in enumerate(chapters):
                chapter_data = {
                    'book_id': book_id,
                    'chapter_index': i,
                    'title': chapter.get('title', f'Chapter {i+1}'),
                    'start_page': chapter.get('start_page', 1),
                    'end_page': chapter.get('end_page', 1)
                }
                self.chapter_repo.create(chapter_data)
            
            self._log_processing(book_id, 'chapter_creation', 'completed', f"Created {len(chapters)} chapters")
            return True
            
        except Exception as e:
            self._log_processing(book_id, 'chapter_creation', 'failed', f"Failed to create chapters: {str(e)}")
            return False
    
    def get_chapters(self, book_id: str) -> List[Dict[str, Any]]:
        """Get all chapters for a book."""
        return self.chapter_repo.get_by_book(book_id)
    
    def get_chapter_text(self, book_id: str, start_page: int, end_page: int) -> str:
        """Get combined text for a chapter."""
        pages = self.page_repo.get_by_chapter(book_id, start_page, end_page)
        return "\n\n".join(page['text_content'] for page in pages if page.get('text_content'))
    
    def update_chapter_summary(self, book_id: str, chapter_index: int, summary_text: str) -> bool:
        """Update chapter with summary."""
        try:
            success = self.chapter_repo.update_summary(book_id, chapter_index, summary_text)
            if success:
                self._log_processing(book_id, 'summarization', 'completed', f"Chapter {chapter_index} summarized")
            return success
        except Exception as e:
            self._log_processing(book_id, 'summarization', 'failed', f"Failed to update chapter summary: {str(e)}")
            return False
    
    def update_chapter_audio(self, book_id: str, chapter_index: int, audio_data: bytes, audio_format: str = 'audio/wav') -> bool:
        """Update chapter with audio data."""
        try:
            success = self.chapter_repo.update_audio(book_id, chapter_index, audio_data, audio_format)
            if success:
                self._log_processing(book_id, 'audio_generation', 'completed', f"Chapter {chapter_index} audio generated")
            return success
        except Exception as e:
            self._log_processing(book_id, 'audio_generation', 'failed', f"Failed to update chapter audio: {str(e)}")
            return False
    
    def get_chapter_audio(self, book_id: str, chapter_index: int) -> Tuple[Optional[bytes], Optional[str]]:
        """Get chapter audio data and format."""
        chapters = self.chapter_repo.get_by_book(book_id)
        for chapter in chapters:
            if chapter['chapter_index'] == chapter_index:
                return chapter.get('audio_data'), chapter.get('audio_format')
        return None, None
    
    def get_processing_stats(self, book_id: str) -> Dict[str, int]:
        """Get processing statistics for a book."""
        chapters = self.get_chapters(book_id)
        total = len(chapters)
        completed = sum(1 for ch in chapters if ch.get('processing_status') == 'completed')
        summarized = sum(1 for ch in chapters if ch.get('processing_status') == 'summarized')
        pending = total - completed - summarized
        
        return {
            'total_chapters': total,
            'completed': completed,
            'summarized': summarized,
            'pending': pending
        }
    
    def _log_processing(self, book_id: str, stage: str, status: str, message: str):
        """Log processing activity."""
        self.log_repo.create({
            'book_id': book_id,
            'stage': stage,
            'status': status,
            'message': message
        })

class PageService:
    """Service for page-related business logic."""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.page_repo = repository_factory.get_page_repository()
        self.log_repo = repository_factory.get_processing_log_repository()
    
    def create_pages(self, book_id: str, pages: List[Dict[str, Any]]) -> bool:
        """Create pages for a book."""
        try:
            for page in pages:
                page_data = {
                    'book_id': book_id,
                    'page_number': page.get('page_number', 1),
                    'text_content': page.get('text', '')
                }
                self.page_repo.create(page_data)
            
            self._log_processing(book_id, 'page_extraction', 'completed', f"Extracted {len(pages)} pages")
            return True
            
        except Exception as e:
            self._log_processing(book_id, 'page_extraction', 'failed', f"Failed to create pages: {str(e)}")
            return False
    
    def get_pages(self, book_id: str) -> List[Dict[str, Any]]:
        """Get all pages for a book."""
        return self.page_repo.get_by_book(book_id)
    
    def get_chapter_pages(self, book_id: str, start_page: int, end_page: int) -> List[Dict[str, Any]]:
        """Get pages for a specific chapter."""
        return self.page_repo.get_by_chapter(book_id, start_page, end_page)
    
    def _log_processing(self, book_id: str, stage: str, status: str, message: str):
        """Log processing activity."""
        self.log_repo.create({
            'book_id': book_id,
            'stage': stage,
            'status': status,
            'message': message
        })

class ProcessingService:
    """Service for processing-related business logic."""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.log_repo = repository_factory.get_processing_log_repository()
        self.book_service = BookService(repository_factory)
        self.chapter_service = ChapterService(repository_factory)
        self.page_service = PageService(repository_factory)
    
    def get_processing_logs(self, book_id: str) -> List[Dict[str, Any]]:
        """Get processing logs for a book."""
        return self.log_repo.get_by_book(book_id)
    
    def log_processing_start(self, book_id: str, stage: str, message: str = None):
        """Log the start of a processing stage."""
        self.log_repo.create({
            'book_id': book_id,
            'stage': stage,
            'status': 'in_progress',
            'message': message or f"Starting {stage}"
        })
    
    def log_processing_complete(self, book_id: str, stage: str, message: str = None):
        """Log the completion of a processing stage."""
        self.log_repo.create({
            'book_id': book_id,
            'stage': stage,
            'status': 'completed',
            'message': message or f"Completed {stage}"
        })
    
    def log_processing_error(self, book_id: str, stage: str, error_message: str):
        """Log a processing error."""
        self.log_repo.create({
            'book_id': book_id,
            'stage': stage,
            'status': 'failed',
            'message': f"Error: {error_message}"
        })
    
    def get_processing_status(self, book_id: str) -> Dict[str, Any]:
        """Get overall processing status for a book."""
        logs = self.get_processing_logs(book_id)
        stats = self.chapter_service.get_processing_stats(book_id)
        
        # Determine overall status
        if stats['completed'] == stats['total_chapters'] and stats['total_chapters'] > 0:
            overall_status = 'completed'
        elif stats['summarized'] > 0 or stats['completed'] > 0:
            overall_status = 'in_progress'
        else:
            overall_status = 'pending'
        
        return {
            'overall_status': overall_status,
            'chapter_stats': stats,
            'recent_logs': logs[-10:] if logs else []  # Last 10 logs
        }

class AudiobookService:
    """Main service that orchestrates all audiobook operations."""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.book_service = BookService(repository_factory)
        self.chapter_service = ChapterService(repository_factory)
        self.page_service = PageService(repository_factory)
        self.processing_service = ProcessingService(repository_factory)
    
    def create_audiobook(self, book_id: str, title: str, author: str = None, 
                        genre: str = None, year: str = None, page_count: int = None,
                        cover_image_path: str = None) -> bool:
        """Create a new audiobook with all necessary components."""
        return self.book_service.create_book(book_id, title, author, genre, year, page_count, cover_image_path)
    
    def add_pages_to_book(self, book_id: str, pages: List[Dict[str, Any]]) -> bool:
        """Add extracted pages to a book."""
        return self.page_service.create_pages(book_id, pages)
    
    def add_chapters_to_book(self, book_id: str, chapters: List[Dict[str, Any]]) -> bool:
        """Add chapters to a book."""
        return self.chapter_service.create_chapters(book_id, chapters)
    
    def get_audiobook_info(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Get complete audiobook information."""
        book = self.book_service.get_book(book_id)
        if not book:
            return None
        
        chapters = self.chapter_service.get_chapters(book_id)
        processing_status = self.processing_service.get_processing_status(book_id)
        
        return {
            'book': book,
            'chapters': chapters,
            'processing_status': processing_status
        }
    
    def get_all_audiobooks(self) -> List[Dict[str, Any]]:
        """Get all audiobooks with their information."""
        books = self.book_service.get_all_books()
        result = []
        
        for book in books:
            book_id = book['book_id']
            chapters = self.chapter_service.get_chapters(book_id)
            processing_status = self.processing_service.get_processing_status(book_id)
            
            result.append({
                'book': book,
                'chapters': chapters,
                'processing_status': processing_status
            })
        
        return result
    
    def delete_audiobook(self, book_id: str) -> bool:
        """Delete an audiobook and all its data."""
        return self.book_service.delete_book(book_id)
