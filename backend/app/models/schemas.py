"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    document_id: Optional[str] = Field(None, description="Document ID for context")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[], description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="RAG chatbot response")
    sources: Optional[List[Dict[str, Any]]] = Field(
        default=[], description="Source documents or data used"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional metadata"
    )


class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Document type")
    status: str = Field(..., description="Processing status")
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Document metadata"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")

