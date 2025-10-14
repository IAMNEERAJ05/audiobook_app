# 📚 Audiobook Generator Application v2.0

A modern desktop application that transforms PDF books into immersive audiobooks using AI-powered technology.  
Features a beautiful, intuitive interface with complete book processing, playback, and download capabilities.

---

## ✨ What's New in v2.0

### 🎨 **Modern UI Design**
- Beautiful gradient backgrounds and modern styling
- Custom button components with hover effects
- Real-time progress tracking with detailed logs
- Responsive design with improved user experience

### 🗄️ **SQLite Database Integration**
- Replaced JSON files with robust SQLite database
- Reliable data storage and retrieval
- Processing status tracking for each chapter
- Better performance and data integrity

### 🚀 **Enhanced Processing Pipeline**
- Processes **ALL chapters** (not just first 7)
- Improved chapter detection using AI analysis
- Better error handling and fallback mechanisms
- Threaded processing for smooth UI experience

### 🎵 **Advanced Audio Features**
- High-quality audio stitching with pauses between chapters
- Proper audio cleanup when windows are closed
- Enhanced error handling for audio playback
- Support for MP3 output with proper codec settings

### 📥 **Complete Download System**
- Download entire audiobooks as ZIP packages
- Combined MP3 audio files with chapter pauses
- Complete summary text files
- Book cover images included

---

## 🚀 Key Features

### **📖 Book Processing**
- **PDF Upload & Analysis** - Intelligent chapter detection using Gemini AI
- **AI-Powered Summaries** - Generate engaging chapter summaries
- **Natural Voice Synthesis** - Convert summaries to high-quality audio
- **Complete Chapter Coverage** - Process every chapter in the book

### **🎵 Audiobook Playback**
- **Modern Player Interface** - Clean, intuitive playback controls
- **Chapter Navigation** - Easy switching between chapters
- **Summary Display** - View chapter summaries alongside audio
- **Progress Tracking** - Visual progress indicators

### **📚 Library Management**
- **Book Collection** - View all processed audiobooks
- **Search & Filter** - Find books by title or author
- **Download Audiobooks** - Export complete audiobooks as portable files
- **Database Storage** - Reliable data persistence

### **🎨 Modern Interface**
- **Beautiful Design** - Gradient backgrounds and modern styling
- **Responsive Layout** - Adapts to different window sizes
- **Real-time Feedback** - Live progress updates and status logs
- **Intuitive Navigation** - Easy-to-use interface

---

## 📂 Project Structure

```plaintext
audiobook_app/
│
├── backend/                   # Core processing logic
│   ├── database.py           # SQLite database management
│   ├── extractor.py          # PDF extraction & analysis
│   ├── summarizer.py         # AI-powered summarization
│   ├── tts_engine.py         # Text-to-speech conversion
│   └── manifest_final.py     # Final manifest generation
│
├── gui/                      # User interface components
│   ├── home_window.py        # Main dashboard
│   ├── processing_window.py  # Book processing interface
│   ├── library_window.py     # Audiobook library
│   ├── player_window.py      # Audio playback interface
│   └── components/           # Reusable UI components
│       ├── buttons.py        # Modern button styles
│       ├── progress_bar.py   # Progress tracking
│       └── status_log.py     # Real-time logging
│
├── data/                     # Application data
│   ├── audiobooks.db         # SQLite database
│   └── books/                # Book storage directory
│
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Google API key for Gemini AI (for text summarization)
- FFmpeg (optional, for audio stitching)

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd audiobook_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv xtts-env
   # Windows
   xtts-env\Scripts\activate
   # Linux/Mac
   source xtts-env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Install FFmpeg (optional)**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt install ffmpeg`
   - **Mac**: `brew install ffmpeg`

### Running the Application
```bash
python main.py
```

---

## 📖 Usage Guide

### 1. **Upload & Process a Book**
- Click "📖 Upload & Process Book" on the home screen
- Select a PDF file from your computer
- The app will automatically:
  - Extract text and detect chapters
  - Generate AI-powered summaries
  - Create high-quality audio files
  - Build the final audiobook manifest

### 2. **Browse Your Library**
- Click "📚 Open Library" to view all processed audiobooks
- Search for specific books by title or author
- See processing status and chapter information

### 3. **Listen to Audiobooks**
- Double-click any book in the library to open the player
- Use playback controls (play, pause, resume, stop)
- Navigate between chapters using the chapter list
- Toggle between cover image and chapter summaries

### 4. **Download Audiobooks**
- Select a book in the library
- Click "📥 Download Audiobook"
- Choose download location
- Get a ZIP file containing:
  - Complete MP3 audio file (with chapter pauses)
  - Full summary text file
  - Book cover image

---

## 🔧 Technical Details

### **Database Schema**
- **Books Table**: Metadata, titles, authors, page counts
- **Chapters Table**: Chapter information with processing status
- **Pages Table**: Individual page content storage

### **Processing Pipeline**
1. **PDF Extraction**: Extract text and detect chapters using Gemini AI
2. **Summarization**: Generate engaging summaries for each chapter
3. **Audio Generation**: Convert summaries to high-quality WAV files
4. **Manifest Creation**: Build final audiobook manifest with file paths

### **Audio Processing**
- Uses pyttsx3 for text-to-speech conversion
- Generates WAV files with natural voice synthesis
- Stitches audio files with 2-second pauses between chapters
- Supports MP3 output with libmp3lame codec

### **UI Components**
- **Modern Buttons**: Gradient backgrounds with hover effects
- **Progress Tracking**: Real-time progress bars with status updates
- **Status Logging**: Colored log messages with timestamps
- **Responsive Design**: Adapts to different screen sizes

---

## 🐛 Troubleshooting

### Common Issues

**Import Error: 'None' object has no attribute 'setMedia'**
- ✅ **Fixed**: Enhanced media player initialization and error handling

**Only few chapters being processed**
- ✅ **Fixed**: Now processes ALL chapters with improved detection

**Audio not stopping when window closes**
- ✅ **Fixed**: Proper audio cleanup on window close

**Download only includes first chapter**
- ✅ **Fixed**: Complete audio stitching with all chapters and pauses

**Database connection issues**
- ✅ **Fixed**: Robust SQLite integration with fallback mechanisms

### Getting Help
- Check the processing log for detailed error messages
- Ensure your Google API key is correctly set in the `.env` file
- Verify FFmpeg installation for audio stitching features
- Check that PDF files are not corrupted or password-protected

---

## 🚀 Future Enhancements

- **Voice Selection**: Multiple TTS voices and languages
- **Speed Control**: Adjustable playback speed
- **Bookmarking**: Save listening positions
- **Cloud Sync**: Synchronize audiobooks across devices
- **Batch Processing**: Process multiple books simultaneously
- **Custom Summaries**: User-defined summary styles and lengths

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using Python, PyQt5, and AI technology**
