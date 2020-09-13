from stackexchange_app import data_manager as dm
import pytest


@pytest.mark.asyncio
async def test_save_topic(postgres_engine):
    async with postgres_engine.acquire() as conn:
        topic = {
            'topic': 'python',
            'questions_count': 25
        }
        result = await dm.save_topic(conn, topic)
        assert result is not None
