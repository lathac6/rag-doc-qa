import os
import google.generativeai as genai
import psycopg2
from dotenv import load_dotenv
import numpy as np
from  google.api_core import exceptions as g_exceptions
import time

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cur = conn.cursor()
def chunk_text(text,chunk_size=500,overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start+chunk_size]
        if chunk:
           chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def embeding(text,retrial=3):
    for attempt in range(retrial):
        try:
            res = genai.embed_content(model='models/gemini-embedding-001',content=text,task_type='retrieval_document',output_dimensionality=768)
            vec = np.array(res["embedding"])
            return (vec/np.linalg.norm(vec)).tolist()
        except g_exceptions.ResourceExhausted:
            time.sleep(2 ** attempt) 
    raise RuntimeError('Embedding failed after retries')

def store_document(text):
    chunks = chunk_text(text)
    for i,chunk in enumerate(chunks,1):
        vec=embeding(chunk)
        cur.execute("INSERT INTO document (content, embedding) VALUES (%s, %s::vector)", (chunk,str(vec))) 
        print(f"Stored chunk {i}/{len(chunks)}")
    conn.commit()
    return len(chunks)

if __name__ == "__main__":
    with open('sample.txt',encoding='utf-8') as f:
        text = f.read()
    n = store_document(text)
    print(f"Done: {n} chunks stored")
    cur.close()
    conn.close()