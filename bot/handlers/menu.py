"""Обработчик главного меню и стартового сообщения."""

from vkbottle.bot import Message

from bot.bot import bot
from bot.keyboards.main_keyboard import get_main_keyboard
from bot.services.formatter import format_help
from bot.states import States


@bot.on.message(command=["start", "меню"])
@bot.on.message(text=["Начать", "Старт", "Привет", "🏠 Главное меню", "⬅️ Назад"])
async def start_handler(message: Message) -> None:
    """Показывает приветствие (или главное меню) и сбрасывает состояние."""
    await bot.state_dispenser.delete(message.peer_id)
    await bot.state_dispenser.set(message.peer_id, States.MAIN_MENU)
    text = (
        "👋 Привет! Я погодный бот.\n"
        "Покажу текущую погоду, прогноз на 5 дней, качество воздуха, "
        "определю погоду по геолокации и сравню два города.\n"
        "Выбирай команду в меню 👇"
    )
    await message.answer(text, keyboard=get_main_keyboard())


@bot.on.message(text=["ℹ️ Помощь", "помощь", "help"])
async def help_handler(message: Message) -> None:
    """Показывает список доступных команд."""
    await message.answer(format_help(), keyboard=get_main_keyboard())