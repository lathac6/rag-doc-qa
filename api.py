from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.api_core import exceptions as g_exceptions
from rag_core import answer_question


app = FastAPI(title="RAG Doc Q&A")

class Question(BaseModel):
    question: str
    
@app.post("/ask")
def ask(q: Question):
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        return answer_question(q.question)
    except (g_exceptions.GoogleAPIError, RuntimeError):
        raise HTTPException(status_code=502, detail="AI service failed")