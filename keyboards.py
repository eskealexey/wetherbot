from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Стартовая клавиатура
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        # [
        #     KeyboardButton(text="Меню"),
        #     KeyboardButton(text="Информация"),
        # ],
        [
            KeyboardButton(text="Мои координаты", request_location=True),
            KeyboardButton(text="Введите координаты"),
        ],
        [
            KeyboardButton(text="Укажите населенный пункт")
        ]
    ], resize_keyboard=True)
wether_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Погода сейчас', callback_data='get_wether_now')
        ],
        [
            InlineKeyboardButton(text='Погода на сегодня', callback_data='get_wether_today')
        ],
        # [
        #     InlineKeyboardButton(text='Погода на неделю', callback_data='get_wether_week')
        # ],
        # [
        #     InlineKeyboardButton(text='Погода на месяц', callback_data='get_wether_month')
        # ]
    ]
)