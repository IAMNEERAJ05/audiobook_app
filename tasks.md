# 📘 Audiobook Generator — MVP Task Plan
*(Goal: process a general book, extract metadata & chapters, generate summaries and audio for first 5–7 chapters.)*

---

## 🧱 Phase 0 — Project Setup

- [ ] **Create project structure**

audiobook_app/
├── backend/
│ ├── extractor.py
│ ├── detector.py
│ ├── summarizer.py
│ ├── tts_engine.py
│ ├── utils.py
├── data/
│ ├── uploads/
│ └── books/
├── .env
├── tasks.md
├── requirements.txt
└── main.py

- [ ] Add `.env` file with:

GOOGLE_API_KEY=your_gemini_api_key_here

- [ ] Create `requirements.txt`:

google-generativeai
PyMuPDF
python-dotenv
tqdm
difflib
pyttsx3
soundfile
numpy
pydub

---

## 📄 Phase 1 — Book Extraction & Metadata

### 1.1 Extract book pages
- [ ] Implement `extractor.py`:
- Load PDF using **PyMuPDF** (`fitz`).
- Extract per-page text.
- Remove repeated headers/footers (if detected).
- Save to: `data/books/{book_id}/pages.json`.
- Return `pages` list + `page_count`.

### 1.2 Extract metadata + TOC using Gemini
- [ ] Use **Gemini 2.5 Flash**:
- Input: first 20–30 pages concatenated.
- Output JSON:
  ```json
  {
    "title": "...",
    "author": "...",
    "genre": "...",
    "year": "...",
    "chapters": [
      {"title": "Chapter 1", "start_page": 1, "end_page": 9},
      ...
    ]
  }
  ```
- [ ] Parse Gemini output (robust JSON parser).
- [ ] Store raw Gemini output → `meta_raw.json`.
- [ ] Store structured metadata → `manifest.json`.

---

## 🔍 Phase 2 — Chapter Detection & Validation

### 2.1 Validate TOC
- [ ] Compare TOC page numbers vs extracted page count.
- [ ] If mismatch:
- Fuzzy match TOC titles to pages using `difflib.SequenceMatcher`.
- Adjust offset automatically (roman vs numeric pagination).

### 2.2 Heuristic fallback (if TOC missing)
- [ ] Detect headings on pages:
- Patterns: `Chapter`, `Prologue`, `Epilogue`, uppercase lines, roman numerals.
- Collect candidate start pages.
- [ ] Sort and build chapters list:

chapters = [
{"index": 1, "title": "Prologue", "start_page": 1, "end_page": 7},
{"index": 2, "title": "Chapter 1", "start_page": 8, "end_page": 15},
]

- [ ] Save detected chapters to `manifest.json`.

### 2.3 Coverage sanity check
- [ ] Ensure sum of chapter pages ≥ 80% of total book pages.
- [ ] If coverage < 80%, flag for manual adjustment.

---

## 🧠 Phase 3 — Chapter Summarization

### 3.1 Summarize first 5–7 chapters
- [ ] For each chapter (1–7):
- Extract text via `get_chapter_text(start_page, end_page)`.
- If text ≤ 12k chars → single-pass summary.
- Else → chunk by sentences (~5k chars) and combine.

### 3.2 Prompt (Gemini Flash)
```text
You are a narrator. Summarize the chapter '{chapter_title}'
in a descriptive, emotional style suitable for audiobook narration.
Keep it 150–220 words.
Return only JSON:
{
"chapter_title": "...",
"summary": "...",
"tone": "emotional|calm|dramatic"
}
```

3.3 Store results

 Write summaries to:

data/books/{book_id}/chapters/chapter_001.json

data/books/{book_id}/manifest.json (append summary reference)

3.4 Validation

 Verify summaries length between 100–250 words.

 Spot check content relevance (print first 100 chars).

🔊 Phase 4 — Audio Generation (TTS)
4.1 Choose TTS engine (local MVP)

Options:

✅ pyttsx3 (offline, consistent)

gTTS (Google free web API)

Gemini 2.5 TTS (if available via model "models/gemini-2.5-flash-preview-tts")

4.2 Implement tts_engine.py

 Function: generate_audio(summary_text, output_path, voice='female')

Input: summary text.

Output: .wav or .mp3 in data/books/{book_id}/audio/.

4.3 Generate for first 5–7 chapters

 Iterate summaries → call TTS → save audio.

 Output paths like:

data/books/{book_id}/audio/chapter_001.mp3
data/books/{book_id}/audio/chapter_002.mp3

4.4 Verify audio files

 Check duration (≥ 60s for each).

 Play sample snippet for human QA.

🧾 Phase 5 — Manifest & Output

 Combine everything into a final manifest:

{
  "book_id": "...",
  "title": "...",
  "author": "...",
  "page_count": 300,
  "chapters": [
    {
      "index": 1,
      "title": "Prologue",
      "start_page": 1,
      "end_page": 8,
      "summary_path": "chapters/chapter_001.json",
      "audio_path": "audio/chapter_001.mp3"
    },
    ...
  ]
}


 Save as data/books/{book_id}/manifest_final.json.
