"""Обработчик геолокации: погода по координатам."""

import logging
import re

from vkbottle.bot import Message

from bot.bot import bot
from bot.keyboards.navigation_keyboard import get_navigation_keyboard
from bot.services.formatter import format_weather
from bot.services.weather_service import build_error_text, get_weather_by_coordinates
from bot.states import States

logger = logging.getLogger(__name__)

GEO_BUTTON = "📍 Геолокация"

# Поддерживаемые форматы: "55.7558, 37.6173" и "55.7558 37.6173"
_COORDS_PATTERN = re.compile(r"^\s*([-+]?\d{1,3}(?:[.,]\d+)?)\s*[,;\s]\s*([-+]?\d{1,3}(?:[.,]\d+)?)\s*$")


def parse_coordinates(text: str):
    """Разбирает текст сообщения на координаты (широту и долготу)."""
    match = _COORDS_PATTERN.match(text)
    if not match:
        return None
    lat = float(match.group(1).replace(",", "."))
    lon = float(match.group(2).replace(",", "."))
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None
    return lat, lon


def _message_has_geo(message: Message) -> bool:
    """Проверяет, приложена ли к сообщению геолокация VK."""
    return bool(getattr(message, "geo", None))


@bot.on.message(text=[GEO_BUTTON])
async def geo_button(message: Message) -> None:
    """Кнопка «Геолокация»: просим прикрепить точку или ввести координаты."""
    await bot.state_dispenser.set(message.peer_id, States.WAITING_GEO)
    await message.answer(
        "📍 Прикрепите геолокацию или отправьте координаты "
        "в формате: 55.7558, 37.6173",
        keyboard=get_navigation_keyboard(),
    )


@bot.on.message(state=States.WAITING_GEO, func=_message_has_geo)
async def geo_attachment_handler(message: Message) -> None:
    """Обрабатывает прикреплённую к сообщению геолокацию."""
    await bot.state_dispenser.delete(message.peer_id)
    try:
        geo = message.geo.coordinates
        data = get_weather_by_coordinates(geo.latitude, geo.longitude)
    except Exception as error:
        await message.answer(build_error_text(error), keyboard=get_navigation_keyboard())
        return
    await message.answer(format_weather(data), keyboard=get_navigation_keyboard())


@bot.on.message(state=States.WAITING_GEO)
async def geo_coordinates_handler(message: Message) -> None:
    """Обрабатывает координаты, введённые текстом."""
    coords = parse_coordinates(message.text)
    if coords is None:
        await message.answer(
            "😕 Не удалось распознать координаты. Пришлите точку на карте "
            "или текст вида «55.7558, 37.6173»."
        )
        return
    await bot.state_dispenser.delete(message.peer_id)
    try:
        data = get_weather_by_coordinates(*coords)
    except Exception as error:
        await message.answer(build_error_text(error), keyboard=get_navigation_keyboard())
        return
    await message.answer(format_weather(data), keyboard=get_navigation_keyboard())