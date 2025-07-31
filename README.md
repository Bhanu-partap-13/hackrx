# HackRx 6.0 - Intelligent Document Retrieval System

Welcome to the **HackRx 6.0** AI-powered document retrieval system! This repository provides a FastAPI-based API for extracting answers from large PDF documents using text chunking, semantic search with sentence transformers, and LLM-powered answer generation via Groq.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Environment Configuration](#environment-configuration)
- [Running Locally](#running-locally)
- [Exposing Your API via Ngrok](#exposing-your-api-via-ngrok)
- [Testing the API](#testing-the-api)
- [HackRx Submission Guidelines](#hackrx-submission-guidelines)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [References](#references)
- [License](#license)

---

## Features

- Download and parse large PDF documents from URLs.
- Clean and chunk text with semantic-aware sentence splitting.
- Produce vector embeddings with fast SentenceTransformers models.
- Perform efficient semantic search using FAISS index.
- Generate concise, accurate answers using Groq LLM API with prompt engineering.
- Async concurrency and caching for fast performance.
- Secure API with Bearer token authentication.

---

## Prerequisites

- Python 3.9+ (3.10+ recommended)
- pip package manager
- (Optional) CUDA-enabled GPU to accelerate embeddings
- Ngrok (optional, to expose local server publicly)
- Groq API key (provided by HackRx)

---

## Setup & Installation

### 1. Clone the repo

```sh
git clone https://github.com/Bhanu-partap-13/hackrx
cd hackrx_project_folder
```

### 2. Create and activate a virtual environment

#### Windows PowerShell

```sh
python -m venv hackrx_env
.\hackrx_env\Scripts\Activate.ps1
```

#### Linux/MacOS

```sh
python3 -m venv hackrx_env
source hackrx_env/bin/activate
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

**Key libraries installed:**

- `fastapi`
- `uvicorn[standard]`
- `sentence-transformers`
- `faiss-cpu`
- `torch` (for embeddings, GPU optional)
- `python-dotenv`
- `requests`
- `PyPDF2`
- `nltk`
- `groq`

### 4. Download NLTK tokenizer models (Run once)

In a python shell or script, run:

```python
import nltk
nltk.download('punkt')
```

---

## Environment Configuration

Create a `.env` file in your project root directory with your Groq API key:

```env
GROQ_API_KEY=<your_groq_api_key_here>
```

Replace `<your_groq_api_key_here>` with your actual API key received from the HackRx Groq platform.

---

## Running Locally

Start your FastAPI server using uvicorn:

```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 --loop uvloop --reload
```

- `--workers` specifies parallel worker instances (choose based on CPU cores).
- `--loop uvloop` for improved async performance (Linux/Mac recommended).

Your API will be accessible at:
`http://localhost:8000`

---

## Exposing Your API via Ngrok

To make your local API publicly accessible (for HackRx evaluation or testing):

1. Download and install [ngrok](https://ngrok.com/).
2. Launch ngrok to forward your local port:

```sh
ngrok http 8000
```

3. Copy the **HTTP** URL generated (e.g., `http://abcd1234.ngrok.io`).

> **Important:** Use HTTP URL during testing to avoid TLS `BAD_DECRYPT` errors. HTTPS tunnels may cause TLS handshake issues without proper cert setup.

4. Update your test script or HackRx submission to point to this ngrok URL.

---

## Testing the API

Use the provided `test_api.py` or tools like Postman with this sample POST request:

- **Endpoint:**
  `http://localhost:8000/api/v1/hackrx/run`

- **Headers:**
  Authorization: Bearer <YOUR_TOKEN_HERE>
  Content-Type: application/json

- **Body:**
  ```json
  {
    "documents": "<URL_of_policy_pdf>",
    "questions": [
      "What is the grace period for premium payment?",
      "Does the policy cover maternity expenses?"
    ]
  }
  ```

Replace `<URL_of_policy_pdf>` with your desired document URL.

---

## HackRx Submission Guidelines

- Your API endpoint **must accept POST** at `/api/v1/hackrx/run` with JSON body containing `documents` (PDF URL) and `questions` (array of strings).
- Use the exact **Bearer token** given in the code for authentication.
- Return an array of answers corresponding to questions in the response.
- Ensure your FastAPI server is always running and accessible (via ngrok or publicly hosted).
- Follow API contract precisely for smooth HackRx evaluation.

---

## Project Structure

```
.
├── main.py                # FastAPI entrypoint & API endpoint
├── document_processor.py  # PDF download & text chunking
├── vector_store.py        # Embeddings & FAISS search
├── groq_service.py        # LLM answer generation via Groq
├── test_api.py            # Sample testing script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (api keys)

```

---

## Troubleshooting

- **Invalid Token:** Make sure the Authorization header token exactly matches the one in `main.py`.
- **Slow Response Times:** Use in-memory caching and run with multiple uvicorn workers. Consider GPU acceleration.
- **TLS Errors with ngrok:** Use the HTTP ngrok forwarding URL during testing.
- **NLTK Errors:** Make sure `nltk` is installed and `'punkt'` tokenizer is downloaded.
- **Timeouts:** Increase uvicorn worker counts or adjust timeouts as needed.

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Server](https://www.uvicorn.org/)
- [Ngrok Docs](https://ngrok.com/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS Library](https://github.com/facebookresearch/faiss)
- [Groq.ai API Docs](https://docs.groq.ai/)
- [NLTK Tokenizer](https://www.nltk.org/api/nltk.tokenize.html)

---

## Github Family

Feel free to raise issues or contribute improvements!
Happy coding and good luck with HackRx 6.0 🎉
