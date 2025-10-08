# Financial Multi-Agent Chatbot API Documentation

## Overview

The Financial Multi-Agent Chatbot API provides a comprehensive interface for interacting with specialized AI agents that can process PDF documents, answer questions, generate summaries, and create quizzes.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement proper API key authentication.

## Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Document Upload

#### POST /upload/multiple

Upload and process one or more PDF documents.

**Request:**
- Content-Type: `multipart/form-data`
- Body: repeatable field name `files` (supports up to 10 files)

**Response:**
Returns a JSON array of `DocumentUploadResponse` items.

```json
[
  {
    "document_id": "3334d636-f573-4836-9770-160f4afa1f29",
    "filename": "document.pdf",
    "document_type": "pdf",
    "status": "processed",
    "metadata": {
      "total_chunks": 25,
      "total_words": 5000,
      "file_size": 1024000
    }
  }
]
```

### Chat Interface

#### POST /chat

Send a message to the multi-agent system.

**Request:**
```json
{
  "message": "What is the main topic of the document?",
  "agent_type": "q&a",
  "document_id": "doc_123456",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "The main topic of the document is ...",
  "agent_type": "q&a",
  "sources": [
    {
      "content": "Quarterly revenue grew 12% ...",
      "metadata": {
        "document_id": "doc_123456",
        "chunk_index": 0,
        "file_type": "pdf",
        "filename": "document.pdf"
      },
      "relevance_score": 0.92,
      "document_type": "pdf"
    }
  ],
  "metadata": {
    "context_chunks_found": 5,
    "agent_type": "q&a",
    "is_analytics_query": false,
    "document_types": ["pdf"]
  }
}
```

### Agent Information

#### GET /agents/{agent_type}

Get information about a specific agent.

**Parameters:**
- `agent_type`: One of `q&a`, `summarization`, `mcq`

**Response:**
```json
{
  "name": "Q&A Agent",
  "description": "Question-answering and analytics over PDF documents using retrieval-augmented generation",
  "capabilities": [
    "Document Q&A",
    "Analytics & KPIs",
    "Trend analysis",
    "Context retrieval",
    "Citation tracking",
    "Data insights"
  ],
  "input_requirements": [
    "PDF documents",
    "Natural language questions",
    "Analytics queries"
  ]
}
```

### Document Management

#### GET /documents

List all uploaded documents.

**Response:**
```json
[
  {
    "document_id": "doc_123456",
    "filename": "document.pdf",
    "file_type": "pdf",
    "status": "processed",
    "total_chunks": 25
  }
]
```

#### GET /documents/{document_id}

Get information about a specific document.

**Response:**
```json
{
  "document_id": "doc_123456",
  "filename": "document.pdf",
  "file_type": "pdf",
  "status": "processed",
  "metadata": {
    "total_chunks": 25,
    "total_words": 5000,
    "total_characters": 30000
  }
}
```

#### DELETE /documents/{document_id}

Delete a document and its associated data.

**Response:**
```json
{
  "message": "Document doc_123456 deleted successfully"
}
```

### System Statistics

#### GET /stats

Get system statistics and status.

**Response:**
```json
{
  "total_documents": 10,
  "pdf_documents": 10,
  "vector_store": {
    "total_chunks": 250,
    "collection_name": "financial-documents"
  },
  "agents": {
    "q&a": "active",
    "summarization": "active",
    "mcq": "active"
  }
}
```

## Agent Types

### Q&A Agent (`q&a`)

**Purpose:** Question-answering and analytics over PDF documents using retrieval-augmented generation.

**Capabilities:**
- Answer questions about uploaded PDF documents
- Perform analytics, KPI calculations, and trend analysis
- Provide citations and source references
- Context-aware responses based on document content
- Generate insights from financial data

**Usage:**
```json
{
  "message": "What are the revenue trends in this document?",
  "agent_type": "q&a",
  "document_id": "doc_123456"
}
```

**Analytics Queries:**
```json
{
  "message": "Calculate the profit margins and identify any anomalies",
  "agent_type": "q&a",
  "document_id": "doc_123456"
}
```

### Summarization Agent (`summarization`)

**Purpose:** Create executive summaries with key quotes and citations.

**Capabilities:**
- Generate executive summaries
- Extract key quotes with context
- Provide document overviews

**Usage:**
```json
{
  "message": "Summarize this document",
  "agent_type": "summarization",
  "document_id": "doc_123456"
}
```

### MCQ Agent (`mcq`)

**Purpose:** Generate multiple choice questions with answers and rationales.

**Capabilities:**
- Create educational questions
- Provide answer options
- Include detailed rationales

**Usage:**
```json
{
  "message": "Generate quiz questions from this document",
  "agent_type": "mcq",
  "document_id": "doc_123456"
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input data
- `404`: Not Found - Document or resource not found
- `413`: Payload Too Large - File size exceeds limit
- `500`: Internal Server Error - Server-side error

### Example Error Responses

**File Size Exceeded:**
```json
{
  "error": "File size (60.5MB) exceeds maximum allowed size (50MB)",
  "code": "413"
}
```

**Document Not Found:**
```json
{
  "error": "Document not found",
  "code": "404"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement appropriate rate limiting based on your requirements.

## File Upload Limits

- **Maximum file size:** 50MB
- **Supported formats:** PDF only
- **Processing timeout:** 5 minutes

## Examples

### Complete Workflow Example

1. **Upload PDF documents:**
```bash
curl -X POST "http://localhost:8000/upload/multiple" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"
```

2. **Ask a question about the document:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main topic of this document?",
    "agent_type": "q&a",
    "document_id": "doc_123456"
  }'
```

3. **Generate a summary:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize this document",
    "agent_type": "summarization",
    "document_id": "doc_123456"
  }'
```

## SDK Examples

### Python SDK

```python
import requests

# Upload documents
files = [
    ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')),
]
upload_resp = requests.post('http://localhost:8000/upload/multiple', files=files)
upload_resp.raise_for_status()
first_doc_id = upload_resp.json()[0]['document_id']

# Ask question
chat_resp = requests.post(
    'http://localhost:8000/chat',
    json={
        'message': 'What is the main topic?',
        'agent_type': 'q&a',
        'document_id': first_doc_id
    }
)
print(chat_resp.json()['response'])
```

### JavaScript SDK

```javascript
// Upload documents
const formData = new FormData();
formData.append('files', pdfFile);

const uploadResponse = await fetch('/upload/multiple', {
  method: 'POST',
  body: formData
});
const uploads = await uploadResponse.json();
const document_id = uploads[0].document_id;

// Ask question
const chatResponse = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is the main topic?',
    agent_type: 'q&a',
    document_id
  })
});
const { response } = await chatResponse.json();
console.log(response);
```

## API Response Models

### ChatRequest
```json
{
  "message": "string",
  "agent_type": "q&a" | "summarization" | "mcq",
  "document_id": "string",
  "conversation_history": []
}
```

### ChatResponse
```json
{
  "response": "string",
  "agent_type": "q&a" | "summarization" | "mcq",
  "sources": [
    {
      "content": "string",
      "metadata": {},
      "relevance_score": 0.92,
      "document_type": "pdf"
    }
  ],
  "metadata": {}
}
```

### DocumentUploadResponse
```json
{
  "document_id": "string",
  "filename": "string",
  "document_type": "pdf",
  "status": "processed" | "error",
  "metadata": {
    "total_chunks": 25,
    "total_words": 5000,
    "file_size": 1024000
  }
}
```