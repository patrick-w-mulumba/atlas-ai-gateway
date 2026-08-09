import hashlib

from app.core.config import get_settings
from app.embeddings.provider import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    async def embed(
        self,
        text: str,
    ) -> list[float]:
        settings = get_settings()

        digest = hashlib.sha256(text.encode("utf-8")).digest()

        values = [byte / 255 for byte in digest]

        repetitions = settings.embedding_dimensions // len(values)

        return (values * repetitions)[: settings.embedding_dimensions]
