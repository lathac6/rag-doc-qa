import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_core import conn, cur
from rag_safe import (
    answer_question_safe, store_document_safe,
    InvalidQuestion, InvalidDocument, ServiceError,
)

app = FastAPI(title="RAG Doc Q&A",description="Upload documents, then ask questions about them.",)
class QueryRequest(BaseModel):
    question: str

class DocumentRequest(BaseModel):
    text: str
class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/")
def home():
    try:
        cur.execute("SELECT COUNT(*) FROM document")
        return {"status": "running", "chunks_stored": cur.fetchone()[0]}
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=502, detail="Database unavailable")

@app.post("/ask", response_model=AnswerResponse)
def ask(req: QueryRequest):
    try:
        return answer_question_safe(req.question)
    except InvalidQuestion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/upload")
def upload(doc: DocumentRequest):
    try:
        n = store_document_safe(doc.text)
        return {"status": "stored", "chunks": n}
    except InvalidDocument as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))