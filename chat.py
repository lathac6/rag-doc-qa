from rag_core import answer_with_memory
history = []
while True:
    q = input('\n You:')
    if q.lower()=='quit':
        break
    result = answer_with_memory(q,history)
    print(f"(searched for: {result['standalone_question']})")
    print(f"Bot: {result['answer']}")
    