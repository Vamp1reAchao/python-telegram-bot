import pytest

from telegram.ext import ApplicationBuilder, PersistenceInput
from tests.ext.test_basepersistence import TrackingPersistence


@pytest.mark.asyncio
async def test_failed_persistence_update_is_retried(one_time_bot, monkeypatch, caplog):
    persistence = TrackingPersistence(
        store_data=PersistenceInput(
            bot_data=False, chat_data=True, user_data=False, callback_data=False
        )
    )
    app = ApplicationBuilder().bot(one_time_bot).persistence(persistence).build()

    attempts = 0
    original_update_chat_data = persistence.update_chat_data

    async def update_chat_data(chat_id, data):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("transient persistence failure")
        await original_update_chat_data(chat_id, data)

    monkeypatch.setattr(persistence, "update_chat_data", update_chat_data)

    async with app:
        app.chat_data[1]["value"] = "persist me"
        app.mark_data_for_update_persistence(chat_ids=1)

        with caplog.at_level("ERROR"):
            await app.update_persistence()

        assert attempts == 1
        assert app._chat_ids_to_be_updated_in_persistence == {1}

        await app.update_persistence()

    assert attempts == 2
    assert persistence.updated_chat_ids == {1: 1}
