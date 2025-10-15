# 📚 Audiobook Generator

A modern desktop application that transforms PDF books into immersive audiobooks using AI-powered technology. Built with Python, PyQt5, and Google's Gemini AI, this application features a beautiful, intuitive interface with complete book processing, playback, and library management capabilities.

---

## ✨ Key Features

### 🎨 **Modern UI Design**
- Beautiful gradient backgrounds and modern styling
- Custom button components with hover effects
- Real-time progress tracking with detailed status logs
- Responsive design with smooth animations
- First-run API key setup wizard

### 🗄️ **SQLite Database Architecture**
- Robust three-layer architecture (Data Access, Business Logic, Presentation)
- Repository pattern for clean data management
- Processing status tracking for each chapter
- Reliable data persistence and integrity

### 🚀 **Intelligent Processing Pipeline**
- AI-powered chapter detection using Google Gemini
- Processes **ALL chapters** in the book
- Smart text extraction from PDFs
- Automated summarization with configurable styles
- High-quality text-to-speech conversion
- Threaded processing for responsive UI

### 🎵 **Advanced Audio Features**
- Natural voice synthesis using pyttsx3
- Audio stitching with configurable pauses between chapters
- Proper audio cleanup and resource management
- Support for MP3 and WAV formats
- Chapter-by-chapter playback controls

### 📥 **Complete Download System**
- Export audiobooks as portable ZIP packages
- Combined MP3 audio files with chapter transitions
- Complete summary text files
- Book cover images and metadata

---

## 🎯 Core Capabilities

### **📖 Book Processing**
- Upload PDF files and extract text content
- AI-powered chapter detection using Google Gemini
- Generate engaging summaries for each chapter
- Convert summaries to natural-sounding audio
- Process all chapters with progress tracking

### **🎵 Audiobook Playback**
- Modern player interface with intuitive controls
- Chapter-by-chapter navigation
- View summaries alongside audio playback
- Visual progress indicators
- Proper audio resource management

### **📚 Library Management**
- Browse all processed audiobooks
- Search and filter by title or author
- View book metadata and processing status
- Download complete audiobooks as ZIP files
- SQLite database for reliable storage

---

## 📂 Project Structure

```plaintext
audiobook_app/
│
├── backend/                          # Core processing logic (3-layer architecture)
│   ├── __init__.py                  # Package exports
│   ├── data_access_layer.py         # Database repositories and connections
│   ├── business_logic_layer.py      # Business services and logic
│   ├── config_manager.py            # Configuration and API key management
│   ├── detector.py                  # Chapter detection logic
│   ├── extractor_new.py             # PDF text extraction
│   ├── summarizer_new.py            # AI-powered summarization
│   ├── tts_engine_new.py            # Text-to-speech conversion
│   ├── manifest_final_new.py        # Audiobook manifest generation
│   ├── utils.py                     # Utility functions
│   ├── cleanup_file_storage.py      # File cleanup utilities
│   └── migrate_to_database.py       # Database migration tools
│
├── gui/                             # User interface components
│   ├── __init__.py                  # GUI package initialization
│   ├── home_window.py               # Main dashboard
│   ├── api_key_dialog.py            # API key setup dialog
│   ├── processing_window_new.py     # Book processing interface
│   ├── library_window_new.py        # Audiobook library browser
│   ├── player_window_new.py         # Audio playback interface
│   ├── output_window.py             # Output display window
│   └── components/                  # Reusable UI components
│       ├── buttons.py               # Modern button styles
│       ├── progress_bar.py          # Progress tracking widgets
│       ├── status_log.py            # Real-time logging display
│       ├── audio_controls.py        # Audio control components
│       └── chapter_list.py          # Chapter list widgets
│
├── data/                            # Application data (created at runtime)
│   ├── audiobooks.db                # SQLite database
│   └── books/                       # Book storage directory
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # This documentation

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** - Required for running the application
- **Google Gemini API Key** - For AI-powered chapter detection and summarization
  - Get your free API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **FFmpeg** (Optional) - For advanced audio processing and MP3 conversion

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/IAMNEERAJ05/audiobook_app.git
   cd audiobook_app
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv xtts-env
   xtts-env\Scripts\activate
   
   # Linux/Mac
   python3 -m venv xtts-env
   source xtts-env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   On first run, you'll be prompted to enter your Google Gemini API key through a setup wizard.

### Optional: Install FFmpeg

FFmpeg enables advanced audio features like MP3 conversion and audio stitching.

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **Linux**: `sudo apt install ffmpeg`
- **Mac**: `brew install ffmpeg`

---

## 📖 Usage Guide

### 1. **First-Time Setup**
- Launch the application with `python main.py`
- Enter your Google Gemini API key in the setup wizard
- The key is securely stored in your system's configuration directory
- You can update the API key anytime from the settings menu

### 2. **Upload & Process a Book**
- Click **"📖 Upload & Process Book"** on the home screen
- Select a PDF file from your computer
- Monitor real-time progress through the processing window:
  - Text extraction from PDF
  - AI-powered chapter detection
  - Summary generation for each chapter
  - Audio file creation
  - Manifest finalization
- Processing runs in a background thread for smooth UI experience

### 3. **Browse Your Library**
- Click **"📚 Open Library"** to view all processed audiobooks
- Search for specific books by title or author
- View book metadata, chapter count, and processing status
- Double-click any book to open the audio player

### 4. **Listen to Audiobooks**
- Select a book from the library to open the player
- Use intuitive playback controls:
  - **Play/Pause** - Start or pause audio playback
  - **Stop** - Stop playback and reset position
  - **Chapter Navigation** - Jump between chapters
- View chapter summaries alongside audio
- Track playback progress with visual indicators

### 5. **Download Audiobooks**
- Select a book in the library
- Click **"📥 Download Audiobook"**
- Choose your download location
- Receive a ZIP file containing:
  - Combined MP3 audio file with chapter transitions
  - Complete summary text file
  - Book metadata and cover image

---

## 🔧 Technical Architecture

### **Three-Layer Architecture**

#### 1. **Data Access Layer** (`data_access_layer.py`)
- **DatabaseConnection**: Singleton pattern for database management
- **Repository Pattern**: Clean separation of data access logic
  - `BookRepository`: Book CRUD operations
  - `ChapterRepository`: Chapter management
  - `PageRepository`: Page content storage
  - `ProcessingLogRepository`: Processing history tracking
- **Connection Pooling**: Efficient database resource management

#### 2. **Business Logic Layer** (`business_logic_layer.py`)
- **BookService**: Book lifecycle management
- **ChapterService**: Chapter processing coordination
- **PageService**: Page content handling
- **ProcessingService**: Processing workflow orchestration
- **AudiobookService**: Audiobook generation and export

#### 3. **Presentation Layer** (`gui/`)
- **PyQt5-based UI**: Modern, responsive interface
- **Component-based design**: Reusable UI elements
- **Threaded processing**: Non-blocking operations
- **Signal/Slot architecture**: Event-driven communication

### **Database Schema**
```sql
Books: id, title, author, total_pages, total_chapters, created_at, updated_at
Chapters: id, book_id, chapter_number, title, summary, audio_path, status
Pages: id, book_id, page_number, content
ProcessingLogs: id, book_id, stage, status, message, timestamp
```

### **Processing Pipeline**
1. **PDF Extraction** (`extractor_new.py`)
   - Text extraction using PyMuPDF
   - Page-by-page content parsing
   
2. **Chapter Detection** (`detector.py`)
   - AI-powered chapter identification using Google Gemini
   - Pattern matching and heuristics
   
3. **Summarization** (`summarizer_new.py`)
   - Chapter-wise summary generation
   - Configurable summary styles and lengths
   
4. **Audio Generation** (`tts_engine_new.py`)
   - Text-to-speech using pyttsx3
   - WAV file generation with quality settings
   
5. **Manifest Creation** (`manifest_final_new.py`)
   - Final audiobook package assembly
   - Metadata and file path management

### **Technology Stack**
- **Frontend**: PyQt5 for desktop UI
- **Backend**: Python 3.8+ with SQLite
- **AI**: Google Generative AI (Gemini)
- **PDF Processing**: PyMuPDF (fitz)
- **Audio**: pyttsx3, pydub, soundfile
- **Database**: SQLite with repository pattern

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**API Key Not Working**
- Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Update the API key through the settings menu (⚙️ icon on home screen)
- Check that the key has proper permissions for Gemini API

**PDF Processing Fails**
- Ensure PDF is not password-protected or corrupted
- Try PDFs with clear text (not scanned images)
- Check that the PDF has readable text content
- Verify sufficient disk space for processing

**Audio Playback Issues**
- Ensure audio files were generated successfully
- Check system audio settings and volume
- Verify pyttsx3 is properly installed
- Try reprocessing the book if audio files are missing

**Database Errors**
- Check write permissions in the application directory
- Ensure `data/` folder exists and is writable
- Try deleting `audiobooks.db` to reset (will lose library data)

**Application Won't Start**
- Verify Python 3.8+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Look for error messages in the console
- Try running in a fresh virtual environment

### Debug Mode
Enable detailed logging by checking the status log window during processing for:
- PDF extraction progress
- Chapter detection results
- Summarization status
- Audio generation progress
- Error messages and stack traces

---

## 🚀 Future Enhancements

### Planned Features
- [ ] **Multiple TTS Engines**: Support for different voice synthesis engines
- [ ] **Voice Customization**: Select from multiple voices, accents, and languages
- [ ] **Playback Speed Control**: Adjustable audio playback speed
- [ ] **Bookmarking System**: Save and resume listening positions
- [ ] **Batch Processing**: Process multiple books simultaneously
- [ ] **Custom Summary Styles**: User-defined summary lengths and formats
- [ ] **Export Formats**: Support for M4B, OGG, and other audiobook formats
- [ ] **Cloud Integration**: Optional cloud storage for audiobooks
- [ ] **Mobile Companion**: Sync with mobile devices
- [ ] **Advanced Chapter Detection**: Improved AI models for better accuracy

### Contributions Welcome
Have ideas for new features? Found a bug? Contributions are welcome!

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

**IAMNEERAJ05**
- GitHub: [@IAMNEERAJ05](https://github.com/IAMNEERAJ05)

---

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful text analysis and summarization
- **PyQt5** for the robust desktop UI framework
- **PyMuPDF** for reliable PDF processing
- **pyttsx3** for text-to-speech capabilities

---

**Built with ❤️ using Python, PyQt5, and AI technology**
