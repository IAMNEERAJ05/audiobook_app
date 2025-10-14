# output_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox
)

# Mock chapters for display
MOCK_CHAPTERS = [f"Chapter {i}" for i in range(1, 6)]

class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Export Audiobook")
        self.setGeometry(200, 200, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("Ready to export audiobook")
        layout.addWidget(self.status_label)

        # Mock chapter list
        self.chapter_list = QListWidget()
        for ch in MOCK_CHAPTERS:
            self.chapter_list.addItem(QListWidgetItem(ch))
        layout.addWidget(self.chapter_list)

        # Download button
        self.download_btn = QPushButton("Download Audiobook")
        self.download_btn.clicked.connect(self.download_audiobook)
        layout.addWidget(self.download_btn)

        self.setLayout(layout)

    def download_audiobook(self):
        # Simulate export
        QMessageBox.information(self, "Download", "Audiobook exported successfully!")
        self.status_label.setText("Export complete!")
