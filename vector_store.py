from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import torch
from typing import List

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        # Move model to GPU if available for speed up
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            self.model = self.model.half()  # Use half precision for speed if supported

    def create_index(self, chunks: List[str]):
        if not chunks:
            raise ValueError("No chunks to embed")
        
        print(f"DEBUG: Creating embeddings for {len(chunks)} chunks with batching...")

        # Generate embeddings in batches for efficiency
        embeddings = self.model.encode(
            chunks,
            batch_size=64,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")
        
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        print(f"DEBUG: FAISS index created with {index.ntotal} vectors, dimension {dim}")
        return index

    def search_relevant_chunks(self, query: str, index, chunks: List[str], top_k: int = 5) -> List[str]:
        query_emb = self.model.encode([query]).astype("float32")
        distances, indices = index.search(query_emb, min(top_k, len(chunks)))
        relevant_chunks = []
        for idx in indices[0]:
            if 0 <= idx < len(chunks):
                relevant_chunks.append(chunks[idx])
        print(f"DEBUG: Found {len(relevant_chunks)} relevant chunks out of {top_k} requested")
        return relevant_chunks
