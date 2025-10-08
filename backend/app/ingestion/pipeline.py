"""Document ingestion pipeline for PDFs."""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from loguru import logger
from app.core.config import settings


class DocumentProcessor:
    """Base class for document processing."""
    
    def __init__(self):
        self.supported_extensions = []
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process a document and return metadata."""
        raise NotImplementedError


class PDFProcessor(DocumentProcessor):
    """PDF document processor."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or settings.max_chunk_size
        overlap = overlap or settings.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process PDF document."""
        try:
            text = self.extract_text(file_path)
            chunks = self.chunk_text(text)
            
            metadata = {
                'total_chunks': len(chunks),
                'total_characters': len(text),
                'total_words': len(text.split()),
                'chunks': chunks,
                'full_text': text
            }
            
            logger.info(f"Processed PDF: {len(chunks)} chunks, {len(text)} characters")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise




class DocumentIngestionPipeline:
    """Main document ingestion pipeline."""
    
    def __init__(self):
        self.processors = {
            'pdf': PDFProcessor()
        }
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type from extension."""
        ext = Path(filename).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        else:
            raise ValueError(f"Unsupported file type: {ext}. Only PDF files are supported.")
    
    def save_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to storage."""
        document_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        saved_filename = f"{document_id}{file_extension}"
        file_path = os.path.join(settings.upload_directory, saved_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path, document_id
    
    def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded document."""
        try:
            # Save file
            file_path, document_id = self.save_file(file_content, filename)
            
            # Determine file type
            file_type = self.get_file_type(filename)
            
            # Process document
            processor = self.processors[file_type]
            metadata = processor.process(file_path)
            
            # Add document metadata
            metadata.update({
                'document_id': document_id,
                'filename': filename,
                'file_type': file_type,
                'file_path': file_path,
                'status': 'processed'
            })
            
            logger.info(f"Successfully processed document {document_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve processed document by ID."""
        # In a production system, this would query a database
        # For now, we'll implement a simple file-based lookup
        try:
            # This is a simplified implementation
            # In production, you'd store metadata in a database
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None

