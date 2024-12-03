"""
Utility Functions
---------------
Helper functions for the translation application.
"""

import os
from typing import List
from pathlib import Path

def create_required_directories():
    """Create necessary directories if they don't exist."""
    directories = ["uploads", "models", "static"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def clean_text(text: str) -> str:
    """
    Clean and prepare text for translation.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    return text

def split_text(text: str, max_length: int = 512) -> List[str]:
    """
    Split long text into smaller chunks for translation.
    
    Args:
        text (str): Text to split
        max_length (int): Maximum length of each chunk
        
    Returns:
        List[str]: List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) > max_length:
            # Remove last word if it makes the chunk too long
            if len(current_chunk) > 1:
                current_chunk.pop()
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def is_valid_file(filename: str, allowed_extensions: set = {'.pdf'}) -> bool:
    """
    Check if the file has an allowed extension.
    
    Args:
        filename (str): Name of the file to check
        allowed_extensions (set): Set of allowed file extensions
        
    Returns:
        bool: True if file extension is allowed
    """
    return Path(filename).suffix.lower() in allowed_extensions
