# player_window_redesign.py

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt

class PlayerWindow(QWidget):
    def __init__(self, book_id=None, manifest=None):
        super().__init__()
        self.book_id = book_id
        self.manifest = manifest
        self.setWindowTitle(f"Player - {manifest.get('title', book_id)}" if manifest else "Player")
        self.setGeometry(200, 150, 700, 450)
        self.current_chapter = 0
        self.show_cover = True
        self.chapters = manifest.get('chapters', []) if manifest else []
        self.media_player = None  # Initialize media player
        
        if not self.chapters:
            QMessageBox.warning(self, "No Chapters", f"No chapters found for book '{book_id}'. Please check the manifest or processing steps.")
            self.close()
            return
        if len(self.chapters) > 0 and not any('title' in ch for ch in self.chapters):
            QMessageBox.critical(self, "Chapter Data Error", "Chapters found but missing 'title' field. Check manifest_final.json format.")
        self.init_ui()
    
    def closeEvent(self, event):
        """Override close event to stop audio when window is closed"""
        self.stop_audio()
        event.accept()
    
    def stop_audio(self):
        """Stop audio playback and cleanup media player"""
        if hasattr(self, 'media_player') and self.media_player is not None:
            try:
                self.media_player.stop()
                self.media_player.setMedia(None)  # Clear media
            except Exception as e:
                print(f"Error stopping audio: {e}")
            finally:
                self.media_player = None

    def init_ui(self):
        main_layout = QHBoxLayout()
        # Left Panel: Chapter Playlist
        self.playlist_frame = QFrame()
        self.playlist_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 8px; }")
        playlist_layout = QVBoxLayout()
        playlist_layout.addWidget(QLabel("Chapters:"))
        self.chapter_list = QListWidget()
        for ch in self.chapters:
            item = QListWidgetItem(ch['title'])
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
        book_id_str = str(self.book_id) if self.book_id is not None else ""
        cover_path = os.path.join(os.path.dirname(__file__), "..", "data", "books", book_id_str, "cover.png")
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            self.display_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.display_label.setText("Cover Image (mock)")
            self.display_label.setFont(QFont("Arial", 12))
            self.display_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    background-color: #fff;
                    padding: 10px;
                }
            """)
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

    def prev_chapter(self):
        if self.chapters and self.current_chapter > 0:
            self.current_chapter -= 1
            self.chapter_list.setCurrentRow(self.current_chapter)
            self.change_chapter(self.chapter_list.currentItem())
            self.stop()

    def next_chapter(self):
        if self.chapters and self.current_chapter < len(self.chapters) - 1:
            self.current_chapter += 1
            self.chapter_list.setCurrentRow(self.current_chapter)
            self.change_chapter(self.chapter_list.currentItem())
            self.stop()

    def play(self):
        if self.chapters:
            chapter = self.chapters[self.current_chapter]
            self.status_label.setText(f"Playing {chapter['title']}")
            audio_path_val = chapter.get('audio_path')
            book_id_str = str(self.book_id) if self.book_id is not None else ""
            audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "books", book_id_str, audio_path_val)) if audio_path_val else ""
            
            if audio_path and os.path.exists(audio_path):
                try:
                    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
                    from PyQt5.QtCore import QUrl
                    
                    # Initialize media player if not exists or is None
                    if not hasattr(self, 'media_player') or self.media_player is None:
                        self.media_player = QMediaPlayer()
                    
                    # Verify media player is properly initialized
                    if self.media_player is not None:
                        # Create media content and set it
                        media_content = QMediaContent(QUrl.fromLocalFile(audio_path))
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
                self.status_label.setText(f"Audio file not found: {audio_path_val or 'No path specified'}")
        else:
            self.status_label.setText("No chapters available to play.")

    def pause(self):
        if hasattr(self, 'media_player') and self.media_player is not None:
            self.media_player.pause()
            self.status_label.setText("Paused")
        else:
            self.status_label.setText("No audio to pause")

    def resume(self):
        if hasattr(self, 'media_player') and self.media_player is not None:
            self.media_player.play()
            self.status_label.setText("Resumed")
        else:
            self.status_label.setText("No audio to resume")

    def stop(self):
        self.stop_audio()
        self.status_label.setText("Stopped")

    def change_chapter(self, item):
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
        
        # Load summary
        summary_path_val = ch.get('summary_path')
        book_id_str = str(self.book_id) if self.book_id is not None else ""
        summary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "books", book_id_str, summary_path_val)) if summary_path_val else ""
        
        if summary_path and os.path.exists(summary_path):
            try:
                with open(summary_path, encoding="utf-8") as f:
                    summary_json = json.load(f)
                summary_text = summary_json.get('summary', 'No summary available.')
                if not summary_text.strip():
                    summary_text = "Summary is empty."
            except Exception as e:
                summary_text = f"Error loading summary from {summary_path}: {e}"
        else:
            summary_text = f"Summary file not found: {summary_path_val or 'No path specified'}"
        
        self.current_summary = summary_text
        self.summary_textedit.setPlainText(self.current_summary)
        self.summary_textedit.show()
        self.display_label.hide()

    def toggle_display(self):
        if self.show_cover:
            self.display_label.hide()
            self.summary_textedit.show()
            self.summary_textedit.setPlainText(getattr(self, 'current_summary', 'No summary available.'))
        else:
            self.summary_textedit.hide()
            self.display_label.show()
            book_id_str = str(self.book_id) if self.book_id is not None else ""
            cover_path = os.path.join(os.path.dirname(__file__), "..", "data", "books", book_id_str, "cover.png")
            if os.path.exists(cover_path):
                pixmap = QPixmap(cover_path)
                self.display_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.display_label.setText("Cover Image (mock)")
        self.show_cover = not self.show_cover
