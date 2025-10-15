import PyPDF2
import pdfplumber
import os
import re
from typing import Dict, List, Tuple

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt']
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text from PDF file using multiple methods for better accuracy"""
        text = ""
        metadata = {}
        
        try:
            # Method 1: Using PyPDF2 for metadata and basic text
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    'pages': len(pdf_reader.pages),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'subject': pdf_reader.metadata.get('/Subject', '')
                }
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
        
        # Method 2: Using pdfplumber for better text extraction
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"PDFPlumber extraction failed: {e}")
        
        return text.strip(), metadata
    
    def extract_text_from_txt(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        metadata = {
            'pages': 1,
            'author': '',
            'title': os.path.basename(file_path),
            'subject': ''
        }
        
        return text, metadata
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        return text.strip()
    
    def process_document(self, file_path: str) -> Dict:
        """Main method to process any supported document"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text, metadata = self.extract_text_from_pdf(file_path)
        elif file_ext == '.txt':
            text, metadata = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        cleaned_text = self.clean_text(text)
        
        return {
            'raw_text': text,
            'cleaned_text': cleaned_text,
            'metadata': metadata,
            'word_count': len(cleaned_text.split()),
            'char_count': len(cleaned_text)
        }