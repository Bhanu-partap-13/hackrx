from groq import Groq
import time


class GroqService:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama3-70b-8192"  # Better model for accuracy

    def generate_answer(self, question: str, context_chunks: list) -> str:
        if not context_chunks:
            return "Not specified in the provided context."

        max_context_chars = 6000
        selected_context = []
        total_chars = 0

        for chunk in context_chunks[:8]:  # Limit chunks included for context
            if total_chars + len(chunk) <= max_context_chars:
                selected_context.append(chunk)
                total_chars += len(chunk)
            else:
                remaining = max_context_chars - total_chars
                if remaining > 200:
                    selected_context.append(chunk[:remaining] + "...")
                break

        context_text = "\n\n---\n\n".join(selected_context)

        prompt = f"""You are an expert insurance policy analyst. Answer the question very briefly and concisely using ONLY the provided policy document excerpts.

POLICY DOCUMENT EXCERPTS:
{context_text}

QUESTION: {question}

INSTRUCTIONS:
1. Provide a short answer, no longer than 2-3 sentences.
2. Include only essential details, e.g. exact numbers, time periods, and conditions.
3. Use the exact terminology and cite important clauses if possible.
4. If the answer is not in the provided context, respond with "Not specified in the provided context."
5. Do NOT add extra explanations or long descriptions.

SHORT ANSWER:"""

        try:
            print(f"DEBUG: Prompt length: {len(prompt)} characters")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise insurance policy analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=200,  # Lower max tokens to encourage brevity
                top_p=1,
                stream=False,
            )
            answer = response.choices[0].message.content.strip()

            # Clean answer from common prefixes
            for prefix in ["SHORT ANSWER:", "Answer:", "ANSWER:"]:
                if answer.startswith(prefix):
                    answer = answer[len(prefix):].strip()

            return answer

        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            print(f"ERROR: {error_msg}")
            return error_msg
