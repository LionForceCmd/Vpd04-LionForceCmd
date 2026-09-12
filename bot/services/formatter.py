"""Форматирование ответов бота: только оформление, без логики запросов."""

from typing import Any, Dict, List

from openweather.utils import celsius_with_sign


def format_weather(data: Dict[str, Any], extended: bool = False) -> str:
    """Оформляет сообщение о текущей погоде."""
    lines = [
        f"🌍 Город: {data['city']}",
        f"☁️ Описание: {data.get('description', '—')}",
        f"🌡 Температура: {celsius_with_sign(data['temperature'])} (ощущается как {celsius_with_sign(data['feels_like'])})",
        f"📊 Мин/Макс: {celsius_with_sign(data['temp_min'])} / {celsius_with_sign(data['temp_max'])}",
        f"💧 Влажность: {data['humidity']}%",
        f"🗜 Давление: {data['pressure']} гПа",
        f"💨 Ветер: {data['wind_speed']} м/с",
    ]

    if extended:
        ext = data.get("extended", {})
        lines.append("──────────────────────────────")
        lines.append("🌅 Расширенная сводка:")
        if ext.get("sunrise"):
            lines.append(f"🌅 Рассвет: {ext['sunrise']}")
        if ext.get("sunset"):
            lines.append(f"🌇 Закат: {ext['sunset']}")
        if ext.get("clouds") is not None:
            lines.append(f"☁️ Облачность: {ext['clouds']}%")
        if ext.get("sea_level"):
            lines.append(f"🏔 Давление на ур. моря: {ext['sea_level']} гПа")
        if ext.get("grnd_level"):
            lines.append(f"⛰ Давление у земли: {ext['grnd_level']} гПа")
        air = ext.get("air_quality")
        if air:
            lines.append("──────────────────────────────")
            lines.append(f"🌫 Воздух: {air.get('aqi_label')} (AQI {air.get('aqi')})")
            if air.get("exceeded"):
                details = ", ".join(f"{label} {value}" for label, value in air["exceeded"])
                lines.append(f"📊 Превышены: {details}")
            lines.append(f"💬 {air.get('summary')}")
    return "\n".join(lines)


def format_forecast(data: Dict[str, Any], limit: int = 8) -> str:
    """Оформляет сообщение с прогнозом на 5 дней."""
    city = data["city"]
    lines = [f"📅 Прогноз для {city} на 5 дней:"]
    for item in data["items"][:limit]:
        pop = item.get("pop")
        pop_text = f" (осадки {int(float(pop) * 100)}%)" if pop is not None else ""
        lines.append(
            f"• {item['dt_txt']}: {celsius_with_sign(item['temp'])}, "
            f"{item.get('description', '—')}, влажность {item.get('humidity')}%, "
            f"ветер {item.get('wind_speed')} м/с{pop_text}"
        )
    lines.append("\nПоказаны ближайшие интервалы. Полный список — по запросу.")
    return "\n".join(lines)


def format_comparison(results: List[Dict[str, Any]]) -> str:
    """Оформляет сравнение погоды в двух городах."""
    if len(results) < 2:
        return "Для сравнения нужно минимум два города."
    a, b = results[0], results[1]
    lines = [
        f"⚖️ Сравнение: {a['city']} vs {b['city']}",
        "──────────────────────────────",
        f"🌡 Температура: {a['city']} {celsius_with_sign(a['temperature'])} vs {b['city']} {celsius_with_sign(b['temperature'])}",
        f"🌡 Ощущается: {a['city']} {celsius_with_sign(a['feels_like'])} vs {b['city']} {celsius_with_sign(b['feels_like'])}",
        f"💧 Влажность: {a['city']} {a['humidity']}% vs {b['city']} {b['humidity']}%",
        f"💨 Ветер: {a['city']} {a['wind_speed']} м/с vs {b['city']} {b['wind_speed']} м/с",
        f"🗜 Давление: {a['city']} {a['pressure']} гПа vs {b['city']} {b['pressure']} гПа",
        f"☁️ {a['city']}: {a.get('description', '—')}",
        f"☁️ {b['city']}: {b.get('description', '—')}",
    ]
    return "\n".join(lines)


def format_help() -> str:
    """Оформляет справочное сообщение о возможностях бота."""
    return (
        "🤖 Я — погодный бот. Умею:\n"
        "🌤 Погода сейчас — текущая погода по названию города;\n"
        "📅 Прогноз 5 дней — прогноз с шагом 3 часа;\n"
        "📍 Геолокация — пришлите точку на карте или координаты;\n"
        "🌫 Расширенный режим — погода + качество воздуха;\n"
        "⚖️ Сравнение городов — сравню погоду в двух городах;\n"
        "ℹ️ Помощь — эта подсказка."
    )