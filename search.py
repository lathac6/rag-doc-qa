import os
import numpy as np
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def embed_query(text):
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_query",
        output_dimensionality=768
    )
    vec = np.array(result["embedding"])
    return (vec / np.linalg.norm(vec)).tolist()

conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cur = conn.cursor()

question = "Write a question about your sample text here"
q = embed_query(question)

cur.execute(
    "SELECT content, embedding <=> %s::vector AS distance "
    "FROM document ORDER BY distance LIMIT 3",
    (str(q),)
)
for content, distance in cur.fetchall():
    print(f"{distance:.4f}  {content[:100]}...\n")