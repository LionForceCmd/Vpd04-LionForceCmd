"""Основной клиент для работы с OpenWeather API.

Содержит только логику взаимодействия с API OpenWeatherMap:
текущая погода, прогноз на 5 дней, геокодинг и качество воздуха.
Не зависит от логики бота и может использоваться из консоли или любым frontend.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from openweather.config import OPENWEATHER_API_KEY
from openweather.exceptions import APIConnectionError, CityNotFoundError, OpenWeatherAPIError
from openweather.utils import kelvin_to_celsius, format_timestamp

TIMEOUT = 15


class OpenWeatherAPI:
    """OOP-клиент над публичным API OpenWeatherMap."""

    # Константы endpoint'ов (актуальные адреса документации OpenWeatherMap)
    ENDPOINT_CURRENT_WEATHER = "https://api.openweathermap.org/data/2.5/weather"
    ENDPOINT_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
    ENDPOINT_AIR_POLLUTION = "https://api.openweathermap.org/data/2.5/air_pollution"
    ENDPOINT_DIRECT_GEOCODE = "https://api.openweathermap.org/geo/1.0/direct"
    ENDPOINT_REVERSE_GEOCODE = "https://api.openweathermap.org/geo/1.0/reverse"

    # Шкала оценки качества воздуха (значения в микрограммах на м3, для CO - мг/м3)
    AQI_LEVELS = {
        "Хорошее": {"so2": (0, 20), "no2": (0, 40), "pm10": (0, 20), "pm2_5": (0, 10), "o3": (0, 60), "co": (0, 4400)},
        "Удовлетворительное": {"so2": (20, 80), "no2": (40, 70), "pm10": (20, 50), "pm2_5": (10, 25), "o3": (60, 100), "co": (4400, 9400)},
        "Умеренное": {"so2": (80, 250), "no2": (70, 150), "pm10": (50, 100), "pm2_5": (25, 50), "o3": (100, 140), "co": (9400, 12400)},
        "Плохое": {"so2": (250, 350), "no2": (150, 200), "pm10": (100, 200), "pm2_5": (50, 75), "o3": (140, 180), "co": (12400, 15400)},
        "Очень плохое": {"so2": (350, float("inf")), "no2": (200, float("inf")), "pm10": (200, float("inf")), "pm2_5": (75, float("inf")), "o3": (180, float("inf")), "co": (15400, float("inf"))},
    }

    POLLUTANT_LABELS = {
        "so2": "SO2",
        "no2": "NO2",
        "pm10": "PM10",
        "pm2_5": "PM2.5",
        "o3": "O3",
        "co": "CO",
    }

    def __init__(self, api_key: str = OPENWEATHER_API_KEY, session: Optional[requests.Session] = None) -> None:
        """Создаёт клиент OpenWeather API.

        Args:
            api_key: Ключ OpenWeatherMap (по умолчанию из .env).
            session: Переиспользуемая сессия requests для оптимизации запросов.
        """
        if not api_key:
            raise OpenWeatherAPIError(
                "API-ключ OpenWeather не задан. Добавьте OPENWEATHER_API_KEY в файл .env."
            )
        self.api_key = api_key
        self.session = session or requests.Session()

    # ------------------------------------------------------------------ #
    # Внутренние методы: запросы к endpoint'ам                            #
    # ------------------------------------------------------------------ #

    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет GET-запрос и возвращает JSON-ответ.

        Args:
            url: Адрес endpoint'а.
            params: Параметры запроса.

        Returns:
            Данные ответа API.

        Raises:
            APIConnectionError: при сетевых или серверных ошибках.
        """
        params["appid"] = self.api_key
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as error:
            raise APIConnectionError(f"Не удалось подключиться к OpenWeather API: {error}") from error
        return response.json()

    def _direct_geocode(self, city: str) -> Dict[str, float]:
        """Прямой геокодинг: превращает название города в координаты.

        Args:
            city: Название города.

        Returns:
            Словарь с координатами {'lat': ..., 'lon': ...}.

        Raises:
            CityNotFoundError: если город не найден.
        """
        data = self._make_request(
            self.ENDPOINT_DIRECT_GEOCODE,
            {"q": city, "limit": 5},
        )
        if not data:
            raise CityNotFoundError(f"Город '{city}' не найден.")
        first = data[0]
        return {"lat": first["lat"], "lon": first["lon"], "name": first.get("name", city)}

    def _reverse_geocode(self, lat: float, lon: float) -> str:
        """Обратный геокодинг: определяет название места по координатам.

        Args:
            lat: Широта.
            lon: Долгота.

        Returns:
            Название населённого пункта.
        """
        data = self._make_request(
            self.ENDPOINT_REVERSE_GEOCODE,
            {"lat": lat, "lon": lon, "limit": 1},
        )
        if not data:
            return f"{lat:.4f}, {lon:.4f}"
        return data[0].get("name", f"{lat:.4f}, {lon:.4f}")

    def _current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Запрашивает текущую погоду по координатам."""
        return self._make_request(
            self.ENDPOINT_CURRENT_WEATHER,
            {"lat": lat, "lon": lon, "units": "metric", "lang": "ru"},
        )

    def _forecast_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Запрашивает прогноз на 5 дней с шагом 3 часа."""
        return self._make_request(
            self.ENDPOINT_FORECAST,
            {"lat": lat, "lon": lon, "units": "metric", "lang": "ru"},
        )

    def _air_pollution(self, lat: float, lon: float) -> Dict[str, Any]:
        """Запрашивает данные о качестве воздуха по координатам."""
        return self._make_request(
            self.ENDPOINT_AIR_POLLUTION,
            {"lat": lat, "lon": lon},
        )

    # ------------------------------------------------------------------ #
    # Бизнес-логика: анализ качества воздуха                              #
    # ------------------------------------------------------------------ #

    def _analyze_air_quality(self, air_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует качество воздуха и формирует человекочитаемый вывод.

        Args:
            air_data: Ответ endpoint'а Air Pollution.

        Returns:
            Словарь: {'aqi', 'aqi_label', 'pollutants', 'exceeded', 'summary'}.
        """
        items = air_data.get("list", [])
        if not items:
            return {"aqi": None, "aqi_label": "Нет данных", "pollutants": {}, "exceeded": [], "summary": "Данные о качестве воздуха отсутствуют."}

        aqi_index = items[0]["main"]["aqi"]  # 1-5
        components: Dict[str, float] = items[0]["components"]

        # AQI-индекс (по шкале OpenWeather): 1 - Good ... 5 - Very Poor
        aqi_labels_index = {1: "Хорошее", 2: "Удовлетворительное", 3: "Умеренное", 4: "Плохое", 5: "Очень плохое"}
        aqi_label = aqi_labels_index.get(aqi_index, "Неизвестно")

        # Определяем загрязнители, вышедшие за пределы идеальных значений
        exceeded = []
        for key, label in self.POLLUTANT_LABELS.items():
            if key in components and components[key] >= self.AQI_LEVELS["Хорошее"][key][1]:
                exceeded.append((label, components[key]))

        summary = self._build_air_summary(aqi_label, exceeded)
        return {
            "aqi": aqi_index,
            "aqi_label": aqi_label,
            "pollutants": components,
            "exceeded": exceeded,
            "summary": summary,
        }

    def _build_air_summary(self, aqi_label: str, exceeded: List[tuple]) -> str:
        """Формирует человекопонятное описание качества воздуха."""
        if not exceeded:
            return "Качество воздуха хорошее. Все основные загрязнители в пределах нормы."
        names = ", ".join(label for label, _ in exceeded[:3])
        hints = {
            "Плохое": "Чувствительным группам стоит сократить пребывание на улице.",
            "Умеренное": "Показатели слегка превышают идеальные значения.",
            "Удовлетворительное": "Обнаружено небольшое превышение норм.",
            "Очень плохое": "Уровень загрязнения опасен для здоровья, избегайте улицы.",
        }
        hint = hints.get(aqi_label, "")
        return f"Качество воздуха: {aqi_label.lower()}. Превышены: {names}. {hint}".strip()

    # ------------------------------------------------------------------ #
    # Форматирование ответов                                              #
    # ------------------------------------------------------------------ #

    def _format_basic_weather(self, data: Dict[str, Any], extended: bool = False) -> Dict[str, Any]:
        """Собирает словарь с базовыми данными о текущей погоде."""
        main = data.get("main", {})
        wind = data.get("wind", {})
        sys_info = data.get("sys", {})
        weather = data.get("weather", [{}])[0]

        result: Dict[str, Any] = {
            "city": data.get("name", "Неизвестно"),
            "country": sys_info.get("country", ""),
            "temperature": round(main.get("temp", 0), 1),
            "feels_like": round(main.get("feels_like", 0), 1),
            "temp_min": round(main.get("temp_min", 0), 1),
            "temp_max": round(main.get("temp_max", 0), 1),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "description": weather.get("description", ""),
            "visibility": data.get("visibility"),
        }

        if extended:
            result["extended"] = {
                "sunrise": format_timestamp(sys_info.get("sunrise", 0)),
                "sunset": format_timestamp(sys_info.get("sunset", 0)),
                "sea_level": main.get("sea_level"),
                "grnd_level": main.get("grnd_level"),
                "clouds": data.get("clouds", {}).get("all"),
            }
        return result

    def _format_forecast_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Собирает словарь с прогнозом на 5 дней (шаг 3 часа)."""
        city_info = data.get("city", {})
        items = []
        for entry in data.get("list", []):
            items.append(
                {
                    "dt_txt": entry.get("dt_txt", ""),
                    "temp": round(entry.get("main", {}).get("temp", 0), 1),
                    "feels_like": round(entry.get("main", {}).get("feels_like", 0), 1),
                    "humidity": entry.get("main", {}).get("humidity"),
                    "pressure": entry.get("main", {}).get("pressure"),
                    "description": entry.get("weather", [{}])[0].get("description", ""),
                    "wind_speed": entry.get("wind", {}).get("speed"),
                    "pop": entry.get("pop"),
                }
            )
        return {
            "city": city_info.get("name", "Неизвестно"),
            "country": city_info.get("country", ""),
            "items": items,
        }

    # ------------------------------------------------------------------ #
    # Публичные методы                                                    #
    # ------------------------------------------------------------------ #

    def get_weather_by_city(self, city: str, extended: bool = False) -> Dict[str, Any]:
        """Возвращает текущую погоду для города по его названию.

        Args:
            city: Название города.
            extended: Включить расширенные данные (рассвет/закат, давление, воздух).

        Returns:
            Словарь с данными о погоде.

        Raises:
            CityNotFoundError: если город не найден.
        """
        coords = self._direct_geocode(city)
        data = self._current_weather(coords["lat"], coords["lon"])
        result = self._format_basic_weather(data, extended=extended)
        result["city"] = coords["name"]
        if extended:
            air = self._air_pollution(coords["lat"], coords["lon"])
            result["extended"]["air_quality"] = self._analyze_air_quality(air)
        return result

    def get_forecast_by_city(self, city: str, extended: bool = False) -> Dict[str, Any]:
        """Возвращает прогноз на 5 дней (шаг 3 часа) для города.

        Args:
            city: Название города.
            extended: Зарезервировано для будущего расширения.

        Returns:
            Словарь с прогнозом.
        """
        coords = self._direct_geocode(city)
        data = self._forecast_weather(coords["lat"], coords["lon"])
        return self._format_forecast_data(data)

    def get_weather_by_coordinates(self, lat: float, lon: float, extended: bool = False) -> Dict[str, Any]:
        """Возвращает текущую погоду по координатам.

        Args:
            lat: Широта.
            lon: Долгота.
            extended: Включить расширенные данные.

        Returns:
            Словарь с данными о погоде.
        """
        data = self._current_weather(lat, lon)
        result = self._format_basic_weather(data, extended=extended)
        result["city"] = self._reverse_geocode(lat, lon)
        if extended:
            air = self._air_pollution(lat, lon)
            result["extended"]["air_quality"] = self._analyze_air_quality(air)
        return result