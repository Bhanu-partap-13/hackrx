# HackRx 6.0 - LLM-Powered Intelligent Query-Retrieval System

This project is a Retrieval-Augmented Generation (RAG) system built for HackRx 6.0. It processes insurance policy PDFs from a given URL, chunks and embeds the text using Sentence Transformers and FAISS for efficient retrieval, and generates precise, explainable answers using the Groq API. The system adheres to the specified API format with a base URL of `/api/v1`, Bearer token authentication, and JSON input/output for documents and questions.

## Key Features
- **API Endpoint**: POST `/api/v1/hackrx/run` – Accepts a document URL and list of questions, returns an array of answers.
- **Authentication**: Requires `Authorization: Bearer 80952cdfb4fc8cfff557b6cb27c4c39b9c980c039093b1ec6047ebedba90a9d7`.
- **Modular Architecture**: Separate modules for document processing, vector storage, and Groq integration.
- **Efficiency**: Optimized chunking, embedding, and retrieval for low latency.
- **Explainability**: Answers cite specific clauses/periods from the context where possible.

## Tech Stack
- FastAPI for the API server.
- Sentence Transformers and FAISS for embedding and vector search.
- Groq API for LLM generation (using Llama3 model).
- PyPDF2 for PDF parsing.
- Python-dotenv for environment management.

## Requirements
- Python 3.8+ (tested on 3.11).
- Dependencies: Listed in `requirements.txt` (e.g., fastapi, uvicorn, sentence-transformers, faiss-cpu, groq, PyPDF2, requests, python-dotenv).

## Setup Instructions
1. **Clone or Unzip the Project**:
   - Extract the ZIP to a folder (e.g., `hackrx-project`).

2. **Create and Activate Virtual Environment**:
    - python -m venv hackrx_env
    - hackrx_env\Scripts\activate # On Windows (use source on Linux/Mac)

3. **Install Dependencies**:
    - pip install -r requirements.txt


4. **Configure Environment Variables**:
- Copy `.env.template` to `.env`.
- Add your Groq API key: `GROQ_API_KEY=your_groq_api_key_here` (obtain from Groq dashboard).

## How to Run the Files
### Starting the FastAPI Server
- In the project directory, run:

- uvicorn main:app --host 127.0.0.1 --port 8000 --reload
- The server will start and log: `Uvicorn running on http://127.0.0.1:8000`.
- Access interactive Swagger UI docs at: http://127.0.0.1:8000/docs (for testing endpoints).

### Testing the API
- With the server running, open another terminal and run the test script:


- Expected Response: JSON with `"answers"` array.

## Project Structure
- `main.py`: Core FastAPI app with endpoint and service integrations.
- `document_processor.py`: Handles PDF download, parsing, cleaning, and chunking.
- `vector_store.py`: Manages embedding and FAISS-based vector search.
- `groq_service.py`: Wraps Groq API calls for answer generation.
- `test_api.py`: Script for local API testing with sample data.
- `requirements.txt`: List of dependencies.
- `.env.template`: Template for environment variables (copy to `.env`).
- `.gitignore`: Excludes unnecessary files like venv and caches.

## Troubleshooting
- **Common Errors**:
- Connection refused: Ensure server is running before testing.
- 401 Unauthorized: Verify Authorization header/token.
- 500 Internal Error: Check Groq API key in `.env` or module imports.
- **Dependencies Issues**: Run `pip install -r requirements.txt` again if modules are missing.
- **Warnings**: Ignore FutureWarnings from libraries; they don't affect functionality.

## Notes for Reviewers
- The system is designed for accuracy, efficiency, and explainability per the problem statement.
- Tested with the provided sample PDF and questions—answers align with policy details (e.g., 30-day grace period).
- No real API keys included; use your own Groq key in `.env`.
- For questions, contact [your email/team contact].

Thank you for reviewing!
