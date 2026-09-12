"""Состояния (FSM) пользователей бота."""

from vkbottle import BaseStateGroup


class States(BaseStateGroup):
    """Все состояния, через которые проходит пользователь."""

    MAIN_MENU = "main_menu"
    WAITING_CITY = "waiting_city"
    WAITING_FORECAST_CITY = "waiting_forecast_city"
    WAITING_GEO = "waiting_geo"
    WAITING_EXTENDED = "waiting_extended"
    WAITING_COMPARE_FIRST = "waiting_compare_first"
    WAITING_COMPARE_SECOND = "waiting_compare_second"