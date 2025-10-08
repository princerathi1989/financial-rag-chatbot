"""FastAPI application for the multi-agent chatbot."""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from loguru import logger
import sys
import os
from contextlib import asynccontextmanager

from app.core.config import settings, ensure_directories, setup_langsmith
from app.models.schemas import (
    ChatRequest, ChatResponse, DocumentUploadResponse, 
    ErrorResponse, DocumentType
)
from app.api.rag_chatbot import rag_chatbot

ensure_directories()

setup_langsmith()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Financial RAG Chatbot API")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"OpenAI model: {settings.openai_model}")
    yield
    logger.info("Shutting down Financial RAG Chatbot API")


app = FastAPI(
    title="Financial RAG Chatbot",
    description="A simple RAG-based chatbot for financial PDF document Q&A",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.remove()
logger.add(sys.stdout, level=settings.log_level)




@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Financial RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "supported_formats": ["pdf"],
        "description": "Simple RAG-based chatbot for financial document Q&A"
    }


@app.post("/upload/multiple", response_model=List[DocumentUploadResponse])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload and process multiple PDF documents."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 10:  # Limit to 10 files at once
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        responses = []
        errors = []
        
        for file in files:
            try:
                # Validate file type
                if not file.filename.lower().endswith('.pdf'):
                    errors.append(f"{file.filename}: Only PDF files are allowed")
                    continue
                
                # Check file size
                file_content = await file.read()
                file_size_mb = len(file_content) / (1024 * 1024)
                if file_size_mb > settings.max_file_size_mb:
                    errors.append(f"{file.filename}: File size ({file_size_mb:.2f}MB) exceeds maximum ({settings.max_file_size_mb}MB)")
                    continue
                
                # Process the document
                response = rag_chatbot.upload_document(file_content, file.filename)
                responses.append(response)
                
                logger.info(f"Successfully uploaded: {file.filename}")
                
            except Exception as e:
                logger.error(f"Error uploading {file.filename}: {e}")
                errors.append(f"{file.filename}: {str(e)}")
                responses.append(DocumentUploadResponse(
                    document_id="",
                    filename=file.filename,
                    document_type="unknown",
                    status='error',
                    metadata={"error": str(e)}
                ))
        
        # If all files failed, return error
        if not responses or all(r.status == 'error' for r in responses):
            raise HTTPException(status_code=500, detail=f"All uploads failed: {'; '.join(errors)}")
        
        logger.info(f"Batch upload completed: {len([r for r in responses if r.status == 'processed'])} successful, {len(errors)} errors")
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the RAG chatbot."""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process the chat message
        response = rag_chatbot.process_chat_message(request)
        
        logger.info(f"Processed chat message with RAG chatbot")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=List[dict])
async def list_documents():
    """List all uploaded documents."""
    try:
        documents = rag_chatbot.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{document_id}", response_model=dict)
async def get_document(document_id: str):
    """Get information about a specific document."""
    try:
        doc_info = rag_chatbot.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": document_id,
            "filename": doc_info["filename"],
            "file_type": doc_info["file_type"],
            "status": doc_info["status"],
            "metadata": {
                "total_chunks": doc_info.get("total_chunks", 0),
                "total_words": doc_info.get("total_words", 0),
                "total_characters": doc_info.get("total_characters", 0)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=dict)
async def get_stats():
    """Get system statistics."""
    try:
        from app.storage.vector_store import get_vector_store
        
        documents = rag_chatbot.list_documents()
        vector_store = get_vector_store()
        vector_stats = vector_store.get_collection_stats()
        
        return {
            "total_documents": len(documents),
            "pdf_documents": len([d for d in documents if d["file_type"] == "pdf"]),
            "vector_store": vector_stats,
            "chatbot_type": "RAG-based"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            code="500"
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.uvicorn_app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        workers=settings.workers
    )

