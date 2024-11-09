from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btn_1 = KeyboardButton('Помощь ⭐️')
btn_2 = KeyboardButton('Описание 📌')
btn_3 = KeyboardButton('Каталог 🛒')
markup.add(btn_1).insert(btn_2).add(btn_3)



only_help_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_1 = KeyboardButton('Помощь ⭐️')
only_help_markup.add(btn_1)