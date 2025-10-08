# Financial RAG Chatbot

A simple RAG-based chatbot that processes PDF documents and answers questions using OpenAI with Pinecone vector store.

## Features

- **Simple RAG System**: Question answering using retrieval-augmented generation
- **PDF Document Processing**: Intelligent chunking using LangChain RecursiveCharacterTextSplitter
- **Pinecone Vector Store**: Cloud-based vector storage
- **Modern UI**: FastAPI backend + Streamlit frontend
- **Production Ready**: Docker support, health checks, and monitoring

## Tech Stack

- **Backend**: FastAPI, OpenAI, Pydantic
- **Frontend**: Streamlit
- **Vector Store**: Pinecone
- **AI**: OpenAI GPT models for text processing and embeddings

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key (required)
- Pinecone API key (required)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd financial-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your API keys
```

### Running the Application

#### Option 1: Unified Launcher (Recommended)
```bash
python start_chatbot.py
```
This starts both backend (port 8000) and frontend (port 8501).

#### Option 2: Backend Only
```bash
python start_chatbot.py --no-frontend
```

#### Option 3: Manual Start
```bash
# Backend
export PYTHONPATH=$PWD/backend
uvicorn backend.uvicorn_app:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
streamlit run frontend/app.py --server.port 8501
```

### Access Points
- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## Project Structure
```
financial-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/                    # API layer
│   │   │   └── rag_chatbot.py
│   │   ├── core/                   # Configuration and settings
│   │   │   ├── config.py
│   │   │   └── service_config.py
│   │   ├── ingestion/              # Document processing pipeline
│   │   │   └── pipeline.py
│   │   ├── models/                 # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── storage/                # Vector store
│   │   │   └── vector_store.py
│   │   └── storage/                # Data directories
│   │       ├── uploads/            # Temporary file storage
│   │       ├── temp/              # Processing temp files
│   │       └── chroma_db/         # Local Chroma database
│   └── uvicorn_app.py             # FastAPI application entry point
├── frontend/
│   └── app.py                     # Streamlit UI
├── docs/                          # Documentation
├── start_chatbot.py              # Unified application launcher
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml           # Docker Compose setup
├── env.example                  # Environment variables template
└── README.md                    # This file
```

## Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `PINECONE_API_KEY` | Pinecone API key | - | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `us-east-1` | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | `financial-documents` | No |
| `VECTOR_STORE_TYPE` | Storage type (`pinecone` or `local`) | `pinecone` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Environment (`development` or `production`) | `development` | No |

### Storage Configuration

- **Pinecone**: Cloud-based vector storage (recommended for production)
- **Local**: JSON-based fallback storage (development/testing)
- **Uploads**: Temporary staging area (cleared on each restart)
- **Chroma**: Optional local database (if using Chroma)

## API Usage

### Upload Documents
```bash
curl -X POST http://localhost:8000/upload/multiple \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Chat with RAG Chatbot
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the key financial highlights?"}'
```

### Get Document Information
```bash
# List all documents
curl http://localhost:8000/documents

# Get specific document
curl http://localhost:8000/documents/{document_id}

# Get statistics
curl http://localhost:8000/stats
```

## Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t financial-chatbot .

# Run with environment file
docker run -p 8000:8000 --env-file .env financial-chatbot
```

### Docker Compose
```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Stop
docker-compose down
```

## How It Works

### RAG System
- **Document Upload**: PDF files are processed and chunked into smaller pieces
- **Vector Storage**: Text chunks are converted to embeddings and stored in Pinecone
- **Question Processing**: User questions are converted to embeddings
- **Similarity Search**: Relevant chunks are retrieved from Pinecone
- **Response Generation**: OpenAI generates answers based on retrieved context

### Document Processing
- PDF files are parsed using PyPDF2
- Text is split using LangChain's RecursiveCharacterTextSplitter with intelligent separators (1000 characters with 200 overlap)
- Each chunk is embedded using OpenAI's text-embedding-3-small model
- Chunks are stored in Pinecone with metadata (filename, document ID, etc.)

### Question Answering
- User questions are embedded using the same model
- Similarity search finds the most relevant chunks
- Context is prepared from top-k results
- OpenAI GPT generates responses based on the context

## Development

### Code Quality
```bash
# Format code
black backend/app/ --line-length=100

# Lint code
flake8 backend/app/ --max-line-length=100

# Type checking
mypy backend/app/
```

### Testing
```bash
# Run tests (if available)
pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **Vector Store Connection**: Ensure Pinecone API key is correct
2. **OpenAI API**: Verify API key and sufficient credits
3. **File Uploads**: Check file permissions and disk space
4. **Port Conflicts**: Ensure ports 8000 and 8501 are available

### Logs
- Application logs are output to stdout
- Use `docker-compose logs -f chatbot` for Docker logs
- Check API documentation at `/docs` for service status

## License

MIT License - see LICENSE file for details.