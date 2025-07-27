import os
from groq import Groq
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    def __init__(self, model: str = "llama3-8b-8192"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model

    def answer(self, question: str, contexts: List[Dict]) -> str:
        context_text = ""
        for i, c in enumerate(contexts, 1):
            context_text += f"[Context {i}]: {c['content']}\n"
        prompt = (
            "You are an expert document analyst. Answer based only on the contexts.\n\n"
            f"Contexts:\n{context_text}\n"
            f"Question: {question}\n\n"
            "Answer with specific details and cite context indices."
        )
        resp = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.1,
            max_tokens=300
        )
        return resp.choices[0].message.content.strip()
