from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


COLLECTION_NAME = "wiki_pages"


class VectorStore:
    def __init__(self, path: str, dimension: int = 1536):
        self.client = QdrantClient(path=path)
        self.dimension = dimension
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )

    def upsert(self, page_id: str, vector: list[float], metadata: dict):
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=self._hash_id(page_id), vector=vector, payload={"page_id": page_id, **metadata})],
        )

    def search(self, query_vector: list[float], top_k: int = 10) -> list[dict]:
        results = self.client.query_points(collection_name=COLLECTION_NAME, query=query_vector, limit=top_k).points
        return [{"id": hit.payload["page_id"], "score": hit.score, "metadata": {k: v for k, v in hit.payload.items() if k != "page_id"}} for hit in results]

    def delete(self, page_id: str):
        self.client.delete(collection_name=COLLECTION_NAME, points_selector=[self._hash_id(page_id)])

    def count(self) -> int:
        return self.client.count(collection_name=COLLECTION_NAME).count

    @staticmethod
    def _hash_id(page_id: str) -> int:
        import hashlib
        return int(hashlib.sha256(page_id.encode()).hexdigest()[:16], 16)


class Embedder:
    """Generate embeddings. Supports OpenAI API or local fastembed."""

    def __init__(self, api_key: str = "", model: str = "text-embedding-3-small", base_url: str = None, provider: str = "local"):
        self.provider = provider
        if provider == "local":
            from fastembed import TextEmbedding
            self._local_model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")
        else:
            import openai
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self.client = openai.OpenAI(**kwargs)
            self.model = model

    def embed(self, text: str) -> list[float]:
        if self.provider == "local":
            results = list(self._local_model.embed([text]))
            return results[0].tolist()
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "local":
            return [r.tolist() for r in self._local_model.embed(texts)]
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]
