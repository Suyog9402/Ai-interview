# RAG System Setup Guide

This guide will help you set up the RAG (Retrieval-Augmented Generation) system for resume-JD matching in the AI Interview Assistant.

## Prerequisites

1. **Azure OpenAI Account**: You need an Azure OpenAI account with:
   - A chat model deployment (e.g., GPT-4)
   - An embedding model deployment (e.g., text-embedding-ada-002)

2. **Python Environment**: Make sure you have Python 3.8+ installed

## Setup Steps

### 1. Install Dependencies

```bash
cd voice-assistant/backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the `voice-assistant/backend` directory with the following variables:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_chat_deployment_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_embedding_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database Configuration
DATABASE_URL=postgresql://postgres@localhost:5432/interview_assistant

# JWT Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Initialize the RAG System

Run the initialization script to load job descriptions into the vector store:

```bash
cd voice-assistant/backend
python initialize_rag.py
```

This script will:
- Check for required environment variables
- Load all job descriptions from the `jd/` folder
- Create embeddings and store them in the vector database

### 4. Start the Backend Server

```bash
cd voice-assistant/backend
uvicorn main:app --reload
```

The server will start on `http://127.0.0.1:8000`

## API Endpoints

### Resume Upload and Matching

- `POST /api/v1/resume/upload` - Upload a resume PDF
- `GET /api/v1/resume/match-jds` - Get job matches for uploaded resume
- `GET /api/v1/resume/jd/{filename}` - Get specific job description content
- `POST /api/v1/resume/initialize-jds` - Reinitialize job descriptions
- `GET /api/v1/resume/resume-status` - Check if user has uploaded resume

### Authentication Required

All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## How It Works

### 1. Resume Upload
- User uploads a PDF resume
- System processes the PDF using PyPDFLoader
- Content is split into chunks and embedded
- Stored in Chroma vector database with user metadata

### 2. Job Description Matching
- System retrieves user's resume content
- Compares against all job descriptions using semantic search
- Uses Azure OpenAI to analyze match percentage and provide detailed analysis
- Returns matches above 60% threshold with:
  - Match percentage
  - Detailed analysis
  - Key matching skills
  - Missing skills
  - Recommendations

### 3. Vector Database
- Uses Chroma as the vector database
- Separate collections for resumes and job descriptions
- Persistent storage in `db/vector_store/` directory

## File Structure

```
voice-assistant/backend/
├── app/
│   ├── services/
│   │   └── rag_service.py          # RAG service implementation
│   └── api/
│       └── resume.py               # Resume API endpoints
├── jd/                             # Job description files
├── db/
│   └── vector_store/               # Vector database storage
├── uploads/                        # Uploaded resume files
├── initialize_rag.py               # RAG initialization script
└── requirements.txt                # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure all Azure OpenAI variables are set correctly
   - Check that the deployment names match your Azure setup

2. **Vector Store Errors**
   - Delete the `db/vector_store/` directory and reinitialize
   - Run `python initialize_rag.py` again

3. **PDF Processing Errors**
   - Ensure PDF files are not corrupted
   - Check file size limits (10MB max)
   - Verify PDF contains extractable text

4. **API Authentication Errors**
   - Ensure user is logged in and has valid JWT token
   - Check token expiration

### Debug Mode

Enable debug logging by setting the log level in your environment:
```env
LOG_LEVEL=DEBUG
```

## Performance Considerations

- **Embedding Generation**: Initial job description embedding may take time
- **Matching Process**: Each resume-JD comparison involves AI analysis
- **Storage**: Vector database grows with more resumes and job descriptions
- **API Rate Limits**: Respect Azure OpenAI rate limits

## Security Notes

- Resume files are stored locally in user-specific directories
- Vector database contains sensitive information
- Ensure proper access controls and data protection
- Consider encryption for stored data in production

## Production Deployment

For production deployment:

1. Use a production-grade database (PostgreSQL)
2. Implement proper file storage (AWS S3, Azure Blob)
3. Add monitoring and logging
4. Implement rate limiting
5. Use HTTPS and proper security headers
6. Consider using managed vector databases (Pinecone, Weaviate) 