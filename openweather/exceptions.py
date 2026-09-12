"""Пользовательские исключения для работы с OpenWeather API."""


class OpenWeatherAPIError(Exception):
    """Базовое исключение модуля OpenWeather API."""


class CityNotFoundError(OpenWeatherAPIError):
    """Город не найден по заданному названию."""


class APIConnectionError(OpenWeatherAPIError):
    """Проблема соединения с сервером OpenWeather API."""