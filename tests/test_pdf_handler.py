"""
Test cases for the PDF handler module.
"""

import os
import pytest
from app.pdf_handler import PDFHandler
import io

@pytest.fixture
def pdf_handler():
    """Create a PDF handler instance for testing."""
    return PDFHandler(upload_dir="test_uploads")

@pytest.fixture
def sample_pdf():
    """Create a simple PDF for testing."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 750, "Hello, World!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def test_extract_text_with_positions(pdf_handler, sample_pdf):
    """Test text extraction with positions."""
    pages_content = pdf_handler.extract_text_with_positions(sample_pdf)
    
    # Check that we got some content
    assert pages_content
    assert isinstance(pages_content, list)
    
    # Check first page
    page = pages_content[0]
    assert 'width' in page
    assert 'height' in page
    assert 'content' in page
    
    # Check content
    content = page['content']
    assert content
    text_item = content[0]
    assert 'text' in text_item
    assert 'x' in text_item
    assert 'y' in text_item
    assert 'fontSize' in text_item
    assert text_item['text'].strip() == "Hello, World!"

def test_create_pdf_with_layout(pdf_handler, sample_pdf):
    """Test PDF creation with layout preservation."""
    # First extract text
    pages_content = pdf_handler.extract_text_with_positions(sample_pdf)
    
    # Create translations dictionary
    translations = {
        "Hello, World!": "ሰላም፣ ዓለም!"
    }
    
    # Create new PDF
    pdf_content = pdf_handler.create_pdf_with_layout(pages_content, translations)
    
    # Check that we got PDF content
    assert pdf_content
    assert isinstance(pdf_content, bytes)
    assert len(pdf_content) > 0

def test_translate_pdf(pdf_handler, sample_pdf, tmp_path):
    """Test full PDF translation process."""
    # Save sample PDF to temp file
    pdf_path = os.path.join(tmp_path, "test.pdf")
    with open(pdf_path, "wb") as f:
        f.write(sample_pdf.getvalue())
    
    # Mock translator
    class MockTranslator:
        def translate(self, text):
            return "ሰላም፣ ዓለም!" if text.strip() == "Hello, World!" else text
    
    # Translate PDF
    output_path = pdf_handler.translate_pdf(pdf_path, MockTranslator())
    
    # Check output
    assert output_path
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0

def test_cleanup(pdf_handler):
    """Test cleanup after all tests."""
    import shutil
    if os.path.exists("test_uploads"):
        shutil.rmtree("test_uploads")
