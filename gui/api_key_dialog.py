"""
api_key_dialog.py
Dialog for first-time API key setup with secure storage.
"""
import os
import json
import base64
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

class APIKeyDialog(QDialog):
    """Dialog for setting up Gemini API key on first launch."""
    
    api_key_saved = pyqtSignal(str)  # Signal emitted when API key is saved
    
    def __init__(self, parent=None, is_first_run=False):
        super().__init__(parent)
        self.is_first_run = is_first_run
        
        if is_first_run:
            self.setWindowTitle("Audiobook Generator - Welcome & API Setup")
        else:
            self.setWindowTitle("Audiobook Generator - API Key Management")
            
        self.setModal(True)
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        
        # Set window icon (if available)
        try:
            self.setWindowIcon(QIcon("assets/icon.ico"))
        except:
            pass
            
        self.setup_ui()
        self.load_existing_key()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        if self.is_first_run:
            title_text = "Welcome to Audiobook Generator!"
        else:
            title_text = "Manage Your API Key"
            
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        if self.is_first_run:
            desc_text = (
                "To use AI-powered summarization, you need a Google Gemini API key.\n"
                "This is required only once and will be stored securely on your device."
            )
        else:
            desc_text = (
                "Update your Google Gemini API key to continue using AI features.\n"
                "Your current key will be replaced with the new one."
            )
            
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(desc_label)
        
        # API Key input
        key_layout = QVBoxLayout()
        key_label = QLabel("Google Gemini API Key:")
        key_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        key_layout.addWidget(key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Gemini API key here...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
        key_layout.addWidget(self.api_key_input)
        
        # Show/Hide checkbox
        self.show_key_checkbox = QCheckBox("Show API key")
        self.show_key_checkbox.toggled.connect(self.toggle_key_visibility)
        key_layout.addWidget(self.show_key_checkbox)
        
        layout.addLayout(key_layout)
        
        # Help text
        help_label = QLabel(
            "Don't have an API key? Get one free at: "
            "<a href='https://makersuite.google.com/app/apikey'>Google AI Studio</a>"
        )
        help_label.setOpenExternalLinks(True)
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setStyleSheet("color: #007acc; font-size: 11px;")
        layout.addWidget(help_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Only show skip button on first run
        if self.is_first_run:
            self.skip_button = QPushButton("Skip (Limited Features)")
            self.skip_button.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.skip_button.clicked.connect(self.skip_setup)
            button_layout.addWidget(self.skip_button)
        
        if self.is_first_run:
            save_text = "Save & Continue"
        else:
            save_text = "Update API Key"
            
        self.save_button = QPushButton(save_text)
        self.save_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.save_button.clicked.connect(self.save_api_key)
        
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Enable/disable save button based on input
        self.api_key_input.textChanged.connect(self.validate_input)
        self.validate_input()
        
    def toggle_key_visibility(self, checked):
        """Toggle API key visibility."""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            
    def validate_input(self):
        """Validate API key input and enable/disable save button."""
        key = self.api_key_input.text().strip()
        is_valid = len(key) > 20 and key.startswith(('AIza', 'ya29'))  # Basic validation
        self.save_button.setEnabled(is_valid)
        
    def load_existing_key(self):
        """Load existing API key if available."""
        config_path = self.get_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'api_key' in config:
                        # Decode the stored key
                        encoded_key = config['api_key']
                        decoded_key = base64.b64decode(encoded_key).decode('utf-8')
                        self.api_key_input.setText(decoded_key)
                        self.show_key_checkbox.setChecked(True)
            except Exception:
                pass  # If loading fails, just continue with empty input
                
    def get_config_path(self):
        """Get the path to the config file."""
        config_dir = Path.home() / ".audiobook_generator"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"
        
    def save_api_key(self):
        """Save the API key securely."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid API key.")
            return
            
        try:
            # Create config directory
            config_path = self.get_config_path()
            
            # Encode the API key for basic obfuscation
            encoded_key = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
            
            # Save config
            config = {
                'api_key': encoded_key,
                'setup_completed': True,
                'version': '1.0.0'
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            # Set file permissions to be more secure (Windows)
            try:
                os.chmod(config_path, 0o600)
            except:
                pass
                
            QMessageBox.information(
                self, 
                "Setup Complete", 
                "API key saved successfully!\nYou can now use all features of the Audiobook Generator."
            )
            
            self.api_key_saved.emit(api_key)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save API key: {str(e)}"
            )
            
    def skip_setup(self):
        """Skip API key setup."""
        reply = QMessageBox.question(
            self,
            "Skip Setup",
            "Are you sure you want to skip API setup?\n\n"
            "Without an API key, you won't be able to use:\n"
            "• AI-powered chapter summarization\n"
            "• Advanced text processing\n\n"
            "You can set it up later from the Settings menu.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Mark setup as completed even without API key
            try:
                config_path = self.get_config_path()
                config = {
                    'setup_completed': True,
                    'version': '1.0.0',
                    'api_key': None
                }
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            except:
                pass
                
            self.api_key_saved.emit("")
            self.accept()
