"""Точка входа VK-бота: запуск через python -m bot.main."""

import logging

from vkbottle import API

from bot.bot import bot, setup_handlers
from openweather.config import VK_BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Настраивает логгеры, регистрирует обработчики и запускает LongPoll."""
    if not VK_BOT_TOKEN:
        logger.error("VK_BOT_TOKEN не задан. Проверьте файл .env")
        return

    setup_handlers()
    api = API(token=VK_BOT_TOKEN)
    logger.info("Бот запущен. LongPoll работает. Нажмите Ctrl+C для остановки.")
    bot.run_forever()


if __name__ == "__main__":
    main()