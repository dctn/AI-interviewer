from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_texts(texts: List[str]) -> np.ndarray:
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings
