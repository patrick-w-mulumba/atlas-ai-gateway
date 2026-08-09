from app.ingestion.loader import DocumentLoader


class TextLoader(DocumentLoader):
    async def load(
        self,
        content: bytes,
    ) -> str:
        return content.decode("utf-8")
