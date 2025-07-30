import asyncio
import traceback
import warnings
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import os
from concurrent.futures import ProcessPoolExecutor

from document_processor import DocumentProcessor
from vector_store import VectorStore
from groq_service import GroqService

warnings.filterwarnings("ignore", category=Warning)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable missing")

app = FastAPI(title="HackRx 6.0 - LLM-Powered Intelligent Query System")
security =  HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    expected = "80952cdfb4fc8cfff557b6cb27c4c39b9c980c039093b1ec6047ebedba90a9d7"  
    if token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    return token

doc_processor = DocumentProcessor()
vector_store = VectorStore()
groq_service = GroqService(api_key=GROQ_API_KEY)

process_pool = ProcessPoolExecutor(max_workers=2)

doc_cache = {}

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

@app.post("/api/v1/hackrx", response_model=QueryResponse)
@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def hackrx_run(request: QueryRequest, token: str = Depends(verify_token)):
    print("\n--- Request received ---")
    loop = asyncio.get_event_loop()
    
    try:
        start_time = time.perf_counter()
        
        if request.documents in doc_cache:
            print("Document cache HIT")
            text, chunks, index = doc_cache[request.documents]
        else:
            print("Document cache MISS")
            text_start = time.perf_counter()
            text = await loop.run_in_executor(None, doc_processor.download_and_parse_pdf, request.documents)
            if not text:
                raise HTTPException(400, "Failed to extract document text")
            print(f"Downloaded PDF: {len(text)} chars in {time.perf_counter() - text_start:.2f} sec")
            
            chunk_start = time.perf_counter()
            chunks = await loop.run_in_executor(process_pool, doc_processor.clean_chunk_text, text)
            if not chunks:
                raise HTTPException(400, "Failed to chunk text")
            print(f"Chunked into {len(chunks)} in {time.perf_counter() - chunk_start:.2f} sec")
            
            idx_start = time.perf_counter()
            index = await loop.run_in_executor(process_pool, vector_store.create_index, chunks)
            print(f"Index created (dim={index.d}) in {time.perf_counter() - idx_start:.2f} sec")
            
            doc_cache[request.documents] = (text, chunks, index)
        
        print("Starting question processing...")
        sem = asyncio.Semaphore(5)
        
        async def process_question(q):
            async with sem:
                retrieval_start = time.perf_counter()
                relevant_chunks = await loop.run_in_executor(None, vector_store.search_relevant_chunks, q, index, chunks, 5)
                print(f"Retrieved {len(relevant_chunks)} chunks in {time.perf_counter() - retrieval_start:.2f} sec for question")
                
                answer_start = time.perf_counter()
                try:
                    answer = await loop.run_in_executor(None, groq_service.generate_answer, q, relevant_chunks)
                except Exception as e:
                    answer = f"Error generating answer: {e}"
                print(f"Generated answer in {time.perf_counter() - answer_start:.2f} sec")
                return answer
        
        answers = await asyncio.gather(*(process_question(q) for q in request.questions))
        total_time = time.perf_counter() - start_time
        print(f"All questions processed in {total_time:.2f} sec")

        return QueryResponse(answers=answers)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        raise HTTPException(500, str(e))


@app.get("/")
async def root():
    return {"status": "HackRx 6.0 API running"}

