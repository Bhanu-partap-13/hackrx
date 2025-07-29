from groq import Groq

class GroqService:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama3-8b-8192"  # Or try "mixtral-8x7b-32768" for better accuracy if tokens allow

    def generate_answer(self, question: str, context: str) -> str:
        if not context:
            return "Not specified in the provided context."
        prompt = f"""You are an expert insurance policy analyst. Answer the question PRECISELY using ONLY the provided context. Cite exact clauses, numbers, periods, conditions, or definitions word-for-word where possible. Be concise but complete. If the information is not explicitly in the context, say 'Not specified in the provided context'.

Context:
{context}

Question: {question}
"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.1,  # Low for precision
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"
