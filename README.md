<<<<<<< HEAD
# RAG Document Q&A

A Retrieval-Augmented Generation (RAG) application that lets users upload text documents and ask questions about their content. It creates embeddings with Google's Gemini API, stores document chunks in Supabase PostgreSQL with pgvector, retrieves relevant chunks using cosine distance, and generates answers grounded in the retrieved context.

## Features

- **Document ingestion:** Load text from a file or upload text through the API.
- **Chunking:** Split text into chunks of 500 characters with a 50-character overlap.
- **Embeddings:** Create 768-dimensional embeddings using `gemini-embedding-001`.
- **Semantic retrieval:** Search stored vectors with pgvector's cosine-distance operator (`<=>`).
- **Context-grounded answers:** Generate answers with `gemini-3.6-flash`, instructing the model to answer from the supplied document context.
- **Conversation memory:** Rewrite follow-up questions into standalone questions and keep recent chat history in the command-line chat flow.
- **Input validation and error handling:** Reject empty or overly long questions/documents and retry selected temporary Gemini API errors.
- **REST API:** Expose health, document-upload, and question-answering endpoints through FastAPI.

## Tech Stack

- Python
- FastAPI and Pydantic
- Google Gen AI SDK (Gemini)
- Supabase PostgreSQL
- pgvector
- NumPy
- psycopg2
- python-dotenv
- Uvicorn

## How the RAG Pipeline Works

1. **Ingest:** Read document text or receive text through `/upload`.
2. **Chunk:** Split the text into smaller overlapping chunks.
3. **Embed:** Convert each chunk into a normalized 768-dimensional vector.
4. **Store:** Save each chunk and its vector in the PostgreSQL `document` table.
5. **Retrieve:** Embed the user's question and rank stored chunks by cosine distance.
6. **Filter:** Keep retrieved chunks whose distance is at or below the configured `MAX_DISTANCE` threshold.
7. **Generate:** Send the question and relevant context to Gemini to generate a grounded answer. If no relevant context passes the threshold, return a not-found response.

## Project Structure

```text
rag-doc-qa/
├── api.py             # FastAPI endpoints
├── rag_core.py        # Chunking, embeddings, retrieval, answer generation, chat memory
├── rag_safe.py        # Input validation and safer service wrappers
├── ingest.py          # Ingest a local text file
├── seed_demo.py       # Add four built-in demo documents
├── chat.py            # Interactive command-line chat with history
├── ask_test.py        # Example question-answering checks
├── edge_tests.py      # Input and retry/error-handling checks
├── check_db.py        # Check database connectivity
├── sample.txt         # Sample source text
├── .env               # Local secrets; do not commit
└── .gitignore
```

## Prerequisites

- Python 3.10+ (use a Python version supported by your installed dependencies).
- A Google Gemini API key.
- A Supabase PostgreSQL database with the `vector` extension enabled.
- A `document` table whose vector dimension matches the application's `DIMS = 768` setting.

Enable pgvector and create the table in the Supabase SQL Editor:

```sql
create extension if not exists vector;

create table if not exists document (
    id bigserial primary key,
    content text not null,
    embedding vector(768) not null
);
```

If you already have a `document` table, check its schema before running this SQL. Do not delete an existing table or data just to recreate it.

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python directly, for example `.\env\Scripts\python.exe -m pip install ...`.

### 2. Install dependencies

```powershell
python -m pip install fastapi uvicorn google-genai psycopg2-binary numpy python-dotenv
```

### 3. Configure environment variables

Create a local `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_DB_URL=your_supabase_postgresql_connection_string
```

Keep real credentials private. The `.env` file should remain excluded from Git.

### 4. Check the database connection

```powershell
python check_db.py
```

A successful connection prints `(1,)`. If it fails, verify the database URL, credentials, network access, and Supabase connection settings.

## Run the Project

### Option A: Load the sample document

```powershell
python ingest.py
```

By default, this reads `sample.txt`. To ingest another text file:

```powershell
python ingest.py path\to\your_document.txt
```

### Option B: Load built-in demo documents

```powershell
python seed_demo.py
```

This adds four small documents covering FastAPI, risotto, Jupiter's Galilean moons, and database indexes. Running it repeatedly inserts duplicates. The optional `--reset` flag clears the `document` table first, so **use it only if you intentionally want to delete all existing stored chunks**:

```powershell
python seed_demo.py --reset
```

### Start the API

```powershell
uvicorn api:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the interactive Swagger UI. The API runs locally with this command; a public deployment requires a separate hosting and configuration step.

## API Endpoints

### `GET /`

Checks that the API can query the database and returns the number of stored chunks.

Example response:

```json
{
  "status": "running",
  "chunks_stored": 4
}
```

The number above is illustrative; the actual count depends on your database.

### `POST /upload`

Stores and embeds document text.

Request:

```json
{
  "text": "FastAPI uses Pydantic for automatic request validation."
}
```

Example response:

```json
{
  "status": "stored",
  "chunks": 1
}
```

### `POST /ask`

Asks a question about the stored documents.

Request:

```json
{
  "question": "What does FastAPI use for request validation?"
}
```

Example response (illustrative):

```json
{
  "answer": "FastAPI uses Pydantic for automatic request validation.",
  "sources": [
    "FastAPI is a modern Python web framework ... Pydantic for automatic request validation ..."
  ]
}
```

Answers depend on which documents have been ingested and which chunks pass the configured similarity threshold.

## Command-Line Examples

Ask a set of predefined questions:

```powershell
python ask_test.py
```

Start an interactive chat with follow-up-question handling:

```powershell
python chat.py
```

Type `quit` to exit the chat.

Run the input-validation and retry/error-handling checks:

```powershell
python edge_tests.py
```

**Note:** `edge_tests.py` includes a test that temporarily deletes rows inside a transaction and then rolls back. Run tests against a development database, not a production database. Review the test before running it against any database with important data.

## Current Limitations

- The current upload endpoint accepts text in the request body; it does not upload PDF or Word files directly.
- Document chunks are stored without document-level identifiers, so the returned sources are text chunks rather than document names or page numbers.
- The similarity threshold (`MAX_DISTANCE = 0.6`) is a configurable starting point and should be evaluated against representative relevant and irrelevant questions.
- The project uses a shared database connection/cursor in module scope; production deployment should review connection lifecycle and concurrency handling.
- This repository does not currently include automated deployment configuration or a frontend UI.

## Future Improvements

- Add document IDs, filenames, and source metadata.
- Support PDF and DOCX ingestion.
- Add authentication, rate limiting, and upload authorization.
- Evaluate retrieval quality and tune the similarity threshold.
- Add production-ready database connection pooling and automated tests.
- Deploy the API to a hosting service and document the live URL once deployment is complete.

## Security

Never commit `.env`, API keys, database passwords, or connection strings. If credentials have been exposed, rotate them and update your local environment variables before using or publishing the project.

## Author

Add your name and GitHub profile here.
