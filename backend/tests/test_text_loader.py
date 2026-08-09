import pytest
from app.ingestion.text_loader import TextLoader


@pytest.mark.asyncio
async def test_text_loader_decodes_utf8() -> None:
    loader = TextLoader()

    result = await loader.load(
        b"Hello Atlas",
    )

    assert result == "Hello Atlas"
