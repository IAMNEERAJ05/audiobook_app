"""
Player Window - Refactored to use database-centric architecture
Uses the new business logic layer for all operations.
"""

import os
import json
import tempfile
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt

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

class PlayerWindow(QWidget):
    """Player window using new architecture."""
    
    def __init__(self, book_id=None, manifest=None):
        super().__init__()
        self.book_id = book_id
        self.manifest = manifest
        self.setWindowTitle(f"Player - {manifest.get('title', book_id)}" if manifest else "Player")
        self.setGeometry(200, 150, 700, 450)
        self.current_chapter = 0
        self.show_cover = True
        self.chapters = manifest.get('chapters', []) if manifest else []
        self.media_player = None
        self.temp_audio_files = []  # Track temporary audio files
        
        # Initialize audiobook service
        self.audiobook_service = AudiobookService(repository_factory)
        
        if not self.chapters:
            QMessageBox.warning(self, "No Chapters", f"No chapters found for book '{book_id}'. Please check the manifest or processing steps.")
            self.close()
            return
        
        self.init_ui()
    
    def closeEvent(self, event):
        """Override close event to stop audio and cleanup temp files."""
        self.stop_audio()
        self._cleanup_temp_files()
        event.accept()
    
    def _cleanup_temp_files(self):
        """Clean up temporary audio files."""
        for temp_file in self.temp_audio_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Error cleaning up temp file {temp_file}: {e}")
        self.temp_audio_files.clear()
    
    def stop_audio(self):
        """Stop audio playback and cleanup media player."""
        if hasattr(self, 'media_player') and self.media_player is not None:
            try:
                self.media_player.stop()
                self.media_player.setMedia(None)  # Clear media
            except Exception as e:
                print(f"Error stopping audio: {e}")
            finally:
                self.media_player = None
    
    def init_ui(self):
        """Initialize the UI."""
        main_layout = QHBoxLayout()
        
        # Left Panel: Chapter Playlist
        self.playlist_frame = QFrame()
        self.playlist_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 8px; }")
        playlist_layout = QVBoxLayout()
        playlist_layout.addWidget(QLabel("Chapters:"))
        self.chapter_list = QListWidget()
        
        for ch in self.chapters:
            # Show processing status
            status = ch.get('processing_status', 'pending')
            has_audio = ch.get('has_audio', False)
            status_icon = "✅" if status == 'completed' and has_audio else "🔄" if status == 'in_progress' else "⏳"
            
            item_text = f"{status_icon} {ch['title']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, ch)
            self.chapter_list.addItem(item)
        
        self.chapter_list.itemClicked.connect(self.change_chapter)
        playlist_layout.addWidget(self.chapter_list)
        self.playlist_frame.setLayout(playlist_layout)
        main_layout.addWidget(self.playlist_frame, 1)

        # Right Panel: Display + Controls
        right_layout = QVBoxLayout()
        
        # Status Label
        self.status_label = QLabel("Stopped")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(self.status_label)
        
        # Display Area (cover)
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_cover_image()
        right_layout.addWidget(self.display_label, 1)
        
        # Display Area (summary)
        self.summary_textedit = QTextEdit()
        self.summary_textedit.setReadOnly(True)
        self.summary_textedit.setFont(QFont("Arial", 12))
        self.summary_textedit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: #fff;
                padding: 10px;
            }
        """)
        self.summary_textedit.hide()
        right_layout.addWidget(self.summary_textedit, 1)
        
        # Toggle Cover/Summary Button
        self.toggle_btn = QPushButton("Toggle Cover/Summary")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #FFC700;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_display)
        right_layout.addWidget(self.toggle_btn)
        
        # Audio & Navigation Controls
        control_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⏮ Previous")
        self.next_btn = QPushButton("⏭ Next")
        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")
        self.resume_btn = QPushButton("⏵ Resume")
        self.stop_btn = QPushButton("■ Stop")
        
        for btn in [self.prev_btn, self.next_btn, self.play_btn, self.pause_btn, self.resume_btn, self.stop_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            control_layout.addWidget(btn)
        
        self.prev_btn.clicked.connect(self.prev_chapter)
        self.next_btn.clicked.connect(self.next_chapter)
        self.play_btn.clicked.connect(self.play)
        self.pause_btn.clicked.connect(self.pause)
        self.resume_btn.clicked.connect(self.resume)
        self.stop_btn.clicked.connect(self.stop)
        right_layout.addLayout(control_layout)
        
        main_layout.addLayout(right_layout, 3)
        self.setLayout(main_layout)
    
    def _load_cover_image(self):
        """Load cover image from database."""
        try:
            cover_data, cover_type = self.audiobook_service.book_service.get_book_cover(self.book_id)
            if cover_data:
                # Create QPixmap from binary data
                pixmap = QPixmap()
                pixmap.loadFromData(cover_data)
                self.display_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.display_label.setText("Cover Image (not available)")
                self.display_label.setFont(QFont("Arial", 12))
                self.display_label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #ccc;
                        border-radius: 8px;
                        background-color: #fff;
                        padding: 10px;
                    }
                """)
        except Exception as e:
            print(f"Error loading cover image: {e}")
            self.display_label.setText("Cover Image (error loading)")
    
    def prev_chapter(self):
        """Go to previous chapter."""
        if self.chapters and self.current_chapter > 0:
            self.current_chapter -= 1
            self.chapter_list.setCurrentRow(self.current_chapter)
            self.change_chapter(self.chapter_list.currentItem())
            self.stop()

    def next_chapter(self):
        """Go to next chapter."""
        if self.chapters and self.current_chapter < len(self.chapters) - 1:
            self.current_chapter += 1
            self.chapter_list.setCurrentRow(self.current_chapter)
            self.change_chapter(self.chapter_list.currentItem())
            self.stop()

    def play(self):
        """Play current chapter audio."""
        if self.chapters:
            chapter = self.chapters[self.current_chapter]
            self.status_label.setText(f"Playing {chapter['title']}")
            
            # Get audio data from database
            audio_data, audio_format = self.audiobook_service.chapter_service.get_chapter_audio(
                self.book_id, chapter.get('index', self.current_chapter)
            )
            
            if audio_data:
                try:
                    # Create temporary file for audio
                    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                    temp_file.write(audio_data)
                    temp_file.close()
                    self.temp_audio_files.append(temp_file.name)
                    
                    # Play audio
                    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
                    from PyQt5.QtCore import QUrl
                    
                    # Initialize media player if not exists
                    if not hasattr(self, 'media_player') or self.media_player is None:
                        self.media_player = QMediaPlayer()
                    
                    if self.media_player is not None:
                        media_content = QMediaContent(QUrl.fromLocalFile(temp_file.name))
                        self.media_player.setMedia(media_content)
                        self.media_player.play()
                        self.status_label.setText(f"Playing {chapter['title']}")
                    else:
                        self.status_label.setText("Failed to initialize audio player")
                        
                except ImportError:
                    self.status_label.setText("Audio playback not available - PyQt5 multimedia not installed")
                except Exception as e:
                    self.status_label.setText(f"Audio playback error: {e}")
            else:
                self.status_label.setText(f"No audio available for {chapter['title']}")
        else:
            self.status_label.setText("No chapters available to play.")

    def pause(self):
        """Pause audio playback."""
        if hasattr(self, 'media_player') and self.media_player is not None:
            self.media_player.pause()
            self.status_label.setText("Paused")
        else:
            self.status_label.setText("No audio to pause")

    def resume(self):
        """Resume audio playback."""
        if hasattr(self, 'media_player') and self.media_player is not None:
            self.media_player.play()
            self.status_label.setText("Resumed")
        else:
            self.status_label.setText("No audio to resume")

    def stop(self):
        """Stop audio playback."""
        self.stop_audio()
        self.status_label.setText("Stopped")

    def change_chapter(self, item):
        """Change to selected chapter."""
        if item is None:
            return
            
        ch = item.data(Qt.ItemDataRole.UserRole)
        if ch is None:
            self.status_label.setText("Error: Chapter data not found.")
            self.current_summary = "No summary available."
            self.summary_textedit.setPlainText(self.current_summary)
            self.summary_textedit.show()
            self.display_label.hide()
            return
        
        try:
            self.current_chapter = self.chapters.index(ch)
        except ValueError:
            self.status_label.setText("Error: Chapter not found in list.")
            self.current_summary = "No summary available."
            self.summary_textedit.setPlainText(self.current_summary)
            self.summary_textedit.show()
            self.display_label.hide()
            return
        
        self.status_label.setText(f"Selected {ch.get('title', 'Unknown')}")
        
        # Load summary from database
        try:
            # Fetch chapter summary from DB by chapter_index
            target_index = ch.get('index', self.current_chapter)
            chapters = self.audiobook_service.chapter_service.get_chapters(self.book_id)
            matched = next((c for c in chapters if c.get('chapter_index') == target_index), None)
            summary_text = (matched or {}).get('summary_text', '') if matched else ''
            if not isinstance(summary_text, str) or not summary_text.strip():
                summary_text = "No summary available for this chapter."
        except Exception as e:
            summary_text = f"Error loading summary: {e}"
        
        self.current_summary = summary_text
        self.summary_textedit.setPlainText(self.current_summary)
        self.summary_textedit.show()
        self.display_label.hide()

    def toggle_display(self):
        """Toggle between cover and summary display."""
        if self.show_cover:
            self.display_label.hide()
            self.summary_textedit.show()
            self.summary_textedit.setPlainText(getattr(self, 'current_summary', 'No summary available.'))
        else:
            self.summary_textedit.hide()
            self.display_label.show()
            self._load_cover_image()
        self.show_cover = not self.show_cover
