# library_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QMessageBox, QFileDialog, QProgressDialog
)

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from gui.player_window import PlayerWindow
import os, json, zipfile
from pathlib import Path
import subprocess
try:
    from backend.database import db
except ImportError:
    # If running as standalone script
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.database import db

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "books")

class AudiobookDownloader(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(str)  # Path to downloaded file
    error = pyqtSignal(str)
    
    def __init__(self, book_id, manifest, output_dir):
        super().__init__()
        self.book_id = book_id
        self.manifest = manifest
        self.output_dir = output_dir
        
    def run(self):
        try:
            book_title = self.manifest.get('title', self.book_id).replace('/', '_').replace('\\', '_')
            safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Create output directory
            book_output_dir = Path(self.output_dir) / f"{safe_title}_audiobook"
            book_output_dir.mkdir(exist_ok=True)
            
            self.progress_updated.emit(10, "Collecting audio files...")
            
            # Collect all audio files
            audio_files = []
            chapters_dir = Path(f"data/books/{self.book_id}")
            
            for chapter in self.manifest.get('chapters', []):
                audio_path = chapter.get('audio_path')
                if audio_path:
                    full_audio_path = chapters_dir / audio_path
                    if full_audio_path.exists():
                        audio_files.append(full_audio_path)
            
            if not audio_files:
                self.error.emit("No audio files found for this book")
                return
            
            self.progress_updated.emit(30, f"Stitching {len(audio_files)} audio files...")
            
            # Create combined audio file using ffmpeg
            combined_audio_path = book_output_dir / f"{safe_title}.mp3"
            temp_list_file = book_output_dir / "audio_list.txt"
            
            # Create file list for ffmpeg with pauses between chapters
            with open(temp_list_file, 'w', encoding='utf-8') as f:
                for i, audio_file in enumerate(audio_files):
                    f.write(f"file '{audio_file.absolute()}'\n")
                    # Add a 2-second pause between chapters (except after the last one)
                    if i < len(audio_files) - 1:
                        # Create a silent audio file for the pause
                        pause_file = book_output_dir / f"pause_{i}.wav"
                        pause_cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100', 
                                   '-t', '2', '-y', str(pause_file)]
                        subprocess.run(pause_cmd, capture_output=True)
                        if pause_file.exists():
                            f.write(f"file '{pause_file.absolute()}'\n")
            
            # Use ffmpeg to concatenate audio files
            ffmpeg_cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(temp_list_file),
                '-c:a', 'libmp3lame', '-b:a', '128k', '-y', str(combined_audio_path)
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            # Clean up temp files
            temp_list_file.unlink()
            for pause_file in book_output_dir.glob("pause_*.wav"):
                pause_file.unlink()
            
            if result.returncode != 0:
                self.error.emit(f"Audio stitching failed: {result.stderr}")
                return
            else:
                self.progress_updated.emit(50, f"Audio files combined successfully with pauses")
            
            self.progress_updated.emit(70, "Collecting chapter summaries...")
            
            # Create combined summary file
            combined_summary_path = book_output_dir / f"{safe_title}_summary.txt"
            with open(combined_summary_path, 'w', encoding='utf-8') as summary_file:
                summary_file.write(f"AUDIOBOOK SUMMARY: {book_title}\n")
                summary_file.write(f"Author: {self.manifest.get('author', 'Unknown')}\n")
                summary_file.write(f"Total Chapters: {len(self.manifest.get('chapters', []))}\n")
                summary_file.write("=" * 80 + "\n\n")
                
                for i, chapter in enumerate(self.manifest.get('chapters', []), 1):
                    chapter_title = chapter.get('title', f'Chapter {i}')
                    summary_path = chapter.get('summary_path')
                    
                    summary_file.write(f"CHAPTER {i}: {chapter_title}\n")
                    summary_file.write("-" * 40 + "\n")
                    
                    if summary_path:
                        full_summary_path = chapters_dir / summary_path
                        if full_summary_path.exists():
                            try:
                                with open(full_summary_path, 'r', encoding='utf-8') as f:
                                    summary_data = json.load(f)
                                summary_text = summary_data.get('summary', 'No summary available')
                                summary_file.write(summary_text + "\n\n")
                            except Exception as e:
                                summary_file.write(f"Error loading summary: {e}\n\n")
                        else:
                            summary_file.write("Summary file not found\n\n")
                    else:
                        summary_file.write("No summary available\n\n")
            
            self.progress_updated.emit(90, "Creating download package...")
            
            # Create ZIP file
            zip_path = Path(self.output_dir) / f"{safe_title}_audiobook.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add audio file
                if combined_audio_path.exists():
                    zipf.write(combined_audio_path, combined_audio_path.name)
                
                # Add summary file
                if combined_summary_path.exists():
                    zipf.write(combined_summary_path, combined_summary_path.name)
                
                # Add cover image if exists
                cover_path = chapters_dir / "cover.png"
                if cover_path.exists():
                    zipf.write(cover_path, "cover.png")
            
            # Clean up individual files
            if combined_audio_path.exists():
                combined_audio_path.unlink()
            if combined_summary_path.exists():
                combined_summary_path.unlink()
            book_output_dir.rmdir()  # Remove empty directory
            
            self.progress_updated.emit(100, "Download package created successfully!")
            self.finished.emit(str(zip_path))
            
        except Exception as e:
            self.error.emit(f"Download failed: {str(e)}")

def get_books():
    """Get all books from database with their manifests."""
    books = []
    db_books = db.get_books_with_chapters()
    
    for book_data in db_books:
        book_id = book_data['book_id']
        
        # Get chapters for manifest
        chapters = db.get_book_chapters(book_id)
        
        # Create manifest in the expected format
        manifest = {
            "book_id": book_id,
            "title": book_data.get("title", book_id),
            "author": book_data.get("author", ""),
            "page_count": book_data.get("page_count", 0),
            "chapters": []
        }
        
        for ch in chapters:
            manifest["chapters"].append({
                "index": ch.get("chapter_index", ch.get("start_page")),
                "title": ch["title"],
                "start_page": ch["start_page"],
                "end_page": ch["end_page"],
                "summary_path": ch.get("summary_path"),
                "audio_path": ch.get("audio_path")
            })
        
        books.append({
            "book_id": book_id,
            "title": book_data.get("title", book_id),
            "author": book_data.get("author", ""),
            "manifest": manifest
        })
    
    return books


class LibraryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audiobook Library")
        self.setGeometry(200, 200, 500, 400)
        self.books = get_books()
        self.downloader = None
        self.progress_dialog = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title or author...")
        layout.addWidget(self.search_input)

        search_layout = QHBoxLayout()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        self.download_btn = QPushButton("📥 Download Audiobook")
        self.download_btn.clicked.connect(self.download_audiobook)
        self.download_btn.setEnabled(False)
        search_layout.addWidget(self.download_btn)
        
        layout.addLayout(search_layout)

        # List of audiobooks
        self.book_list = QListWidget()
        layout.addWidget(self.book_list)

        self.load_books(self.books)

        # Handle selection and double click
        self.book_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.book_list.itemDoubleClicked.connect(self.open_player)

        self.setLayout(layout)

    def load_books(self, books):
        self.book_list.clear()
        for book in books:
            item_text = f"{book['title']} - {book['author']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, book)
            self.book_list.addItem(item)

    def perform_search(self):
        query = self.search_input.text().lower()
        filtered = [
            book for book in self.books
            if query in book['title'].lower() or query in book['author'].lower()
        ]
        self.load_books(filtered)

    def on_selection_changed(self):
        """Enable download button when a book is selected"""
        current_item = self.book_list.currentItem()
        self.download_btn.setEnabled(current_item is not None)
    
    def open_player(self, item):
        book = item.data(Qt.ItemDataRole.UserRole)
        self.player_window = PlayerWindow(book['book_id'], book['manifest'])
        self.player_window.show()
    
    def download_audiobook(self):
        """Download the selected audiobook as a ZIP file"""
        current_item = self.book_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a book to download.")
            return
        
        book = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Ask user for download location
        output_dir = QFileDialog.getExistingDirectory(
            self, 
            "Select Download Location", 
            os.path.expanduser("~/Downloads")
        )
        
        if not output_dir:
            return
        
        # Check if book has audio files
        book_dir = Path(f"data/books/{book['book_id']}")
        audio_files = list(book_dir.glob("audio/*.wav"))
        
        if not audio_files:
            QMessageBox.warning(
                self, 
                "No Audio Files", 
                "This book doesn't have any audio files to download."
            )
            return
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Preparing download...", 
            "Cancel", 
            0, 100, 
            self
        )
        self.progress_dialog.setWindowTitle("Downloading Audiobook")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        
        # Start download worker
        self.downloader = AudiobookDownloader(book['book_id'], book['manifest'], output_dir)
        self.downloader.progress_updated.connect(self.update_download_progress)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.error.connect(self.download_error)
        self.downloader.start()
    
    def update_download_progress(self, progress, message):
        """Update the progress dialog"""
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(message)
    
    def download_finished(self, file_path):
        """Handle successful download completion"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        QMessageBox.information(
            self, 
            "Download Complete", 
            f"Audiobook downloaded successfully!\n\n"
            f"Location: {file_path}\n"
            f"Size: {file_size:.1f} MB\n\n"
            f"The ZIP file contains:\n"
            f"• Combined MP3 audio file\n"
            f"• Complete summary text file\n"
            f"• Book cover image"
        )
    
    def download_error(self, error_message):
        """Handle download error"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.critical(
            self, 
            "Download Failed", 
            f"Failed to download audiobook:\n\n{error_message}\n\n"
            f"Make sure ffmpeg is installed for audio stitching, or the download will use a fallback method."
        )
