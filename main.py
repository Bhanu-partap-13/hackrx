from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import PyPDF2
from io import BytesIO
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = FastAPI(title="HackRx 6.0 - LLM Document Query System")

# Initialize components
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

def download_and_parse_pdf(url: str) -> str:
    """Download and extract text from PDF URL"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            raise ValueError(f"Failed to download PDF: {response.status_code}")
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

def clean_and_chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Clean text and split into overlapping chunks"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?()-]', '', text)
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk) > 50:
            chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

def create_embeddings_and_index(chunks: List[str]):
    """Create FAISS index from text chunks"""
    if not chunks:
        raise ValueError("No chunks to embed")
    embeddings = embedding_model.encode(chunks)
    embeddings = np.array(embeddings).astype('float32')
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, chunks

def retrieve_relevant_chunks(query: str, index, chunks: List[str], top_k: int = 3) -> str:
    """Retrieve most relevant chunks for a query"""
    query_emb = embedding_model.encode([query])
    query_emb = np.array(query_emb).astype('float32')
    distances, indices = index.search(query_emb, min(top_k, len(chunks)))
    relevant = [chunks[idx] for idx in indices[0] if idx < len(chunks)]
    return "\n\n".join(relevant)

def generate_answer_with_groq(question: str, context: str) -> str:
    """Generate answer using Groq API"""
    try:
        prompt = f"""You are an expert document analyst. Based on the provided context from an insurance policy document, answer the question precisely and completely.

Context:
{context}

Question: {question}

Instructions:
1. Answer based ONLY on the information provided in the context
2. Be specific and include relevant details like time periods, amounts, conditions
3. If the context doesn't contain enough information, state that clearly
4. Use the exact terminology from the document
5. Keep the answer concise but complete

Answer:"""
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"

@app.get("/")
async def root():
    return {"message": "HackRx 6.0 Document Query System", "status": "running"}

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest):
    """Main endpoint for processing document queries"""
    try:
        # Step 1: Download and parse PDF
        document_text = download_and_parse_pdf(request.documents)
        if not document_text:
            raise ValueError("No text extracted from document")
        # Step 2: Chunk the text
        chunks = clean_and_chunk_text(document_text)
        if not chunks:
            raise ValueError("No valid chunks created from document")
        # Step 3: Create embeddings and FAISS index
        index, chunks = create_embeddings_and_index(chunks)
        # Step 4: Process each question
        answers = []
        for question in request.questions:
            relevant = retrieve_relevant_chunks(question, index, chunks, top_k=4)
            answer = generate_answer_with_groq(question, relevant)
            answers.append(answer)
        return QueryResponse(answers=answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
