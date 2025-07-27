import requests
from io import BytesIO
import PyPDF2
import re
from typing import List

class DocumentProcessor:
    def download_and_parse_pdf(self, url: str) -> str:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            raise ValueError(f"Failed to download PDF: HTTP {response.status_code}")
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()

    def clean_and_chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        # Clean text: normalize spaces and remove unwanted chars but keep basic punctuation
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s.,!?()-]", "", text)

        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i+chunk_size]
            if len(chunk_words) > 50:  # minimal chunk size check
                chunks.append(" ".join(chunk_words))
            if i + chunk_size >= len(words):
                break
        return chunks
