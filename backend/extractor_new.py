"""
PDF Extractor - Refactored to use database-centric architecture
Extracts pages and text from PDF books using the new business logic layer.
No more file-based storage - everything goes to database.
"""

try:
    import fitz  # PyMuPDF
except ImportError:
    import PyMuPDF as fitz
import os
import json
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv
import google.generativeai as genai

try:
    from .business_logic_layer import AudiobookService
    from .data_access_layer import repository_factory
except ImportError:
    from business_logic_layer import AudiobookService
    from data_access_layer import repository_factory

class PDFExtractor:
    """PDF extraction service using the new architecture."""
    
    def __init__(self):
        self.audiobook_service = AudiobookService(repository_factory)
    
    def extract_pages(self, pdf_path: str) -> list:
        """Extract pages from PDF with header/footer removal."""
        doc = fitz.open(pdf_path)
        pages = []
        header_counts = Counter()
        footer_counts = Counter()
        
        # First pass: collect headers/footers
        for i in range(doc.page_count):
            page = doc.load_page(i)
            try:
                lines = page.get_text("text").splitlines()
            except Exception:
                lines = page.getText().splitlines() if hasattr(page, 'getText') else []
            
            if len(lines) > 2:
                header_counts[lines[0].strip()] += 1
                footer_counts[lines[-1].strip()] += 1
        
        # Detect most common header/footer
        header = header_counts.most_common(1)[0][0] if header_counts else None
        footer = footer_counts.most_common(1)[0][0] if footer_counts else None
        
        # Second pass: extract text, remove header/footer
        for i in range(doc.page_count):
            page = doc.load_page(i)
            try:
                lines = page.get_text("text").splitlines()
            except Exception:
                lines = page.getText().splitlines() if hasattr(page, 'getText') else []
            
            # Remove header/footer if detected
            if header and lines and lines[0].strip() == header:
                lines = lines[1:]
            if footer and lines and lines[-1].strip() == footer:
                lines = lines[:-1]
            
            text = "\n".join(lines).strip()
            pages.append({"page_number": i+1, "text": text})
        
        doc.close()
        return pages
    
    def extract_cover_image(self, pdf_path: str, book_id: str) -> bool:
        """Extract cover image from PDF and store in database."""
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            
            try:
                pix = page.get_pixmap()
            except Exception:
                pix = page.getPixmap() if hasattr(page, 'getPixmap') else None
            
            if pix is None:
                print("Warning: Could not extract cover image from PDF.")
                doc.close()
                return False
            
            # Convert to bytes
            cover_data = pix.tobytes("png")
            doc.close()
            
            # Update book with cover image
            self.audiobook_service.book_service.update_book(book_id, {
                'cover_image_data': cover_data,
                'cover_image_type': 'image/png'
            })
            
            print(f"Saved cover image to database for book {book_id}")
            return True
            
        except Exception as e:
            print(f"Error extracting cover image: {e}")
            return False
    
    def extract_metadata(self, pages: list, book_id: str) -> bool:
        """Extract metadata and chapters using AI."""
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY missing from environment")
            return self._create_default_metadata(pages, book_id)
        
        try:
            genai.configure(api_key=api_key)
            model_name = "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name)
            
            # Use first 50 pages for better chapter detection
            front_text = "\n\n".join(f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages[:50])
            prompt = f"""
You are analyzing a general narrative book to extract metadata and chapter information.
From the following front pages (title, copyright, table of contents, introduction):

{front_text}

Return a JSON object:
{{
  "title": "...",
  "author": "...",
  "genre": "...",
  "year": "...",
  "chapters": [
    {{"title": "Chapter 1", "start_page": 1, "end_page": 9}},
    {{"title": "Chapter 2", "start_page": 10, "end_page": 18}},
    ...
  ]
}}

IMPORTANT: 
- Look for table of contents, chapter headings, or section breaks
- If no clear chapters found, create logical chapters every 8-15 pages
- Try to identify chapter titles from headings or TOC
- Return at least 5-10 chapters if possible
- If you cannot find TOC, estimate chapters based on content breaks

Return only valid JSON.
"""
            
            response = model.generate_content(prompt)
            raw_output = response.text
            
            # Try to parse JSON
            import re
            try:
                meta_json = json.loads(raw_output)
            except Exception:
                m = re.search(r"(\{.*\})", raw_output, flags=re.S)
                if m:
                    meta_json = json.loads(m.group(1))
                else:
                    meta_json = {"error": "Could not parse AI output", "raw": raw_output}
            
            # Update book with metadata
            title = meta_json.get("title", "Unknown Title")
            author = meta_json.get("author", "Unknown Author")
            genre = meta_json.get("genre", "Unknown Genre")
            year = meta_json.get("year", "Unknown Year")
            
            self.audiobook_service.book_service.update_book(book_id, {
                'title': title,
                'author': author,
                'genre': genre,
                'year': year,
                'page_count': len(pages)
            })
            
            # Add chapters
            chapters = meta_json.get("chapters", [])
            if chapters:
                self.audiobook_service.add_chapters_to_book(book_id, chapters)
                print(f"Added {len(chapters)} chapters to database")
            else:
                print("No chapters found, creating default chapters")
                self._create_default_chapters(pages, book_id)
            
            return True
            
        except Exception as e:
            print(f"AI extraction failed: {e}")
            return self._create_default_metadata(pages, book_id)
    
    def _create_default_metadata(self, pages: list, book_id: str) -> bool:
        """Create default metadata when AI extraction fails."""
        try:
            # Create minimal book entry
            self.audiobook_service.book_service.update_book(book_id, {
                'title': "Unknown Title",
                'author': "Unknown Author",
                'genre': "Unknown Genre",
                'year': "Unknown Year",
                'page_count': len(pages)
            })
            
            # Create default chapters
            self._create_default_chapters(pages, book_id)
            return True
            
        except Exception as e:
            print(f"Failed to create default metadata: {e}")
            return False
    
    def _create_default_chapters(self, pages: list, book_id: str):
        """Create default chapters when AI extraction fails."""
        default_chapters = []
        pages_per_chapter = max(10, len(pages) // 10)  # At least 10 pages per chapter
        
        for i in range(0, len(pages), pages_per_chapter):
            start_page = i + 1
            end_page = min(i + pages_per_chapter, len(pages))
            default_chapters.append({
                "title": f"Chapter {len(default_chapters) + 1}",
                "start_page": start_page,
                "end_page": end_page
            })
        
        self.audiobook_service.add_chapters_to_book(book_id, default_chapters)
        print(f"Created {len(default_chapters)} default chapters")
    
    def process_pdf(self, pdf_path: str, book_id: str) -> bool:
        """Complete PDF processing pipeline."""
        try:
            print(f"Starting PDF processing for {book_id}")
            
            # Step 1: Extract pages
            print("Extracting pages...")
            pages = self.extract_pages(pdf_path)
            if not pages:
                print("No pages extracted from PDF")
                return False
            
            # Step 2: Add pages to database
            print(f"Adding {len(pages)} pages to database...")
            if not self.audiobook_service.add_pages_to_book(book_id, pages):
                print("Failed to add pages to database")
                return False
            
            # Step 3: Extract cover image
            print("Extracting cover image...")
            self.extract_cover_image(pdf_path, book_id)
            
            # Step 4: Extract metadata and chapters
            print("Extracting metadata and chapters...")
            if not self.extract_metadata(pages, book_id):
                print("Failed to extract metadata")
                return False
            
            print(f"PDF processing completed successfully for {book_id}")
            return True
            
        except Exception as e:
            print(f"PDF processing failed: {e}")
            return False

def main():
    """Command line interface for PDF extraction."""
    import argparse
    parser = argparse.ArgumentParser(description="Extract pages and metadata from PDF")
    parser.add_argument("--pdf_path", type=str, required=True, help="Path to PDF file")
    parser.add_argument("--book_id", type=str, required=True, help="Unique book ID")
    args = parser.parse_args()
    
    # Create book first
    audiobook_service = AudiobookService(repository_factory)
    if not audiobook_service.create_audiobook(args.book_id, "Processing...", "Unknown Author"):
        print("Failed to create book entry")
        return
    
    # Process PDF
    extractor = PDFExtractor()
    success = extractor.process_pdf(args.pdf_path, args.book_id)
    
    if success:
        print(f"Successfully processed PDF: {args.pdf_path}")
    else:
        print(f"Failed to process PDF: {args.pdf_path}")

if __name__ == "__main__":
    main()
