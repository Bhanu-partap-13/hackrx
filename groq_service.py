from groq import Groq

class GroqService:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def generate_answer(self, question: str, context: str) -> str:
        prompt = (
            "You are an insurance policy analyst. Answer ONLY based on the context.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\n"
            "If info is missing, say 'Not specified in the provided context'."
        )
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"
