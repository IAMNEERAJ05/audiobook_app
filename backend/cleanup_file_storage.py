"""
Cleanup Script - Remove file-based storage after migration
This script removes all file-based storage dependencies after successful migration.
"""

import os
import shutil
from pathlib import Path
from typing import List

class FileStorageCleanup:
    """Cleans up file-based storage after migration to database."""
    
    def __init__(self):
        self.data_dir = Path("data/books")
        self.backup_dir = Path("data_backup")
    
    def cleanup_books_directory(self, create_backup: bool = True) -> bool:
        """Remove the books directory and all its contents."""
        try:
            if not self.data_dir.exists():
                print("No books directory found to clean up")
                return True
            
            if create_backup:
                print("Creating final backup before cleanup...")
                if self.backup_dir.exists():
                    shutil.rmtree(self.backup_dir)
                shutil.copytree(self.data_dir, self.backup_dir)
                print(f"Final backup created at: {self.backup_dir}")
            
            # Remove the books directory
            shutil.rmtree(self.data_dir)
            print(f"Removed directory: {self.data_dir}")
            
            return True
            
        except Exception as e:
            print(f"Error cleaning up books directory: {e}")
            return False
    
    def cleanup_old_manifest_files(self) -> bool:
        """Remove old manifest files that are no longer needed."""
        try:
            # Look for any remaining manifest files in the data directory
            data_path = Path("data")
            if data_path.exists():
                manifest_files = list(data_path.rglob("manifest*.json"))
                for manifest_file in manifest_files:
                    try:
                        manifest_file.unlink()
                        print(f"Removed old manifest: {manifest_file}")
                    except Exception as e:
                        print(f"Error removing {manifest_file}: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error cleaning up manifest files: {e}")
            return False
    
    def cleanup_temp_files(self) -> bool:
        """Clean up any temporary files."""
        try:
            # Clean up any .pyc files
            for pyc_file in Path(".").rglob("*.pyc"):
                try:
                    pyc_file.unlink()
                    print(f"Removed .pyc file: {pyc_file}")
                except Exception as e:
                    print(f"Error removing {pyc_file}: {e}")
            
            # Clean up __pycache__ directories
            for pycache_dir in Path(".").rglob("__pycache__"):
                try:
                    shutil.rmtree(pycache_dir)
                    print(f"Removed __pycache__: {pycache_dir}")
                except Exception as e:
                    print(f"Error removing {pycache_dir}: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
            return False
    
    def verify_cleanup(self) -> bool:
        """Verify that cleanup was successful."""
        try:
            # Check that books directory is gone
            if self.data_dir.exists():
                print(f"Warning: Books directory still exists: {self.data_dir}")
                return False
            
            # Check that database still works
            from .business_logic_layer import AudiobookService
            from .data_access_layer import repository_factory
            
            audiobook_service = AudiobookService(repository_factory)
            books = audiobook_service.get_all_audiobooks()
            print(f"Database verification: {len(books)} books found in database")
            
            return True
            
        except Exception as e:
            print(f"Cleanup verification failed: {e}")
            return False
    
    def full_cleanup(self, create_backup: bool = True) -> bool:
        """Perform full cleanup of file-based storage."""
        try:
            print("Starting full cleanup of file-based storage...")
            
            # Step 1: Clean up books directory
            if not self.cleanup_books_directory(create_backup):
                print("Failed to clean up books directory")
                return False
            
            # Step 2: Clean up old manifest files
            if not self.cleanup_old_manifest_files():
                print("Failed to clean up manifest files")
                return False
            
            # Step 3: Clean up temp files
            if not self.cleanup_temp_files():
                print("Failed to clean up temp files")
                return False
            
            # Step 4: Verify cleanup
            if not self.verify_cleanup():
                print("Cleanup verification failed")
                return False
            
            print("Full cleanup completed successfully!")
            print("All file-based storage has been removed.")
            print("The application now uses database-only storage.")
            
            return True
            
        except Exception as e:
            print(f"Full cleanup failed: {e}")
            return False

def main():
    """Main cleanup function."""
    print("Starting cleanup of file-based storage...")
    print("This will remove all file-based storage after migration to database.")
    
    response = input("Are you sure you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Cleanup cancelled")
        return False
    
    cleanup = FileStorageCleanup()
    success = cleanup.full_cleanup(create_backup=True)
    
    if success:
        print("\nCleanup completed successfully!")
        print("Your application now uses database-only storage.")
        print("A backup of the original data has been created in 'data_backup' directory.")
    else:
        print("\nCleanup failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
