"""Инициализация VKBottle-бота."""

import logging

from vkbottle.bot import Bot

from openweather.config import VK_BOT_TOKEN

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Создаёт и возвращает экземпляр бота VKBottle."""
    if not VK_BOT_TOKEN:
        raise RuntimeError(
            "Токен сообщества VK не задан. Добавьте VK_BOT_TOKEN в файл .env"
        )
    return Bot(token=VK_BOT_TOKEN)


bot = create_bot()


def setup_handlers() -> None:
    """Импортирует все модули обработчиков, регистрируя их на боте."""
    import bot.handlers.help  # noqa: F401
    import bot.handlers.menu  # noqa: F401
    import bot.handlers.weather  # noqa: F401
    import bot.handlers.forecast  # noqa: F401
    import bot.handlers.geo  # noqa: F401
    import bot.handlers.compare  # noqa: F401

    logger.info("Все обработчики зарегистрированы.")