# home_window.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QLabel, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPixmap, QPalette, QLinearGradient, QPainter
import sys

# Import windows
from gui.processing_window import ProcessingWindow
from gui.library_window import LibraryWindow

# Import modern components
from gui.components.buttons import ActionButton, ModernButton

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📚 Audiobook Generator")
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header section
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)
        
        # Add spacer
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Action buttons section
        buttons_frame = self._create_buttons_section()
        main_layout.addWidget(buttons_frame)
        
        # Add spacer
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Footer section
        footer_frame = self._create_footer()
        main_layout.addWidget(footer_frame)
        
        self.setLayout(main_layout)
        
        # Apply modern styling
        self._apply_modern_styling()
    
    def _create_header(self):
        """Create the header section with title and description."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Main title
        title_label = QLabel("📚 Audiobook Generator")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                background: transparent;
                border: none;
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Transform your PDF books into immersive audiobooks")
        subtitle_label.setFont(QFont("Segoe UI", 14))
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #7F8C8D;
                background: transparent;
                border: none;
                padding: 5px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Feature highlights
        features_text = "✨ AI-powered summaries • 🎵 Natural voice synthesis • 📱 Download & enjoy anywhere"
        features_label = QLabel(features_text)
        features_label.setFont(QFont("Segoe UI", 11))
        features_label.setStyleSheet("""
            QLabel {
                color: #95A5A6;
                background: transparent;
                border: none;
                padding: 10px;
            }
        """)
        features_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(features_label)
        
        frame.setLayout(layout)
        return frame
    
    def _create_buttons_section(self):
        """Create the action buttons section."""
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
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Section title
        section_title = QLabel("Choose an Action")
        section_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        section_title.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                background: transparent;
                border: none;
                padding: 5px;
            }
        """)
        section_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(section_title)
        
        # Upload Book Button
        self.upload_btn = ActionButton("📖 Upload & Process Book", "primary")
        self.upload_btn.clicked.connect(self.upload_book)
        layout.addWidget(self.upload_btn)
        
        # Library Button
        self.library_btn = ActionButton("📚 Open Library", "info")
        self.library_btn.clicked.connect(self.open_library)
        layout.addWidget(self.library_btn)
        
        frame.setLayout(layout)
        return frame
    
    def _create_footer(self):
        """Create the footer section with version info."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Version info
        version_label = QLabel("Version 2.0 • Powered by AI • Built with ❤️")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setStyleSheet("""
            QLabel {
                color: #BDC3C7;
                background: transparent;
                border: none;
                padding: 5px;
            }
        """)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        frame.setLayout(layout)
        return frame
    
    def _apply_modern_styling(self):
        """Apply modern styling to the main window."""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #F8F9FA, stop: 1 #E9ECEF);
            }
        """)

    # Mock actions
    def upload_book(self):
        from PyQt5.QtWidgets import QFileDialog
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Select PDF Book", "", "PDF Files (*.pdf)")
        if not pdf_path:
            return
        QMessageBox.information(self, "Upload", f"Book selected: {pdf_path}")
        try:
            self.processing_window = ProcessingWindow(pdf_path)
        except TypeError:
            self.processing_window = ProcessingWindow()
        self.processing_window.show()

    def open_library(self):
        self.library_window = LibraryWindow()
        self.library_window.show()



# Run standalone for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    home = HomeWindow()
    home.show()
    sys.exit(app.exec_())
