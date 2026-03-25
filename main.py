from ingestion import build_vector_store 
from retrieval import retrieve_context_multi 
from generation import expand_query, generate_answer 
 
if __name__ == "__main__": 
    vector_store = build_vector_store("data/uploads") 
 
    while True: 
        query = input("\nAsk a question (type 'exit' to quit): ") 
        if query.lower() == "exit": 
            break 
 
        expanded = expand_query(query) 
        context = retrieve_context_multi(vector_store, expanded) 
 
        if context is None: 
            print("Not found in document.") 
        else: 
            answer = generate_answer(context, query) 
            print("\nAnswer:\n", answer) 
