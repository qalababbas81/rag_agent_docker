def get_answer(vectorstore, question, k=6, fetch_k=15, lambda_mult=0.5):
    """
    MMR-based optimized retriever with:
    - diversity-aware search
    - configurable k and fetch_k
    - structured context formatting
    """
    print(f"DEBUG: Starting vector search for: {question}", flush=True) # Print 1
    try:
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": fetch_k,
                "lambda_mult": lambda_mult
            }
        )

        docs = retriever.invoke(question)
        print(f"DEBUG: Search finished. Found {len(docs)} docs.", flush=True) # Print 2

    except Exception as e:
        # Fallback to normal similarity search
        print(f"DEBUG: MMR failed, falling back. Error: {e}", flush=True)
        docs = vectorstore.similarity_search(question, k=k)

    if not docs:
        print("DEBUG: No docs found in vectorstore.", flush=True)
        return "No relevant context found."

    context = "\n\n".join(
        [
            f"Source {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(docs)
        ]
    )
    print("DEBUG: Context formatted, returning to generator.", flush=True) # Print 3
 
    return context

# def get_answer(vectorstore, question, k=4, score_threshold=None):
#     """
#     Optimized retriever with:
#     - configurable top-k
#     - optional score filtering
#     - structured context formatting
#     """

#     # If your vectorstore supports scores (FAISS/Chroma usually do)
#     try:
#         docs_and_scores = vectorstore.similarity_search_with_score(question, k=k)

#         if score_threshold is not None:
#             filtered = [
#                 doc for doc, score in docs_and_scores
#                 if score < score_threshold  # lower = better match (depends on backend)
#             ]
#         else:
#             filtered = [doc for doc, _ in docs_and_scores]

#     except:
#         # fallback if similarity_search_with_score not supported
#         filtered = vectorstore.similarity_search(question, k=k)

#     if not filtered:
#         return "No relevant context found."

#     # Structured formatting
#     context = "\n\n".join(
#         [f"Source {i+1}:\n{doc.page_content}"
#          for i, doc in enumerate(filtered)]
#     )

#     return context