from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata: List[Dict] = []

    def add(self, docs: List[Dict]) -> None:
        texts = [d["content"] for d in docs]
        embs = self.model.encode(texts)
        embs = np.array(embs, dtype="float32")
        self.index.add(embs)
        self.metadata.extend(docs)

    def search(self, query: str, top_k: int = 4) -> List[Dict]:
        q_emb = self.model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, min(top_k, self.index.ntotal))
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.metadata):
                m = self.metadata[idx].copy()
                m["score"] = float(dist)
                results.append(m)
        return results
