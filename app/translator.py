"""
Translation Module
----------------
Handles the core translation functionality using the NLLB model.
"""

import os
from typing import Optional
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

def load_model(model_name: str):
    """Load and cache the model to prevent reloading on every rerun."""
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float32,
            device_map='auto'
        )
        return model
    except Exception as e:
        return None

def load_tokenizer(model_name: str):
    """Load and cache the tokenizer to prevent reloading on every rerun."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return tokenizer
    except Exception as e:
        return None

class Translator:
    def __init__(self):
        """Initialize the translator with the NLLB model."""
        self.model_name = "facebook/nllb-200-distilled-600M"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load tokenizer first
        self.tokenizer = load_tokenizer(self.model_name)
        if self.tokenizer is None:
            raise RuntimeError("Failed to load tokenizer")
            
        # Load model with optimizations
        self.model = load_model(self.model_name)
        if self.model is None:
            raise RuntimeError("Failed to load model")
            
        # Move model to appropriate device
        self.model.to(self.device)
        
        # Set language codes
        self.src_lang = "eng_Latn"  # English
        self.tgt_lang = "amh_Ethi"  # Amharic
        
        # Clear GPU memory if possible
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    def translate(self, text: str, max_length: Optional[int] = 512) -> str:
        """
        Translate English text to Amharic.
        
        Args:
            text (str): The English text to translate
            max_length (int, optional): Maximum length of the translated text
            
        Returns:
            str: The translated Amharic text
        """
        try:
            # Prepare the input text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            ).to(self.device)
            
            # Add language tokens
            inputs["forced_bos_token_id"] = self.tokenizer.lang_code_to_id[self.tgt_lang]
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=5,
                    length_penalty=1.0,
                    early_stopping=True
                )
            
            # Decode the translation
            translated_text = self.tokenizer.batch_decode(
                outputs,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )[0]
            
            return translated_text
            
        except Exception as e:
            raise RuntimeError(f"Translation error: {str(e)}")

    def __call__(self, text: str) -> str:
        """
        Make the translator callable.
        
        Args:
            text (str): The English text to translate
            
        Returns:
            str: The translated Amharic text
        """
        return self.translate(text)
