from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def create_index(self, chunks: List[str]):
        if not chunks:
            raise ValueError("No chunks to embed")
        embeddings = self.model.encode(chunks).astype("float32")
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index  # Return both index and chunks for retrieval

    def search_relevant_chunks(self, query: str, index, chunks: List[str], top_k: int = 6) -> str:  # Increased to 6
        query_emb = self.model.encode([query]).astype("float32")
        distances, indices = index.search(query_emb, min(top_k, len(chunks)))
        relevant = [chunks[idx] for idx in indices[0] if idx < len(chunks)]
        return "\n\n".join(relevant)
