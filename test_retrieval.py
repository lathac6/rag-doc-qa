from rag_core import conn,cur,store_document,retrival_chunks

paragraphs = [ "FastAPI is a modern Python web framework for building APIs. It uses type hints and "
    "Pydantic for automatic request validation, and generates interactive Swagger "
    "documentation at /docs. It runs on an ASGI server such as Uvicorn.",

    "To make a good risotto, toast the arborio rice in butter before adding liquid. Add "
    "warm stock one ladle at a time, stirring often so the starch releases and creates a "
    "creamy texture. Finish with parmesan off the heat.",

    "Jupiter is the largest planet in the solar system, a gas giant with a Great Red Spot "
    "storm that has raged for centuries. It has dozens of known moons, including the four "
    "large Galilean moons Io, Europa, Ganymede, and Callisto.",

    "A database index is a data structure that speeds up lookups by avoiding a full table "
    "scan. B-tree indexes handle equality and range queries well, but the trade-off is "
    "slower writes and extra storage because the index is updated on every insert.",]

cur.execute("DELETE FROM document;")
conn.commit()

for p in paragraphs:
    store_document(p)
    
queries = [
    "How do I cook a creamy rice dish?",
    "Which planet is the biggest?",
    "How can I make my queries run faster?",
    "How do I validate request data in Python?",
    "What is the capital of France?",
]
for q in queries:
    print(f"\nQ: {q}")
    for content, dist in retrival_chunks(q, k=3, with_scores=True):
        print(f"  {dist:.4f}  {content[:70]}...")