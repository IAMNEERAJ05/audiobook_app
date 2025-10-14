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
from gui.api_key_dialog import APIKeyDialog

# Import modern components
from gui.components.buttons import ActionButton, ModernButton
from backend.config_manager import ConfigManager

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📚 Audiobook Generator")
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(500, 400)
        self.config_manager = ConfigManager()
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Top bar with API key button
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
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
    
    def _create_top_bar(self):
        """Create the top bar with API key management button."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Left spacer
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # API Key Status and Button
        api_status_layout = QHBoxLayout()
        api_status_layout.setSpacing(10)
        
        # API Key Status Indicator
        self.api_status_label = QLabel()
        self.api_status_label.setFont(QFont("Segoe UI", 9))
        self._update_api_status()
        api_status_layout.addWidget(self.api_status_label)
        
        # API Key Management Button
        self.api_key_btn = QPushButton("🔑 API Key")
        self.api_key_btn.setFont(QFont("Segoe UI", 9))
        self.api_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        self.api_key_btn.clicked.connect(self.manage_api_key)
        api_status_layout.addWidget(self.api_key_btn)
        
        layout.addLayout(api_status_layout)
        
        frame.setLayout(layout)
        return frame
    
    def _update_api_status(self):
        """Update the API key status indicator."""
        has_key = self.config_manager.has_api_key()
        if has_key:
            self.api_status_label.setText("✅ API Key: Configured")
            self.api_status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        else:
            self.api_status_label.setText("⚠️ API Key: Not Set")
            self.api_status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
    
    def manage_api_key(self):
        """Open API key management dialog."""
        api_dialog = APIKeyDialog(self)
        
        def on_api_key_saved(api_key):
            if api_key:
                self.config_manager.set_api_key(api_key)
                # Set environment variable for immediate use
                import os
                os.environ['GOOGLE_API_KEY'] = api_key
                QMessageBox.information(
                    self, 
                    "API Key Updated", 
                    "API key has been saved successfully!\nYou can now use all AI features."
                )
            else:
                # User skipped, but mark setup as completed
                self.config_manager.mark_setup_completed()
                QMessageBox.information(
                    self,
                    "Setup Complete",
                    "Setup completed without API key.\nYou can add it later using this button."
                )
            self._update_api_status()
                
        api_dialog.api_key_saved.connect(on_api_key_saved)
        api_dialog.exec_()
    
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
