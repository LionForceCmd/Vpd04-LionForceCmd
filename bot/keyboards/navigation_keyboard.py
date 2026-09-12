"""Навигационные кнопки: возврат в меню."""

from vkbottle import Keyboard, KeyboardButtonColor, Text


def get_navigation_keyboard() -> Keyboard:
    """Собирает клавиатуру с кнопками «Назад» и «Главное меню»."""
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("⬅️ Назад"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("🏠 Главное меню"), color=KeyboardButtonColor.SECONDARY)
    return keyboard