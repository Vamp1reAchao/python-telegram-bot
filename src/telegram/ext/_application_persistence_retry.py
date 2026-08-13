from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from telegram.ext._application import Application as _Application
from telegram.ext._utils.trackingdict import TrackingDict


class Application(_Application):
    """Application variant that retains persistence markers after failed writes."""

    __slots__ = ("__persistence_update_lock", "__persistence_update_failed")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__persistence_update_lock = asyncio.Lock()
        self.__persistence_update_failed = False

    async def process_error(
        self,
        update: object | None,
        error: Exception,
        job: Any = None,
        coroutine: Coroutine | None = None,
    ) -> bool:
        if update is None and self.__persistence_update_lock.locked():
            self.__persistence_update_failed = True
        return await super().process_error(update=update, error=error, job=job, coroutine=coroutine)

    async def update_persistence(self) -> None:
        async with self.__persistence_update_lock:
            chat_updates = self._chat_ids_to_be_updated_in_persistence.copy()
            chat_deletes = self._chat_ids_to_be_deleted_in_persistence.copy()
            user_updates = self._user_ids_to_be_updated_in_persistence.copy()
            user_deletes = self._user_ids_to_be_deleted_in_persistence.copy()
            conversation_updates = {
                name: set(states._write_access_keys)
                for name, states in self._conversation_handler_conversations.items()
                if isinstance(states, TrackingDict)
            }

            self.__persistence_update_failed = False
            await super().update_persistence()

            if not self.__persistence_update_failed:
                return

            self._chat_ids_to_be_updated_in_persistence.update(chat_updates)
            self._chat_ids_to_be_deleted_in_persistence.update(chat_deletes)
            self._user_ids_to_be_updated_in_persistence.update(user_updates)
            self._user_ids_to_be_deleted_in_persistence.update(user_deletes)
            for name, keys in conversation_updates.items():
                states = self._conversation_handler_conversations.get(name)
                if states is not None:
                    states._write_access_keys.update(keys)
