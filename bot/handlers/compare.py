"""Обработчик сравнения погоды в двух городах."""

from vkbottle.bot import Message

from bot.bot import bot
from bot.keyboards.navigation_keyboard import get_navigation_keyboard
from bot.services.formatter import format_comparison
from bot.services.state_manager import storage
from bot.services.weather_service import build_error_text, get_current_weather
from bot.states import States

COMPARE_BUTTON = "⚖️ Сравнение городов"
_FIRST_KEY = "compare_first:{}"


@bot.on.message(text=[COMPARE_BUTTON])
async def compare_button(message: Message) -> None:
    """Кнопка «Сравнение городов»: просим первый город."""
    await bot.state_dispenser.set(message.peer_id, States.WAITING_COMPARE_FIRST)
    await message.answer(
        "⚖️ Сравнение городов. Назовите первый город:",
        keyboard=get_navigation_keyboard(),
    )


@bot.on.message(state=States.WAITING_COMPARE_FIRST)
async def compare_first_handler(message: Message) -> None:
    """Запоминаем первый город и просим второй."""
    city = message.text.strip()
    if not city:
        await message.answer("Пожалуйста, введите название города.")
        return
    storage.set(_FIRST_KEY.format(message.peer_id), city)
    await bot.state_dispenser.set(message.peer_id, States.WAITING_COMPARE_SECOND)
    await message.answer("Назовите второй город:")


@bot.on.message(state=States.WAITING_COMPARE_SECOND)
async def compare_second_handler(message: Message) -> None:
    """Сравниваем погоду в двух городах и отправляем результат."""
    second_city = message.text.strip()
    first_city = storage.get(_FIRST_KEY.format(message.peer_id))
    if not second_city:
        await message.answer("Пожалуйста, введите название города.")
        return
    if not first_city:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Похоже, диалог прервался. Начнём сравнение заново.")
        return

    await bot.state_dispenser.delete(message.peer_id)
    storage.delete(_FIRST_KEY.format(message.peer_id))

    try:
        first = get_current_weather(first_city)
        second = get_current_weather(second_city)
    except Exception as error:
        await message.answer(build_error_text(error), keyboard=get_navigation_keyboard())
        return
    await message.answer(
        format_comparison([first, second]),
        keyboard=get_navigation_keyboard(),
    )