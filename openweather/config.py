"""Конфигурация проекта: загрузка ключей из .env."""

import os

from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
VK_BOT_TOKEN = os.getenv("VK_BOT_TOKEN", "")