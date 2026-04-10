from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from app.embeddings.embedder import embed_texts


def retrieve_top_k_chunks_with_scores(
    query_text: str,
    chunks: List[str],
    top_k: int = 3
) -> List[Tuple[str, float]]:
    if not chunks:
        return []

    chunk_embeddings = embed_texts(chunks)
    query_embedding = embed_texts([query_text])

    scores = cosine_similarity(query_embedding, chunk_embeddings)[0]
    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return scored_chunks[:top_k]