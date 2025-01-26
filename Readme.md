# RAG Chatbot with Flask & MySQL

## Overview
This project implements a Retrieval-Augmented Generation (RAG) chatbot that:
- Processes PDF documents using **ChromaDB** for vector storage
- Uses **Hugging Face embeddings** for semantic search
- Generates responses via **Groq's Llama 3.2-1B** LLM
- Stores chat history in a **MySQL** database
- Serves predictions via a Flask API

## Features
- `/chat` endpoint for querying the RAG system
- `/history` endpoint for retrieving conversation logs
- Automatic document chunking and vectorization
- Context-aware responses using retrieved document snippets

## Prerequisites
- Python 3.9+
- MySQL Server installed and running
- [Groq API key](https://console.groq.com/keys)
- PDF documents in `documents/` folder (e.g., `sample.pdf`)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```ini
GROQ_API_KEY=your_groq_api_key
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=chat_history
```

### 3. Database Setup
1. Create MySQL database:
```sql
CREATE DATABASE chat_history;
```
2. Tables will be auto-created when starting the app

### 4. Add Documents
Place PDF files in `documents/` folder. The system will automatically process `sample.pdf` on startup.

## Project Structure
```
./
├── app.py               # Flask API endpoints
├── init_db.py           # MySQL database initialization and operations
├── init_RAG.py          # Document processing & RAG pipeline logic
├── requirements.txt     # Python dependency list
├── .env                 # Environment variables (API keys, DB credentials)
├── .gitignore           # Specifies untracked files
└── documents/           # Folder for PDF documents
    └── sample.pdf       # Example document for processing
```

## API Endpoints

### POST `/chat`
Submit queries to the chatbot:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

**Response:**
```json
{
  "answer": "The main topic is...",
  "status": "success"
}
```

### GET `/history`
Retrieve chat history (max 100 messages):
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

(chat_history)[!chat_history]

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
