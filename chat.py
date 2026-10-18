import psycopg2
from rag_core import answer_with_memory, conn, ServiceError
from rag_safe import validate_question, InvalidQuestion

history = []
print("Ask questions about your documents. Type 'quit' to exit.")

while True:
    try:
        q = input("\nYou: ")
    except (EOFError, KeyboardInterrupt):
        break
    if q.strip().lower() == "quit":
        break

    try:
        q = validate_question(q)
        result = answer_with_memory(q, history)
    except InvalidQuestion as e:
        print(f"({e})")
        continue
    except ServiceError as e:
        print(f"(Something went wrong: {e})")
        continue
    except psycopg2.Error:
        conn.rollback()
        print("(Database error, please try again)")
        continue

    print(f"(searched for: {result['standalone_question']})")
    print(f"Bot: {result['answer']}")