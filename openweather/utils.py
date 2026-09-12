"""Вспомогательные функции модуля OpenWeather API."""

from datetime import datetime


def kelvin_to_celsius(temp: float) -> float:
    """Переводит температуру из Кельвинов в Цельсии."""
    return round(temp - 273.15, 1)


def format_timestamp(timestamp: int) -> str:
    """Форматирует Unix-время в удобный для чтения формат."""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M")


def windspeed_ms_to_kmh(speed_ms: float) -> float:
    """Переводит скорость ветра из м/с в км/ч."""
    return round(speed_ms * 3.6, 1)


def celsius_with_sign(temp_c: float) -> str:
    """Форматирует температуру со знаком плюс/минус."""
    return f"+{temp_c:.0f}°C" if temp_c >= 0 else f"{temp_c:.0f}°C"