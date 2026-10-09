import os
import psycopg2
import numpy as np 
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def embed(text):
   result = genai.embed_content( model="models/gemini-embedding-001",content=text,output_dimensionality=768)
   vec = np.array(result["embedding"])
   return (vec / np.linalg.norm(vec)).tolist()
   
conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cur = conn.cursor()

docs = [
    "FastAPI is built on top of Starlette and Pydantic.",
    "PostgreSQL supports full-text search and JSON columns.",
]
for d in docs:
    vec = embed(d)
    print(len(vec))
    cur.execute(
        "INSERT INTO document (content, embedding) VALUES (%s, %s::vector)",
        (d, str(vec))
    )
conn.commit()
q = embed("What is FastAPI based on?")
cur.execute(
    "SELECT content, embedding <=> %s::vector AS distance FROM document ORDER BY distance LIMIT 1",
    (str(q),)
)
print(cur.fetchone())

cur.close()
conn.close()