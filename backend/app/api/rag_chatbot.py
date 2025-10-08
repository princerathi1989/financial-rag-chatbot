"""Simple RAG chatbot service for financial document Q&A."""

from typing import Dict, Any, Optional, List
from loguru import logger
from openai import OpenAI
from langsmith import traceable
from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, DocumentUploadResponse
from app.storage.vector_store import get_vector_store
from app.ingestion.pipeline import DocumentIngestionPipeline


class SimpleRAGChatbot:
    """Simple RAG chatbot for financial document processing and Q&A."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.document_store = {}  # In-memory document metadata storage
        self.logger = logger.bind(component="rag_chatbot")
    
    @traceable(name="rag_chat_message")
    def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message using RAG (Retrieval-Augmented Generation)."""
        try:
            query = request.message.strip()
            if not query:
                return ChatResponse(
                    response="Please provide a question about your uploaded documents.",
                    sources=[],
                    metadata={"error": "Empty message"}
                )
            
            # Search for relevant chunks
            vector_store = get_vector_store()
            search_results = vector_store.search_similar_chunks(
                query=query,
                top_k=settings.rag_top_k_results,
                document_id=request.document_id
            )
            
            if not search_results:
                return ChatResponse(
                    response="I couldn't find relevant information in the uploaded documents to answer your question. Please make sure you have uploaded PDF documents first.",
                    sources=[],
                    metadata={"context_chunks_found": 0}
                )
            
            # Prepare context from search results
            context_text = self._prepare_context_from_search_results(search_results)
            
            # Generate response using OpenAI
            response = self._generate_response(query, context_text)
            
            # Prepare sources
            sources = self._prepare_sources(search_results)
            
            return ChatResponse(
                response=response,
                sources=sources,
                metadata={
                    "context_chunks_found": len(search_results),
                    "document_id": request.document_id,
                    "query_type": "rag"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again.",
                sources=[],
                metadata={"error": str(e)}
            )
    
    def _prepare_context_from_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context string from search results."""
        if not search_results:
            return ""
        
        context_parts = ["=== RELEVANT DOCUMENT CONTENT ==="]
        for i, result in enumerate(search_results[:3]):  # Top 3 results
            filename = result.get('metadata', {}).get('filename', 'Unknown')
            content = result.get('content', '')
            context_parts.append(f"Source {i+1} (from {filename}):")
            context_parts.append(content)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    @traceable(name="rag_generate_response")
    def _generate_response(self, query: str, context: str) -> str:
        """Generate response using OpenAI with context."""
        try:
            prompt = f"""You are a helpful financial assistant. Answer the user's question based on the provided context from financial documents.

Context from financial documents:
{context}

User Question: {query}

Instructions:
- Provide a clear and accurate answer based on the context provided
- If the context doesn't contain enough information, clearly state this limitation
- Use professional financial language
- Be concise but comprehensive
- If you find specific numbers, metrics, or data in the context, include them in your answer
- Always cite which document the information comes from when possible

Answer:"""

            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant that answers questions based on provided document context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I encountered an error while generating a response. Please try again."
    
    def _prepare_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare sources for the response."""
        sources = []
        for result in search_results:
            source = {
                "content": result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', ''),
                "metadata": result.get('metadata', {}),
                "relevance_score": result.get('relevance_score', 0),
                "document_type": result.get('metadata', {}).get('file_type', 'unknown')
            }
            sources.append(source)
        return sources
    
    @traceable(name="rag_upload_document")
    def upload_document(self, file_content: bytes, filename: str) -> DocumentUploadResponse:
        """Upload and process a document."""
        try:
            # Process the document
            metadata = self.ingestion_pipeline.process_document(file_content, filename)
            
            # Store document metadata
            document_id = metadata['document_id']
            self.document_store[document_id] = metadata
            
            # Add to vector store if it has chunks
            if 'chunks' in metadata and metadata['chunks']:
                self.logger.info(f"🔄 UPLOAD: Adding document {document_id} ({filename}) to vector store...")
                vector_store = get_vector_store()
                vector_store.add_document_chunks(
                    document_id=document_id,
                    chunks=metadata['chunks'],
                    metadata={
                        'filename': metadata['filename'],
                        'file_type': metadata['file_type'],
                        'total_chunks': metadata['total_chunks']
                    }
                )
                self.logger.info(f"🎉 UPLOAD COMPLETE: Document {document_id} ({filename}) successfully processed and stored!")
            else:
                self.logger.warning(f"⚠️ UPLOAD WARNING: Document {document_id} ({filename}) has no chunks to store")
            
            return DocumentUploadResponse(
                document_id=document_id,
                filename=filename,
                document_type=metadata['file_type'],
                status='processed',
                metadata={
                    'total_chunks': metadata.get('total_chunks', 0),
                    'total_words': metadata.get('total_words', 0),
                    'file_size': len(file_content)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error uploading document: {e}")
            return DocumentUploadResponse(
                document_id="",
                filename=filename,
                document_type="pdf",
                status='error',
                metadata={"error": str(e)}
            )
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific document."""
        try:
            # First check local document store
            if document_id in self.document_store:
                doc_data = self.document_store[document_id]
                return {
                    'document_id': document_id,
                    'filename': doc_data['filename'],
                    'file_type': doc_data['file_type'],
                    'total_chunks': doc_data.get('total_chunks', 0),
                    'total_words': doc_data.get('total_words', 0),
                    'status': doc_data.get('status', 'processed')
                }
            
            # Fallback to vector store
            vector_store = get_vector_store()
            chunks = vector_store.get_document_chunks(document_id)
            if not chunks:
                return None
            
            metadata = chunks[0]['metadata']
            return {
                'document_id': document_id,
                'filename': metadata.get('filename', 'Unknown'),
                'file_type': metadata.get('file_type', 'unknown'),
                'total_chunks': len(chunks),
                'upload_date': metadata.get('upload_date', 'Unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting document info: {e}")
            return None
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents."""
        try:
            # Get documents from local store first
            documents = []
            for doc_id, doc_data in self.document_store.items():
                documents.append({
                    'document_id': doc_id,
                    'filename': doc_data['filename'],
                    'file_type': doc_data['file_type'],
                    'status': doc_data.get('status', 'processed'),
                    'total_chunks': doc_data.get('total_chunks', 0)
                })
            
            self.logger.info(f"Listed {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []
    
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search across all uploaded documents."""
        try:
            vector_store = get_vector_store()
            results = vector_store.search_similar_chunks(
                query=query,
                top_k=top_k,
                document_id=None  # Search all documents
            )
            
            self.logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        try:
            vector_store = get_vector_store()
            chunks = vector_store.get_document_chunks(document_id)
            self.logger.info(f"Retrieved {len(chunks)} chunks for document: {document_id}")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error getting document chunks: {e}")
            return []


# Global chatbot instance
rag_chatbot = SimpleRAGChatbot()
