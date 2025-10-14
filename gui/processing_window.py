# processing_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, QApplication, QTextEdit,
    QFrame, QHBoxLayout, QSpacerItem, QSizePolicy
)
import sys
import json
import os
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from pathlib import Path

# Import modern components
from gui.components.progress_bar import ProgressWidget
from gui.components.status_log import StatusLogWidget
from gui.components.buttons import ModernButton

class ProcessingWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, pdf_path, book_id):
        super().__init__()
        self.pdf_path = pdf_path
        self.book_id = book_id
        
    def run(self):
        try:
            # Step 1: Extract PDF
            self.progress_updated.emit(10, "Extracting PDF pages...")
            extractor_args = [
                sys.executable, "backend/extractor.py",
                "--pdf_path", str(self.pdf_path),
                "--book_id", str(self.book_id)
            ]
            import subprocess
            result = subprocess.run(extractor_args, capture_output=True, text=True)
            if result.returncode != 0:
                self.error.emit(f"PDF extraction failed: {result.stderr}")
                return
            
            # Step 2: Get chapter count from manifest
            manifest_path = Path(f"data/books/{self.book_id}/manifest.json")
            if not manifest_path.exists():
                self.error.emit("Manifest file not found after extraction")
                return
                
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            chapters = manifest.get("chapters", [])
            total_chapters = len(chapters)
            
            if total_chapters == 0:
                self.error.emit("No chapters found in manifest")
                return
            
            # Step 3: Summarize chapters
            self.progress_updated.emit(20, f"Starting summarization of {total_chapters} chapters...")
            summarizer_args = [
                sys.executable, "backend/summarizer.py",
                "--book_id", str(self.book_id)
            ]
            
            # Run summarizer with progress tracking
            result = subprocess.run(summarizer_args, capture_output=True, text=True)
            if result.returncode != 0:
                self.error.emit(f"Summarization failed: {result.stderr}")
                return
            
            # Parse summarizer output to track chapter progress
            chapters_dir = Path(f"data/books/{self.book_id}/chapters")
            processed_summaries = 0
            for chapter in chapters:
                chapter_file = chapters_dir / f"chapter_{chapter['start_page']:03d}.json"
                if chapter_file.exists():
                    processed_summaries += 1
                    progress = 20 + int((processed_summaries / total_chapters) * 40)
                    self.progress_updated.emit(progress, f"Summarizing chapter {processed_summaries}/{total_chapters}: {chapter['title']}")
            
            # Step 4: Generate audio
            self.progress_updated.emit(60, f"Starting audio generation for {total_chapters} chapters...")
            tts_args = [
                sys.executable, "backend/tts_engine.py",
                "--book_id", str(self.book_id)
            ]
            
            result = subprocess.run(tts_args, capture_output=True, text=True)
            if result.returncode != 0:
                self.error.emit(f"Audio generation failed: {result.stderr}")
                return
            
            # Parse TTS output to track audio progress
            audio_dir = Path(f"data/books/{self.book_id}/audio")
            processed_audio = 0
            for chapter in chapters:
                audio_file = audio_dir / f"chapter_{chapter['start_page']:03d}.wav"
                if audio_file.exists():
                    processed_audio += 1
                    progress = 60 + int((processed_audio / total_chapters) * 30)
                    self.progress_updated.emit(progress, f"Generating audio for chapter {processed_audio}/{total_chapters}: {chapter['title']}")
            
            # Step 5: Build final manifest
            self.progress_updated.emit(90, "Building final manifest...")
            manifest_args = [
                sys.executable, "backend/manifest_final.py",
                "--book_id", str(self.book_id)
            ]
            result = subprocess.run(manifest_args, capture_output=True, text=True)
            if result.returncode != 0:
                self.error.emit(f"Manifest creation failed: {result.stderr}")
                return
            
            self.progress_updated.emit(100, "Processing Complete!")
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Processing error: {str(e)}")

class ProcessingWindow(QWidget):
    def __init__(self, pdf_path=None):
        super().__init__()
        self.setWindowTitle("🔄 Processing Book")
        self.setGeometry(150, 150, 700, 600)
        self.setMinimumSize(600, 500)
        self.pdf_path = pdf_path
        # Generate book_id from filename (simple slug)
        import os
        if pdf_path:
            base = os.path.basename(pdf_path)
            book_id = os.path.splitext(base)[0].replace(" ", "_").replace("-", "_").lower()
        else:
            book_id = "uploaded_book"
        self.book_id = book_id
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)
        
        # Progress section
        self.progress_widget = ProgressWidget()
        main_layout.addWidget(self.progress_widget)
        
        # Status log section
        self.status_log = StatusLogWidget("Processing Log")
        main_layout.addWidget(self.status_log)
        
        # Buttons section
        buttons_frame = self._create_buttons_section()
        main_layout.addWidget(buttons_frame)
        
        self.setLayout(main_layout)
        self.worker = None
        
        # Apply modern styling
        self._apply_modern_styling()
    
    def _create_header(self):
        """Create the header section."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("🔄 Book Processing")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                background: transparent;
                border: none;
                padding: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Book info
        if self.pdf_path:
            book_name = os.path.basename(self.pdf_path)
            book_label = QLabel(f"📖 {book_name}")
        else:
            book_label = QLabel("📖 No book selected")
        
        book_label.setFont(QFont("Segoe UI", 12))
        book_label.setStyleSheet("""
            QLabel {
                color: #7F8C8D;
                background: transparent;
                border: none;
                padding: 5px;
            }
        """)
        book_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(book_label)
        
        frame.setLayout(layout)
        return frame
    
    def _create_buttons_section(self):
        """Create the buttons section."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Start button
        self.start_btn = ModernButton("🚀 Start Processing", primary=True)
        self.start_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_btn)
        
        # Cancel button
        self.cancel_btn = ModernButton("⏹ Cancel", primary=False)
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)
        
        frame.setLayout(layout)
        return frame
    
    def _apply_modern_styling(self):
        """Apply modern styling to the window."""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #F8F9FA, stop: 1 #E9ECEF);
            }
        """)

    def start_processing(self):
        if not self.pdf_path or not isinstance(self.pdf_path, str):
            QMessageBox.critical(self, "Error", "No PDF file selected or invalid path.")
            return
            
        self.status_log.clear_log()
        self.status_log.add_info("Starting audiobook processing...")
        self.status_log.add_info(f"PDF: {self.pdf_path}")
        self.status_log.add_info(f"Book ID: {self.book_id}")
        
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Create and start worker thread
        self.worker = ProcessingWorker(self.pdf_path, self.book_id)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.start()
    
    def update_progress(self, progress, message):
        self.progress_widget.set_progress(progress, message)
        self.status_log.add_info(message)
    
    def processing_finished(self):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_log.add_success("Processing completed successfully!")
        self.progress_widget.set_progress(100, "Complete!")
        QMessageBox.information(self, "🎉 Done", "Audiobook ready! You can now play it from the library.")
    
    def processing_error(self, error_message):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_log.add_error(f"Error: {error_message}")
        self.progress_widget.set_status("Processing failed")
        QMessageBox.critical(self, "❌ Processing Error", f"An error occurred:\n{error_message}")
    
    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_log.add_warning("Processing cancelled by user")
        self.progress_widget.set_status("Processing cancelled")
        self.progress_widget.set_progress(0)
