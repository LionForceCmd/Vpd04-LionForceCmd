"""Логика состояний и хранения выбранного города пользователя."""

from typing import Optional

from vkbottle import CtxStorage

storage = CtxStorage()

_CITY_KEY = "selected_city:{}"


def save_city(peer_id: int, city: str) -> None:
    """Запоминает последний выбранный пользователем город."""
    storage.set(_CITY_KEY.format(peer_id), city)


def get_last_city(peer_id: int) -> Optional[str]:
    """Возвращает последний выбранный пользователем город."""
    return storage.get(_CITY_KEY.format(peer_id))