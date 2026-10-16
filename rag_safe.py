import psycopg2
from rag_core import (
    conn, cur, answer_question, store_document,
    ServiceError, with_retry,       # re-exported so other files can import them from here
)

MAX_QUESTION_CHARS = 1000
MAX_UPLOAD_CHARS = 20_000


class InvalidQuestion(ValueError):
    """Bad input from the caller (maps to HTTP 400)."""

class InvalidDocument(ValueError):
    """Bad upload from the caller (maps to HTTP 400)."""

def validate_question(q):
    q = (q or "").strip()
    if not q:
        raise InvalidQuestion("Please enter a question.")
    if not any(ch.isalnum() for ch in q):
        raise InvalidQuestion("The question needs some letters or numbers.")
    if len(q) > MAX_QUESTION_CHARS:
        raise InvalidQuestion(f"Question is too long (max {MAX_QUESTION_CHARS} characters).")
    return q


def validate_document(text):
    text = (text or "").strip()
    if not text:
        raise InvalidDocument("Document text cannot be empty.")
    if len(text) > MAX_UPLOAD_CHARS:
        raise InvalidDocument(f"Document too large (max {MAX_UPLOAD_CHARS} characters).")
    return text


def has_documents():
    try:
        cur.execute("SELECT EXISTS (SELECT 1 FROM document)")
        return cur.fetchone()[0]
    except psycopg2.Error:
        conn.rollback()                     # un-stick the shared connection
        raise ServiceError("Database error")


def answer_question_safe(query):
    query = validate_question(query)
    if not has_documents():
        return {"answer": "No documents have been added yet.", "sources": []}
    try:
        return answer_question(query)       # one pipeline, no duplicated logic
    except psycopg2.Error:
        conn.rollback()
        raise ServiceError("Database error while searching")


def store_document_safe(text):
    text = validate_document(text)
    try:
        return store_document(text)
    except psycopg2.Error:
        conn.rollback()
        raise ServiceError("Database error while storing the document")
    except ServiceError:
        conn.rollback()                     # discard chunks inserted before the failure
        raise