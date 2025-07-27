import PyPDF2
from docx import Document as DocxDocument
from email import message_from_string
import re
from io import BytesIO
from typing import List, Dict

class DocumentProcessor:
    def __init__(self, chunk_size: int = 600, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def extract_text_from_pdf(self, content: bytes) -> str:
        pdf = BytesIO(content)
        reader = PyPDF2.PdfReader(pdf)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def extract_text_from_docx(self, content: bytes) -> str:
        doc = DocxDocument(BytesIO(content))
        text = ""
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
        return text

    def extract_text_from_email(self, raw: str) -> str:
        msg = message_from_string(raw)
        parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    parts.append(part.get_payload(decode=True).decode(errors="ignore"))
        else:
            parts.append(msg.get_payload(decode=True).decode(errors="ignore"))
        return "\n".join(parts)

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?()-]', '', text)
        return text.strip()

    def chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i : i + self.chunk_size])
            if len(chunk) > 50:
                chunks.append(chunk)
            if i + self.chunk_size >= len(words):
                break
        return chunks

    def process(self, filename: str, content: bytes) -> List[Dict]:
        ext = filename.lower().split('.')[-1]
        if ext == "pdf":
            raw = self.extract_text_from_pdf(content)
        elif ext == "docx":
            raw = self.extract_text_from_docx(content)
        elif ext in ("eml", "txt"):
            raw = self.extract_text_from_email(content.decode(errors="ignore"))
        else:
            raise ValueError(f"Unsupported extension: {ext}")
        cleaned = self.clean_text(raw)
        chunks = self.chunk_text(cleaned)
        return [{"filename": filename, "chunk_id": f"{filename}_{i}", "content": c}
                for i, c in enumerate(chunks)]
