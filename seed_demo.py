"""Load four small demo documents so you can try the app straight away.

    python seed_demo.py            # add the demo documents
    python seed_demo.py --reset    # clear the table first, then add them

Running it twice without --reset stores every document twice.
"""
import sys
from rag_core import store_document, cur, conn

DEMO_DOCS = [
    "FastAPI is a modern Python web framework for building APIs. It uses type hints and "
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
    "slower writes and extra storage because the index is updated on every insert.",
]

if __name__ == "__main__":
    if "--reset" in sys.argv:
        cur.execute("DELETE FROM document")
        conn.commit()
        print("Cleared the document table.")
    total = sum(store_document(doc) for doc in DEMO_DOCS)
    print(f"Stored {len(DEMO_DOCS)} demo documents ({total} chunks).")
    cur.close()
    conn.close()