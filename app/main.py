"""
Main Application
--------------
Streamlit-based web interface for the English to Amharic translator.
"""

import streamlit as st
import os
from typing import Optional
import time
import io
import contextlib

from translator import Translator
from pdf_handler import PDFHandler
from utils import clean_text, split_text, is_valid_file, create_required_directories

# Initialize session state
if 'translator' not in st.session_state:
    st.session_state.translator = Translator()
if 'pdf_handler' not in st.session_state:
    st.session_state.pdf_handler = PDFHandler()

def initialize_app():
    """Initialize the application settings and layout."""
    st.set_page_config(
        page_title="English to Amharic Translator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stTextArea {
            font-size: 16px !important;
        }
        .amharic-text {
            font-family: 'Nyala', 'Arial', sans-serif;
            font-size: 18px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the application header."""
    st.title("English to Amharic Translator")
    st.markdown("""
    Welcome to the English to Amharic Translation Service! 
    This application helps you translate English text and PDF documents to Amharic.
    """)

def handle_text_translation():
    """Handle the text translation section."""
    st.header("Text Translation")
    
    # Create two columns for input and output
    col1, col2 = st.columns(2)
    
    with col1:
        input_text = st.text_area(
            "Enter English text:",
            height=200,
            placeholder="Type or paste English text here..."
        )
        
        if st.button("Translate Text", type="primary"):
            if input_text:
                with st.spinner("Translating..."):
                    # Clean and prepare text
                    cleaned_text = clean_text(input_text)
                    
                    # Split long text if necessary
                    chunks = split_text(cleaned_text)
                    
                    # Translate each chunk
                    translated_chunks = []
                    progress_bar = st.progress(0)
                    
                    for i, chunk in enumerate(chunks):
                        translated_chunk = st.session_state.translator.translate(chunk)
                        translated_chunks.append(translated_chunk)
                        progress_bar.progress((i + 1) / len(chunks))
                    
                    # Combine translations
                    final_translation = " ".join(translated_chunks)
                    
                    # Store in session state
                    st.session_state.last_translation = final_translation
                    
                    # Update progress
                    progress_bar.progress(100)
            else:
                st.warning("Please enter some text to translate")
    
    with col2:
        st.subheader("Amharic Translation")
        if 'last_translation' in st.session_state:
            st.markdown(
                f'<div class="amharic-text">{st.session_state.last_translation}</div>',
                unsafe_allow_html=True
            )
            if st.button("Copy Translation"):
                st.write("Translation copied to clipboard!")
                # Note: Actual clipboard functionality requires JavaScript

def handle_pdf_translation():
    """Handle the PDF translation section."""
    st.header("PDF Translation")
    
    # Add debug expander
    debug_container = st.expander("Debug Information", expanded=False)
    with debug_container:
        st.text("Debug logs will appear here during translation")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload an English PDF document to translate to Amharic"
    )
    
    if uploaded_file is not None:
        if is_valid_file(uploaded_file.name):
            st.success(f"File uploaded successfully: {uploaded_file.name}")
            
            if st.button("Translate PDF", type="primary"):
                # Create progress bar and status text
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(progress, message):
                    """Update progress bar and status message."""
                    if progress < 0:  # Error state
                        st.error(message)
                        progress_bar.empty()
                    else:
                        progress_bar.progress(progress)
                        status_text.text(message)
                
                try:
                    # Save uploaded file temporarily
                    temp_path = os.path.join("uploads", uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Create StringIO to capture print statements
                    debug_output = io.StringIO()
                    with contextlib.redirect_stdout(debug_output):
                        # Translate the PDF with progress tracking
                        translated_pdf_path = st.session_state.pdf_handler.translate_pdf(
                            temp_path,
                            st.session_state.translator,
                            progress_callback=update_progress
                        )
                    
                    # Display debug output
                    with debug_container:
                        st.text(debug_output.getvalue())
                    
                    if translated_pdf_path and os.path.exists(translated_pdf_path):
                        # Read the translated PDF for download
                        with open(translated_pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        # Show success message and download button
                        st.success("Translation completed successfully!")
                        st.download_button(
                            label="Download Translated PDF",
                            data=pdf_bytes,
                            file_name=f"translated_{uploaded_file.name}",
                            mime="application/pdf"
                        )
                        
                        # Clean up temporary files
                        os.remove(temp_path)
                        os.remove(translated_pdf_path)
                    else:
                        st.error("Failed to create translated PDF. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    if os.getenv("DEBUG_MODE", "false").lower() == "true":
                        st.exception(e)
                finally:
                    # Clean up temporary file if it exists
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            st.error("Please upload a valid PDF file")

def main():
    """Main application entry point."""
    try:
        # Initialize app
        initialize_app()
        
        # Create required directories
        create_required_directories()
        
        # Render header
        render_header()
        
        # Add tabs for different translation modes
        tab1, tab2 = st.tabs(["Text Translation", "PDF Translation"])
        
        with tab1:
            handle_text_translation()
            
        with tab2:
            handle_pdf_translation()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if os.getenv("DEBUG_MODE", "false").lower() == "true":
            st.exception(e)

if __name__ == "__main__":
    main()
