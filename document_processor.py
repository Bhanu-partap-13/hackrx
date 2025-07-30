import nltk
import requests
import re
import time
from typing import List
from io import BytesIO
import PyPDF2

# Download this once in your environment (remove from prod code if needed)
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize

class DocumentProcessor:
    def download_and_parse_pdf(self, url: str, retries: int = 3, delay: int = 2) -> str:
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                pdf_file = BytesIO(response.content)
                reader = PyPDF2.PdfReader(pdf_file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + "\n" if page.extract_text() else ''
                return text.strip()
            except Exception as e:
                if attempt == retries -1:
                    raise
                time.sleep(delay)

    def clean_chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        print("Starting cleaning and chunking of text...")
        start_time = time.time()

        # Clean the text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?():\-–—%$]', '', text)
        text = text.strip()

        print(f"Cleaned text length: {len(text)} chars")
        clean_done = time.time()

        # Use nltk sentence tokenizer
        sentences = sent_tokenize(text)

        chunks = []
        current_chunk = ''
        for sent in sentences:
            if len(current_chunk) + len(sent) + 1 <= chunk_size:
                current_chunk = current_chunk + ' ' + sent if current_chunk else sent
            else:
                if len(current_chunk.split()) >= 10:
                    chunks.append(current_chunk.strip())
                overlap_words = current_chunk.split()[-20:] if current_chunk else []
                current_chunk = ' '.join(overlap_words) + ' ' + sent if overlap_words else sent
        if current_chunk and len(current_chunk.split()) >= 10:
            chunks.append(current_chunk.strip())

        done_time = time.time()
        print(f"Chunking took {done_time - clean_done:.2f} seconds")
        print(f"Created {len(chunks)} chunks with average size {sum(len(c) for c in chunks) / len(chunks):.0f} chars")

        return chunks
