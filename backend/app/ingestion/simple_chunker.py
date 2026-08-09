from app.ingestion.chunker import Chunker


class SimpleChunker(Chunker):
    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(
        self,
        text: str,
    ) -> list[str]:
        if not text:
            return []

        chunks: list[str] = []

        start = 0

        while start < len(text):
            end = start + self._chunk_size

            chunks.append(text[start:end])

            start = end - self._overlap

        return chunks
