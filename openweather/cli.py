"""Точка входа для запуска модуля OpenWeather API из консоли.

Примеры использования:
    python -m openweather.cli --city Москва
    python -m openweather.cli --city Москва --extended
    python -m openweather.cli --city Москва --forecast
    python -m openweather.cli --lat 55.7558 --lon 37.6173
    python -m openweather.cli --compare Москва,Анталья
"""

import argparse
import sys

from openweather.client import OpenWeatherAPI
from openweather.exceptions import CityNotFoundError, OpenWeatherAPIError


def print_weather(data: dict) -> None:
    """Печатает информацию о погоде в консоль."""
    print("=" * 50)
    city = data["city"]
    country = data.get("country", "")
    print(f"Город: {city} ({country})" if country else f"Город: {city}")
    print(f"Описание: {data.get('description', '—')}")
    print(f"Температура: {data['temperature']}°C (ощущается как {data['feels_like']}°C)")
    print(f"Мин/Макс: {data['temp_min']}°C / {data['temp_max']}°C")
    print(f"Влажность: {data['humidity']}%")
    print(f"Давление: {data['pressure']} гПа")
    print(f"Ветер: {data['wind_speed']} м/с")

    extended = data.get("extended")
    if extended:
        print("--- Расширенные данные ---")
        print(f"Рассвет: {extended.get('sunrise')} / Закат: {extended.get('sunset')}")
        if extended.get("sea_level"):
            print(f"Давление на уровне моря: {extended['sea_level']} гПа")
        if extended.get("grnd_level"):
            print(f"Давление у земли: {extended['grnd_level']} гПа")
        if extended.get("clouds") is not None:
            print(f"Облачность: {extended['clouds']}%")
        air = extended.get("air_quality")
        if air:
            print("--- Анализ воздуха ---")
            print(f"AQI: {air.get('aqi')} — {air.get('aqi_label')}")
            if air.get("exceeded"):
                print("Превышены нормативы:", ", ".join(f"{label} = {val}" for label, val in air["exceeded"]))
            print(air.get("summary"))


def print_forecast(data: dict, limit: int = 8) -> None:
    """Печатает прогноз на 5 дней (по умолчанию первые 8 интервалов)."""
    print("=" * 50)
    print(f"Прогноз для {data['city']} ({data.get('country', '')}) на 5 дней")
    print("-" * 50)
    for item in data["items"][:limit]:
        print(
            f"{item['dt_txt']}: {item['temp']}°C, {item.get('description', '—')}, "
            f"влажность {item.get('humidity')}%, ветер {item.get('wind_speed')} м/с"
        )


def compare_cities(api: OpenWeatherAPI, cities: list[str]) -> list[dict]:
    """Запрашивает погоду для списка городов и возвращает результаты."""
    results = []
    for city in cities:
        city = city.strip()
        if not city:
            continue
        results.append(api.get_weather_by_city(city))
    return results


def print_comparison(results: list[dict]) -> None:
    """Печатает сравнение погоды в городах."""
    if len(results) < 2:
        print("Для сравнения нужно указать минимум два города.")
        return
    print("=" * 50)
    print("Сравнение городов")
    print("=" * 50)
    headers = ["Показатель", *[r["city"] for r in results]]
    print(f"{headers[0]:<18}" + "".join(f"{h:<18}" for h in headers[1:]))
    rows = {
        "Температура °C": [f"{r['temperature']}" for r in results],
        "Ощущается °C": [f"{r['feels_like']}" for r in results],
        "Влажность %": [f"{r['humidity']}" for r in results],
        "Ветер м/с": [f"{r['wind_speed']}" for r in results],
        "Давление гПа": [f"{r['pressure']}" for r in results],
        "Описание": [r.get("description", "—") for r in results],
    }
    for label, values in rows.items():
        print(f"{label:<18}" + "".join(f"{v:<18}" for v in values))


def main() -> None:
    """Разбирает аргументы командной строки и выполняет запрос к API."""
    parser = argparse.ArgumentParser(description="Работа с OpenWeather API из консоли")
    parser.add_argument("--city", help="Название города для погоды")
    parser.add_argument("--extended", action="store_true", help="Расширенный режим (качество воздуха и др.)")
    parser.add_argument("--forecast", action="store_true", help="Прогноз на 5 дней")
    parser.add_argument("--lat", type=float, help="Широта")
    parser.add_argument("--lon", type=float, help="Долгота")
    parser.add_argument("--compare", help="Список городов через запятую: Москва,Анталья")
    args = parser.parse_args()

    try:
        api = OpenWeatherAPI()
    except OpenWeatherAPIError as error:
        print(f"Ошибка конфигурации: {error}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.compare:
            results = compare_cities(api, args.compare.split(","))
            print_comparison(results)
        elif args.city and args.forecast:
            print_forecast(api.get_forecast_by_city(args.city))
        elif args.city:
            print_weather(api.get_weather_by_city(args.city, extended=args.extended))
        elif args.lat is not None and args.lon is not None:
            print_weather(api.get_weather_by_coordinates(args.lat, args.lon, extended=args.extended))
        else:
            parser.print_help()
    except CityNotFoundError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
    except OpenWeatherAPIError as error:
        print(f"Ошибка API: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()