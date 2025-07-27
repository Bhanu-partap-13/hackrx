# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import warnings

from document_processor import DocumentProcessor
from vector_store import VectorStore
from groq_service import GroqService

warnings.filterwarnings("ignore", category=FutureWarning)
# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable must be set in .env")

# Initialize FastAPI app
app = FastAPI(title="HackRx 6.0 - LLM-Powered Intelligent Query-Retrieval System")

# HTTP Bearer Auth scheme for Swagger/OpenAPI
security = HTTPBearer()

# Token validation dependency
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    expected_token = "80952cdfb4fc8cfff557b6cb27c4c39b9c980c039093b1ec6047ebedba90a9d7"
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    return token

# Initialize service instances
doc_processor = DocumentProcessor()
vector_store = VectorStore()
groq_service = GroqService(api_key=GROQ_API_KEY)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

# API endpoint matching spec with security dependency
@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def hackrx_run(request: QueryRequest, token: str = Depends(verify_token)):
    try:
        # Step 1: Download and parse PDF text
        raw_text = doc_processor.download_and_parse_pdf(request.documents)

        if not raw_text:
            raise HTTPException(status_code=400, detail="Failed to extract text from document")

        # Step 2: Clean and chunk text
        chunks = doc_processor.clean_and_chunk_text(raw_text)
        if not chunks:
            raise HTTPException(status_code=400, detail="Document could not be chunked")

        # Step 3: Create vector index
        index = vector_store.create_index(chunks)

        # Step 4: For each question, retrieve relevant chunks and generate answer
        answers = []
        for question in request.questions:
            context = vector_store.search_relevant_chunks(question, index, chunks, top_k=4)
            answer = groq_service.generate_answer(question, context)
            answers.append(answer)

        return QueryResponse(answers=answers)

    except Exception as e:
        # For debugging, optionally replace with logging
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Optional: Add a root GET endpoint to confirm service is running
@app.get("/")
async def root():
    return {"message": "HackRx 6.0 LLM Query-Retrieval System is running."}
