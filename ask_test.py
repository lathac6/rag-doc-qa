from rag_core import answer_question
tests = [
    "What does FastAPI use for request validation?",
    "When should I add the parmesan to risotto?",
    "Name the four Galilean moons.",
    "What port does Uvicorn run on by default?",
    "What is the capital of France?",
]

for q in tests:
    result = answer_question(q)
    print(f"\nQ: {q}")
    print(f"A: {result['answer']}")
    print(f"Sources used: {len(result['sources'])}")