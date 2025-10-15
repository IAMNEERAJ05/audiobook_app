"""
Processing Window - Refactored to use database-centric architecture
Uses the new business logic layer for all operations.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, QApplication, QTextEdit,
    QFrame, QHBoxLayout, QSpacerItem, QSizePolicy
)
import sys
import os
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from pathlib import Path

# Import modern components
from gui.components.progress_bar import ProgressWidget
from gui.components.status_log import StatusLogWidget
from gui.components.buttons import ModernButton

# Import new backend architecture
try:
    from backend.business_logic_layer import AudiobookService
    from backend.data_access_layer import repository_factory
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.business_logic_layer import AudiobookService
    from backend.data_access_layer import repository_factory

class ProcessingWorker(QThread):
    """Worker thread for processing audiobooks using new architecture."""
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, pdf_path, book_id):
        super().__init__()
        self.pdf_path = pdf_path
        self.book_id = book_id
        self.audiobook_service = AudiobookService(repository_factory)
    
    def run(self):
        try:
            # Step 1: Extract PDF
            self.progress_updated.emit(10, "Extracting PDF pages...")
            try:
                from backend.extractor_new import PDFExtractor
                extractor = PDFExtractor()
                
                if not extractor.process_pdf(self.pdf_path, self.book_id):
                    self.error.emit("PDF extraction failed")
                    return
            except Exception as e:
                self.error.emit(f"PDF extraction failed: {str(e)}")
                return
            
            # Step 2: Get processing stats
            self.progress_updated.emit(20, "Checking extraction results...")
            stats = self.audiobook_service.chapter_service.get_processing_stats(self.book_id)
            total_chapters = stats['total_chapters']
            
            if total_chapters == 0:
                self.error.emit("No chapters found after extraction")
                return
            
            # Step 3: Summarize chapters
            self.progress_updated.emit(30, f"Starting summarization of {total_chapters} chapters...")
            try:
                from backend.summarizer_new import ChapterSummarizer
                summarizer = ChapterSummarizer()
                
                if not summarizer.process_book_chapters(self.book_id):
                    self.error.emit("Chapter summarization failed")
                    return
            except Exception as e:
                self.error.emit(f"Chapter summarization failed: {str(e)}")
                return
            
            # Step 4: Generate audio
            self.progress_updated.emit(70, f"Starting audio generation for {total_chapters} chapters...")
            try:
                from backend.tts_engine_new import TTSEngine
                tts_engine = TTSEngine()
                
                if not tts_engine.process_book_chapters(self.book_id):
                    self.error.emit("Audio generation failed")
                    return
            except Exception as e:
                self.error.emit(f"Audio generation failed: {str(e)}")
                return
            
            # Step 5: Build final manifest
            self.progress_updated.emit(90, "Building final manifest...")
            try:
                from backend.manifest_final_new import ManifestBuilder
                manifest_builder = ManifestBuilder()
                
                manifest = manifest_builder.build_final_manifest(self.book_id)
                if not manifest:
                    self.error.emit("Failed to build final manifest")
                    return
            except Exception as e:
                self.error.emit(f"Failed to build final manifest: {str(e)}")
                return
            
            self.progress_updated.emit(100, "Processing Complete!")
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Processing error: {str(e)}")

class ProcessingWindow(QWidget):
    """Processing window using new architecture."""
    
    def __init__(self, pdf_path=None, parent=None):
        super().__init__()
        self.setWindowTitle("🔄 Processing Book")
        self.setGeometry(150, 150, 700, 600)
        self.setMinimumSize(600, 500)
        self.pdf_path = pdf_path
        self.parent_window = parent
        
        # Generate book_id from filename
        if pdf_path:
            base = os.path.basename(pdf_path)
            book_id = os.path.splitext(base)[0].replace(" ", "_").replace("-", "_").lower()
        else:
            book_id = "uploaded_book"
        self.book_id = book_id
        
        # Initialize audiobook service
        self.audiobook_service = AudiobookService(repository_factory)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
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
    
    def closeEvent(self, event):
        """Ensure closing this window does not exit the app; cancel worker if needed."""
        try:
            if self.worker and self.worker.isRunning():
                reply = QMessageBox.question(
                    self,
                    "Cancel Processing",
                    "Processing is running. Do you want to cancel and close?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    try:
                        self.worker.terminate()
                        self.worker.wait()
                    except Exception:
                        pass
                else:
                    event.ignore()
                    return
        except Exception:
            # In case of any issue, fall back to safe hide
            pass
        
        # Show parent window if available and just hide this dialog
        if self.parent_window:
            try:
                self.parent_window.show()
            except Exception:
                pass
        self.hide()
        event.ignore()
    
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
        """Start the processing workflow."""
        if not self.pdf_path or not isinstance(self.pdf_path, str):
            QMessageBox.critical(self, "Error", "No PDF file selected or invalid path.")
            return
        
        # Create book entry first
        if not self.audiobook_service.create_audiobook(self.book_id, "Processing...", "Unknown Author"):
            QMessageBox.critical(self, "Error", "Failed to create book entry in database.")
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
        """Update progress display."""
        self.progress_widget.set_progress(progress, message)
        self.status_log.add_info(message)
    
    def processing_finished(self):
        """Handle processing completion."""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_log.add_success("Processing completed successfully!")
        self.progress_widget.set_progress(100, "Complete!")
        
        # Show completion message
        QMessageBox.information(self, "🎉 Done", "Audiobook ready! You can now play it from the library.")
        
        # Show parent window if it exists
        if self.parent_window:
            self.parent_window.show()
    
    def processing_error(self, error_message):
        """Handle processing errors."""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_log.add_error(f"Error: {error_message}")
        self.progress_widget.set_status("Processing failed")
        QMessageBox.critical(self, "❌ Processing Error", f"An error occurred:\n{error_message}")
    
    def cancel_processing(self):
        """Cancel processing."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_log.add_warning("Processing cancelled by user")
        self.progress_widget.set_status("Processing cancelled")
        self.progress_widget.set_progress(0)
