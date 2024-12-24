from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
btn_1 = KeyboardButton('Помощь ⭐️')
btn_3 = KeyboardButton('Купить товар 🛒')
btn_4 = KeyboardButton('Просмотр своего профиля')
btn_5 = KeyboardButton('Поддержать меня!')
btn_star = KeyboardButton('⭐')
markup.add(btn_1).add(btn_3).add(btn_4).add(btn_5)





only_help_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_1 = KeyboardButton('Помощь ⭐️')
only_help_markup.add(btn_1)