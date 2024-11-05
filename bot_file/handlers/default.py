from aiogram import types
from random import randrange
from aiogram.dispatcher.filters import Text
from django.conf import settings
from ..loader import bot, dp
from ..keyboards import sign_inup_kb, admin_kb, default_kb
from ..models import TelegramUser
from .authorization import sign_in

HELP_TEXT = """
Привет 👋, я бот по продаже различных товаров! У нас есть такие команды как:

<b>Помощь ⭐️</b> - помощь по командам бота
<b>Описание 📌</> - адрес, контактные данные, график работы
<b>Каталог 🛒</b> - список товаров которые можно купить
<b>Админ 👑</b> - меню администратора

Но перед началом нужно <b>зарегистрироваться или войти</b> в свой профиль. 
Нажми на команду <b>Регистрация ✌️'</b> или <b>Войти 👋</b>
Если этого не сделаете, некоторые команды будут <b>не доступны</b> 🔴

Рады что вы используете данного бота 🦦
"""

# @dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    try:
        await bot.send_message(chat_id=message.chat.id,
                               text="Привет ✋, я бот по продаже различных товаров!\n\n"
                                    "У меня вы можете купить все что захотите, чтобы увидеть список "
                                    "товаров которые у меня есть.\n\n"
                                    "Нажмите снизу на команду 'Каталог 🛒'\n\n"
                                    "Но для начала <b>нужно зарегистрироваться</b>, "
                                    "иначе остальные команды будут не доступны!\n\n"
                                    "Нажми на команду <b>Регистрация 👌'</b> или <b>Войти 👋</b>",
                               reply_markup=sign_inup_kb.markup)
    except:
        await message.reply(text="Чтобы можно было общаться с ботом, "
                                 "ты можешь написать мне в личные сообщение: "
                                 "https://t.me/salo_kh")
        


# @dp.message_handler(Text(equals='Помощь ⭐️'))
async def cmd_help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=HELP_TEXT, reply_markup=default_kb.markup)


# @dp.message_handler(Text(equals='Описание 📌'))
async def cmd_description(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text="Привет ✋, мы компания по продаже различных товаров!, "
                                "Мы очень рады что Вы используете"
                                " наш сервис ❤️, мы работает с Понедельника до "
                                "Пятницы.\n9:00 - 21:00")
    await bot.send_location(chat_id=message.chat.id,
                            latitude=randrange(1, 100),
                            longitude=randrange(1, 100))

















def default_handlers_register():
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_help, Text(equals='Помощь ⭐️'))
    dp.register_message_handler(cmd_description, Text(equals='Описание 📌'))