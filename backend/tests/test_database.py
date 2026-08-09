from sqlalchemy import text


async def test_database_connection(db_session) -> None:
    result = await db_session.execute(text("SELECT 1"))

    assert result.scalar() == 1
