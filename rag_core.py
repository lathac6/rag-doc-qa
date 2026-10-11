import os, psycopg2
from dotenv import load_dotenv
import google.generativeai as genai
from  google.api_core import exceptions as g_exceptions
import time
import numpy as np

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

conn = psycopg2.connect(os.getenv('SUPABASE_DB_URL'))
cur = conn.cursor()

def __embed(text,test_type,retrial= 3):

    for attempt in range(retrial):
        try:
            result = genai.embed_content(model='models/gemini-embedding-001',content=text,task_type=test_type,output_dimensionality=768)
            vec = np.array(result['embedding'])
            return (vec/np.linalg.norm(vec)).tolist()
        except g_exceptions.ResourceExhausted:
            time.sleep(attempt**2)
        raise RuntimeError('Embedding failed after retries')

def embed_document(text):
    return __embed(text,'retrieval_document')

def embed_query(text):
    return __embed(text,'retrieval_query')

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0 
    while start < len(text):
        chunk = text[start:start+chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def store_document(text):
    chunks = chunk_text(text)
    for chunk in chunks:
        cur.execute(
            "INSERT INTO document (content, embedding) VALUES (%s, %s::vector)",
            (chunk, str(embed_document(chunk))),
        )
    conn.commit()
    return len(chunks)

def retrival_chunks(query,k=3,with_scores=False):
    q=embed_query(query)
    cur.execute("SELECT content, embedding <=> %s::vector AS distance "
        "FROM document ORDER BY distance LIMIT %s",
        (str(q), k),
                 )
    rows = cur.fetchall()
    return rows if with_scores else [row[0] for row in rows]