def retrieve_context_multi(vector_store, queries, k=3, max_distance=2.0):
    all_chunks = {}

    for query in queries:
        results = vector_store.similarity_search_with_score(query, k=k)

        for doc, score in results:
            if score <= max_distance:
                all_chunks[doc.page_content] = score

    if not all_chunks:
        return None

    sorted_chunks = sorted(all_chunks.items(), key=lambda x: x[1])
    return "\n\n".join(chunk for chunk, _ in sorted_chunks[:5])
