import asyncio
import concurrent.futures
from typing import List

class AsyncDocumentProcessor:
    def __init__(self, doc_processor, vector_store, groq_service):
        # Create thread pool and process pool for parallel tasks
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)  # I/O-heavy ops like downloading
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=2)  # CPU-heavy ops like embedding
        self.doc_processor = doc_processor
        self.vector_store = vector_store
        self.groq_service = groq_service

    async def run_in_threadpool(self, func, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args)

    async def run_in_processpool(self, func, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args)

    async def async_download_and_parse(self, url: str):
        return await self.run_in_threadpool(self.doc_processor.download_and_parse_pdf, url)

    async def async_chunk_text(self, text: str):
        return await self.run_in_threadpool(self.doc_processor.clean_and_chunk_text, text)

    async def async_create_index(self, chunks: List[str]):
        return await self.run_in_processpool(self.vector_store.create_index, chunks)

    async def async_search(self, index, chunks, question: str, top_k=5):
        return await self.run_in_threadpool(self.vector_store.search_relevant_chunks, question, index, chunks, top_k)

    async def async_generate_answer(self, question: str, context_chunks: List[str]):
        # This assumes groq_service.generate_answer is sync
        # We'll run it in threadpool to avoid blocking
        return await self.run_in_threadpool(self.groq_service.generate_answer, question, context_chunks)

    async def process_document_and_questions(self, url: str, questions: List[str]):
        # Step 1: Download and parse PDF (I/O bound)
        pdf_text = await self.async_download_and_parse(url)

        # Step 2: Chunk text (CPU/IO bound)
        chunks = await self.async_chunk_text(pdf_text)

        # Step 3: Create vector index (CPU intensive)
        index = await self.async_create_index(chunks)

        # Step 4: For each question, concurrently fetch relevant chunks and generate answers
        tasks = []
        for q in questions:
            task = self.process_single_question(q, index, chunks)
            tasks.append(task)

        answers = await asyncio.gather(*tasks)
        return answers

    async def process_single_question(self, question: str, index, chunks):
        # Search relevant chunks
        relevant_chunks = await self.async_search(index, chunks, question, top_k=5)
        # Generate answer
        answer = await self.async_generate_answer(question, relevant_chunks)
        return answer
