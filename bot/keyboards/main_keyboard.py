"""Главное меню бота."""

from vkbottle import Keyboard, KeyboardButtonColor, Text


def get_main_keyboard() -> Keyboard:
    """Собирает главное меню с кнопками-командами."""
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("🌤 Погода сейчас"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("📅 Прогноз 5 дней"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("📍 Геолокация"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("🌫 Расширенный режим"), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text("⚖️ Сравнение городов"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("ℹ️ Помощь"), color=KeyboardButtonColor.PRIMARY)
    return keyboard