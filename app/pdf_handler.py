"""
PDF Processing Module
-------------------
Handles PDF file operations including text extraction and PDF generation.
"""

import os
from typing import List, Tuple, Dict
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm, pica
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import re
import traceback

class PDFHandler:
    def __init__(self, upload_dir: str = "uploads"):
        """Initialize PDF handler."""
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        # Register Nyala font for Amharic text
        font_path = os.path.join(os.path.dirname(__file__), "..", "static", "fonts", "nyala.ttf")
        try:
            pdfmetrics.registerFont(TTFont('Nyala', font_path))
        except Exception as e:
            print(f"Warning: Could not load Nyala font: {e}")

    def extract_text_with_positions(self, pdf_file) -> List[Dict]:
        """
        Extract text and their positions from PDF file.
        
        Returns:
            List[Dict]: List of dictionaries containing text and position info for each page
        """
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            pages_content = []
            
            for page_num, page in enumerate(reader.pages):
                # Get page dimensions and rotation
                mediabox = page.mediabox
                page_width = float(mediabox.width)
                page_height = float(mediabox.height)
                rotation = page.get('/Rotate', 0)
                
                # Extract text with positions
                text_content = []
                def visitor_body(text, cm, tm, fontDict, fontSize):
                    if not text.strip():
                        return
                    
                    # Extract position and text properties
                    x = tm[4]
                    y = tm[5]
                    
                    # Get font metrics
                    font_name = fontDict.get('/BaseFont', 'Helvetica') if fontDict else 'Helvetica'
                    font_size = fontSize if fontSize else 12
                    
                    # Store text properties
                    text_content.append({
                        'text': text.strip(),
                        'x': x,
                        'y': y,
                        'fontSize': font_size,
                        'font': font_name,
                        'rotation': rotation,
                        'width': page_width,
                        'height': page_height
                    })
                
                page.extract_text(visitor_text=visitor_body)
                
                if text_content:
                    pages_content.append({
                        'width': page_width,
                        'height': page_height,
                        'rotation': rotation,
                        'content': sorted(text_content, key=lambda x: (-x['y'], x['x'])),  # Sort by y desc, then x asc
                        'page_number': page_num + 1
                    })
            
            return pages_content
            
        except Exception as e:
            print(f"PDF extraction error: {str(e)}")
            return []

    def create_pdf_with_layout(self, pages_content: List[Dict], translations: Dict[str, str]) -> bytes:
        """
        Create a new PDF maintaining the original layout but with translated text.
        """
        buffer = io.BytesIO()
        
        try:
            print("Starting PDF creation...")
            print(f"Number of pages to process: {len(pages_content)}")
            
            # Create PDF with first page size
            first_page = pages_content[0]
            print(f"First page dimensions: {first_page['width']} x {first_page['height']}")
            
            # Create PDF with UTF-8 encoding
            c = canvas.Canvas(buffer, pagesize=(first_page['width'], first_page['height']))
            c._doc.setTitle("Translated Document")
            c._doc.setProducer("English to Amharic Translator")
            c._doc.setAuthor("Amharic Translator")
            
            # Try to register Nyala font
            try:
                nyala_path = os.path.join('fonts', 'nyala.ttf')
                if os.path.exists(nyala_path):
                    print("Using Nyala font for Amharic text")
                    pdfmetrics.registerFont(TTFont('Nyala', nyala_path))
                    font_name = 'Nyala'
                else:
                    print("Nyala font not found, using Helvetica")
                    font_name = 'Helvetica'
            except Exception as e:
                print(f"Error registering font: {str(e)}")
                print("Falling back to Helvetica")
                font_name = 'Helvetica'
            
            for page_num, page in enumerate(pages_content, 1):
                try:
                    print(f"Processing page {page_num}...")
                    
                    # Set up the canvas for this page
                    c.setPageSize((page['width'], page['height']))
                    
                    # Handle page rotation if needed
                    if page['rotation'] != 0:
                        print(f"Rotating page {page_num} by {page['rotation']} degrees")
                        c.rotate(page['rotation'])
                    
                    # Track vertical position to prevent overlaps
                    last_y = None
                    min_y_spacing = 2 * mm  # Minimum 2mm spacing between lines
                    
                    # Sort content by vertical position (top to bottom)
                    sorted_content = sorted(page['content'], 
                                         key=lambda x: float('-inf') if x.get('y') is None else -x['y'])
                    
                    for content_num, content in enumerate(sorted_content, 1):
                        text = content['text']
                        if not text:
                            continue
                        
                        try:
                            # Get translation and ensure it's UTF-8 encoded
                            translated_text = translations.get(text, text)
                            if not translated_text:
                                print(f"Warning: Empty translation for text: {text}")
                                continue
                            
                            # Ensure text is properly encoded
                            if isinstance(translated_text, str):
                                translated_text = translated_text.encode('utf-8').decode('utf-8')
                            
                            # Calculate font size adjustments
                            original_font_size = content.get('fontSize', 12)
                            adjusted_font_size = original_font_size * 1.2  # Slightly larger for Amharic
                            
                            # Set font and size
                            c.setFont(font_name, adjusted_font_size)
                            
                            # Calculate positions
                            x = content.get('x', 0)
                            y = content.get('y', 0)
                            
                            # Adjust vertical position if too close to previous text
                            if last_y is not None and abs(y - last_y) < min_y_spacing:
                                y = last_y - adjusted_font_size - min_y_spacing
                            
                            # Draw text with proper encoding
                            c.drawString(x, y, translated_text)
                            
                            # Update last_y position
                            last_y = y
                            
                        except Exception as e:
                            print(f"Error processing text element {content_num} on page {page_num}: {str(e)}")
                            print(f"Text content: {text}")
                            print(f"Translation: {translated_text}")
                            continue
                    
                    c.showPage()
                    print(f"Completed page {page_num}")
                    
                except Exception as e:
                    print(f"Error processing page {page_num}: {str(e)}")
                    continue
            
            print("Saving PDF...")
            c.save()
            buffer.seek(0)
            print("PDF creation completed successfully")
            return buffer.getvalue()
            
        except Exception as e:
            print(f"PDF creation error: {str(e)}")
            traceback.print_exc()
            return b""

    def translate_pdf(self, pdf_path: str, translator, progress_callback=None) -> str:
        """
        Translate a PDF file from English to Amharic.
        
        Args:
            pdf_path (str): Path to the PDF file
            translator: Translator object
            progress_callback: Optional callback function for progress updates
            
        Returns:
            str: Path to the translated PDF file
        """
        try:
            # Extract text with positions from PDF
            if progress_callback:
                progress_callback(0.1, "Extracting text from PDF...")
                
            with open(pdf_path, 'rb') as file:
                pages_content = self.extract_text_with_positions(file)
            
            if not pages_content:
                raise ValueError("No extractable text found in PDF. Please ensure the PDF contains text and not just images.")
            
            # Create translations dictionary
            translations = {}
            total_items = sum(len(page['content']) for page in pages_content)
            items_processed = 0
            
            if progress_callback:
                progress_callback(0.2, "Translating text...")
            
            for page in pages_content:
                for content in page['content']:
                    text = content['text']
                    if text and text not in translations:
                        try:
                            translated = translator.translate(text)
                            translations[text] = translated
                        except Exception as e:
                            raise ValueError(f"Translation failed: {str(e)}")
                    
                    items_processed += 1
                    if progress_callback:
                        progress = 0.2 + (0.6 * items_processed / total_items)
                        progress_callback(progress, f"Translating page {page['page_number']}...")
            
            # Create new PDF with translations
            if progress_callback:
                progress_callback(0.8, "Creating translated PDF...")
                
            pdf_content = self.create_pdf_with_layout(pages_content, translations)
            
            if not pdf_content:
                raise ValueError("Failed to create PDF with translated text. Please try again with a different PDF.")
            
            # Save the translated PDF
            if progress_callback:
                progress_callback(0.9, "Saving translated PDF...")
                
            output_path = os.path.join(
                self.upload_dir,
                f"translated_{os.path.basename(pdf_path)}"
            )
            
            with open(output_path, 'wb') as file:
                file.write(pdf_content)
            
            if progress_callback:
                progress_callback(1.0, "Translation complete!")
            
            return output_path
            
        except Exception as e:
            error_msg = str(e)
            if "No extractable text" in error_msg:
                error_msg = "Could not extract text from PDF. Please ensure the PDF contains text and not just images."
            elif "Translation failed" in error_msg:
                error_msg = "Translation failed. Please try again or check your internet connection."
            elif "Failed to create PDF" in error_msg:
                error_msg = "Could not create translated PDF. The file might be corrupted or in an unsupported format."
            else:
                error_msg = f"PDF translation error: {error_msg}"
            
            print(error_msg)
            if progress_callback:
                progress_callback(-1, error_msg)
            return ""