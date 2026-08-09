import hashlib

from app.embeddings.provider import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    async def embed(
        self,
        text: str,
    ) -> list[float]:

        digest = hashlib.sha256(text.encode("utf-8")).digest()

        values = [byte / 255 for byte in digest]

        return (values * 48)[:1536]
