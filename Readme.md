# RAG Chatbot with Flask

## Overview
This project implements a Retrieval-Augmented Generation (RAG) chatbot that:
- Processes PDF documents using **ChromaDB** for vector storage
- Uses **Hugging Face embeddings** for semantic search
- Generates responses via **Groq's deepseek-r1-distill-llama-70b** LLM
- Serves predictions via a Flask API

## Features
- `/chat` endpoint for querying the RAG system
- `/history` endpoint for retrieving conversation logs
- Automatic document chunking and vectorization
- Context-aware responses using retrieved document snippets

## Prerequisites
- Python 3.11+
- [Groq API key](https://console.groq.com/keys)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```ini
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=something
```

## Project Structure
```
./
├── app.py               # Flask API endpoints
├── init_db.py           # MySQL database initialization and operations
├── init_RAG.py          # Document processing & RAG pipeline logic
├── requirements.txt     # Python dependency list
├── .gitignore           # Specifies untracked files
```

## API Endpoints

### POST `/upload`
Add new documents to RAG system
```bash
curl -X POST http://localhost:5000/upload -F "file=@path/to/your/document.pdf" -H "Content-Type: multipart/form-data"
```

### POST `/chat`
Submit queries to the chatbot:
```bash
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"query": "Write the summary of the pdf in 100 words."}'
```

**Response:**
```json
{
  "answer": "The main topic is...",
  "status": "success"
}
```

### GET `/history`
Retrieve chat history:
```bash
curl http://localhost:5000/history?limit=5
```

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "timestamp": "2024-02-01 12:34:56",
      "role": "user",
      "content": "What is XYZ?"
    }
  ]
}
```

## Running the System
```bash
python app.py
```
The API will be available at `http://localhost:5000`

## Database Schema
```sql
CREATE TABLE messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  role ENUM('user', 'system'),
  content TEXT
);
```

## Configuration Tips
1. For local LLM usage: Replace `ChatGroq` in `init_RAG.py` with any Hugging Face model
2. To change document source: Modify `rag.process_documents()` path in `app.py`
3. Adjust chunk size/overlap in `init_RAG.py` for different document types

## Troubleshooting
- **MySQL Connection Issues**: Verify credentials in `.env` match your MySQL setup
- **Missing Documents**: Ensure PDF files exist in `documents/` folder
- **API Errors**: Check Groq API key validity and quota
