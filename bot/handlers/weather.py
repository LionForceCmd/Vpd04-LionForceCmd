"""Обработчики текущей погоды и расширенного режима."""

from vkbottle.bot import Message

from bot.bot import bot
from bot.keyboards.navigation_keyboard import get_navigation_keyboard
from bot.services.formatter import format_weather
from bot.services.state_manager import save_city
from bot.services.weather_service import build_error_text, get_current_weather
from bot.states import States

WEATHER_BUTTON = "🌤 Погода сейчас"
EXTENDED_BUTTON = "🌫 Расширенный режим"


async def _ask_city(message: Message, extended: bool) -> None:
    """Просит пользователя ввести название города."""
    await bot.state_dispenser.set(
        message.peer_id, States.WAITING_EXTENDED if extended else States.WAITING_CITY
    )
    hint = " (включая качество воздуха)" if extended else ""
    await message.answer(
        f"🏙 Введите название города{hint}:",
        keyboard=get_navigation_keyboard(),
    )


@bot.on.message(text=[WEATHER_BUTTON])
async def weather_button(message: Message) -> None:
    """Кнопка «Погода сейчас»: переходим в состояние ожидания города."""
    await _ask_city(message, extended=False)


@bot.on.message(text=[EXTENDED_BUTTON])
async def extended_button(message: Message) -> None:
    """Кнопка «Расширенный режим»: переходим в состояние ожидания города."""
    await _ask_city(message, extended=True)


@bot.on.message(state=States.WAITING_CITY)
async def weather_city_handler(message: Message) -> None:
    """Принимает название города и возвращает текущую погоду."""
    city = message.text.strip()
    if not city:
        await message.answer("Пожалуйста, введите название города.")
        return
    await bot.state_dispenser.delete(message.peer_id)
    try:
        data = get_current_weather(city)
    except Exception as error:
        await message.answer(build_error_text(error), keyboard=get_navigation_keyboard())
        return
    save_city(message.peer_id, data["city"])
    await message.answer(format_weather(data), keyboard=get_navigation_keyboard())


@bot.on.message(state=States.WAITING_EXTENDED)
async def extended_city_handler(message: Message) -> None:
    """Принимает город и возвращает расширенную сводку с качеством воздуха."""
    city = message.text.strip()
    if not city:
        await message.answer("Пожалуйста, введите название города.")
        return
    await bot.state_dispenser.delete(message.peer_id)
    try:
        data = get_current_weather(city, extended=True)
    except Exception as error:
        await message.answer(build_error_text(error), keyboard=get_navigation_keyboard())
        return
    save_city(message.peer_id, data["city"])
    await message.answer(format_weather(data, extended=True), keyboard=get_navigation_keyboard())