#!/usr/bin/env python3
"""
Simplified Document Processor for Vishakha_Notewise
Handles basic file reading - lets OpenRouter AI do the heavy lifting for content analysis.
"""

import os
from pathlib import Path

class SimpleDocumentProcessor:
    """Simplified document processor - OpenRouter handles content analysis."""
    
    def process_file(self, file_path):
        """
        Read file content and return basic metadata.
        OpenRouter API will handle content analysis and extraction.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            dict: Basic file info and raw content
        """
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            file_size = file_path.stat().st_size
            
            if file_extension == '.txt':
                content = self._read_text_file(file_path)
            elif file_extension == '.pdf':
                content = self._read_pdf_basic(file_path)
            elif file_extension in ['.doc', '.docx']:
                content = self._read_doc_basic(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            return {
                'success': True,
                'content': content,
                'metadata': {
                    'file_type': file_extension[1:],  # Remove the dot
                    'size': file_size,
                    'filename': file_path.name
                }
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': f"Error reading file: {str(e)}",
                'metadata': {
                    'file_type': 'unknown',
                    'size': 0,
                    'filename': file_path.name if 'file_path' in locals() else 'unknown'
                }
            }
    
    def _read_text_file(self, file_path):
        """Read text file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _read_pdf_basic(self, file_path):
        """Basic PDF reading - try PyPDF2 or fallback to OpenRouter processing."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n\n"
                
                if content.strip():
                    return content.strip()
                else:
                    # PDF exists but no text could be extracted (might be image-based)
                    return f"PDF file: {file_path.name}\n\nNote: This PDF appears to contain images or no extractable text. Consider using OCR for image-based PDFs."
        except ImportError:
            return self._fallback_message(file_path, 'PDF', 'pip install PyPDF2')
        except Exception as e:
            return f"PDF file: {file_path.name}\n\nError reading PDF: {str(e)}\n\nThe file may be corrupted or password-protected."
    
    def _read_doc_basic(self, file_path):
        """Basic DOC/DOCX reading - try python-docx or fallback to OpenRouter processing."""
        try:
            from docx import Document
            doc = Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content if content.strip() else self._fallback_message(file_path, 'Word document')
        except ImportError:
            return self._fallback_message(file_path, 'Word document', 'pip install python-docx')
        except Exception:
            return self._fallback_message(file_path, 'Word document')
    
    def _fallback_message(self, file_path, file_type, install_cmd=None):
        """Generate fallback message for files that can't be processed locally."""
        message = f"📄 {file_type} file: {file_path.name}\n\n"
        message += "Content extraction requires additional libraries.\n"
        if install_cmd:
            message += f"Install with: {install_cmd}\n\n"
        message += "OpenRouter AI will analyze this file when you save the note."
        return message

# Global processor instance
doc_processor = SimpleDocumentProcessor()