"""
Test cases for the translator module.
"""

import pytest
from app.translator import Translator
from app.utils import clean_text, split_text

def test_clean_text():
    """Test text cleaning functionality."""
    input_text = "  This   is  a    test   "
    expected = "This is a test"
    assert clean_text(input_text) == expected

def test_split_text():
    """Test text splitting functionality."""
    # Create a long text
    input_text = " ".join(["word"] * 1000)
    chunks = split_text(input_text, max_length=100)
    
    # Check that each chunk is within the max length
    for chunk in chunks:
        assert len(chunk) <= 100

@pytest.mark.slow
def test_translator():
    """Test basic translation functionality."""
    translator = Translator()
    input_text = "Hello, world!"
    
    # Test translation
    translation = translator.translate(input_text)
    assert translation  # Check that we get a non-empty result
    assert isinstance(translation, str)  # Check that result is a string

@pytest.mark.parametrize("input_text", [
    "",
    "Hello",
    "This is a test",
    "A" * 1000,  # Test long text
])
def test_translator_various_inputs(input_text):
    """Test translator with various input types."""
    translator = Translator()
    translation = translator.translate(input_text)
    assert isinstance(translation, str)
