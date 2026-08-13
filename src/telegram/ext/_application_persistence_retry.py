from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from telegram.ext._application import Application as _Application
from telegram.ext._utils.trackingdict import TrackingDict


class Application(_Application):
    """Application variant that retains persistence markers after failed writes."""

    __slots__ = (
        "__persistence_update_lock",
        "__persistence_update_failed",
        "__persistence_update_active",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__persistence_update_lock = asyncio.Lock()
        self.__persistence_update_failed = False
        self.__persistence_update_active = False
