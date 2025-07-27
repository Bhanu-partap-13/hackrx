from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List


class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def create_index(self, chunks: List[str]):
        """
        Given a list of text chunks, embed them and create a FAISS index.
        Returns the FAISS index instance.
        """
        embeddings = self.model.encode(chunks).astype("float32")
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index

    def search_relevant_chunks(self, query: str, index: faiss.IndexFlatL2, chunks: List[str], top_k: int = 4) -> str:
        """
        Search the FAISS index for the query embedding, return the top_k matching chunks concatenated.
        """
        query_emb = self.model.encode([query]).astype("float32")
        distances, indices = index.search(query_emb, min(top_k, index.ntotal))
        results = []
        for idx in indices[0]:
            if idx < len(chunks):
                results.append(chunks[idx])
        return "\n\n".join(results)
