"""Обработчик прогноза на 5 дней."""

from vkbottle.bot import Message

from bot.bot import bot
from bot.keyboards.navigation_keyboard import get_navigation_keyboard
from bot.services.formatter import format_forecast
from bot.services.state_manager import save_city
from bot.services.weather_service import build_error_text, get_forecast
from bot.states import States

FORECAST_BUTTON = "📅 Прогноз 5 дней"


@bot.on.message(text=[FORECAST_BUTTON])
async def forecast_button(message: Message) -> None:
    """Кнопка «Прогноз 5 дней»: просим назвать город."""
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FORECAST_CITY)
    await message.answer(
        "🏙 Введите название города:",
        keyboard=get_navigation_keyboard(),
    )


@bot.on.message(state=States.WAITING_FORECAST_CITY)
async def forecast_city_handler(message: Message) -> None:
    """Принимает город и возвращает прогноз на 5 дней."""
    city = message.text.strip()
    if not city:
        await message.answer("Пожалуйста, введите название города.")
        return
    await bot.state_dispenser.delete(message.peer_id)
    try:
        data = get_forecast(city)
    except Exception as error:
        await message.answer(build_error_text(error), keyboard=get_navigation_keyboard())
        return
    save_city(message.peer_id, data["city"])
    await message.answer(format_forecast(data), keyboard=get_navigation_keyboard())