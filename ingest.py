import sys
from rag_core import store_document, cur, conn

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample.txt"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    n = store_document(text)
    print(f"Done: {n} chunks stored from {path}")
    cur.close()
    conn.close()