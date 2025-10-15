"""
Backend package for Audiobook Generator
Contains data access layer and business logic layer
"""

from .data_access_layer import (
    DatabaseConnection,
    RepositoryFactory,
    BookRepository,
    ChapterRepository,
    PageRepository,
    ProcessingLogRepository,
    BaseRepository,
    db_connection,
    repository_factory
)

from .business_logic_layer import (
    BookService,
    ChapterService,
    PageService,
    ProcessingService,
    AudiobookService
)

__all__ = [
    'DatabaseConnection',
    'RepositoryFactory', 
    'BookRepository',
    'ChapterRepository',
    'PageRepository',
    'ProcessingLogRepository',
    'BaseRepository',
    'db_connection',
    'repository_factory',
    'BookService',
    'ChapterService',
    'PageService',
    'ProcessingService',
    'AudiobookService'
]
