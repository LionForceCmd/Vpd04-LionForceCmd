"""Связующее звено между VKBottle и модулем OpenWeather API.

Единственное место, где бот напрямую общается с погодным API.
"""

import logging
from typing import Any, Dict, List

from openweather.client import OpenWeatherAPI
from openweather.exceptions import CityNotFoundError, OpenWeatherAPIError

logger = logging.getLogger(__name__)

weather_api = OpenWeatherAPI()


def get_current_weather(city: str, extended: bool = False) -> Dict[str, Any]:
    """Запрашивает текущую погоду для города.

    Raises:
        OpenWeatherAPIError: при ошибках провайдера.
    """
    return weather_api.get_weather_by_city(city, extended=extended)


def get_forecast(city: str) -> Dict[str, Any]:
    """Запрашивает прогноз на 5 дней для города."""
    return weather_api.get_forecast_by_city(city)


def get_weather_by_coordinates(lat: float, lon: float, extended: bool = False) -> Dict[str, Any]:
    """Запрашивает текущую погоду по координатам."""
    return weather_api.get_weather_by_coordinates(lat, lon, extended=extended)


def build_error_text(error: Exception) -> str:
    """Превращает исключение в понятное сообщение для пользователя."""
    if isinstance(error, CityNotFoundError):
        return f"🤔 {error}"
    if isinstance(error, OpenWeatherAPIError):
        logger.exception("Ошибка OpenWeather API")
        return "😔 Погодный сервис временно недоступен. Попробуйте позже."
    logger.exception("Непредвиденная ошибка")
    return "😔 Что-то пошло не так. Попробуйте ещё раз."