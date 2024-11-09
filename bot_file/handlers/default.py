from aiogram import types
from random import randrange
from aiogram.dispatcher.filters import Text
from django.conf import settings
from ..loader import bot, dp
from ..keyboards import sign_inup_kb, admin_kb, default_kb
from ..models import TelegramUser
from .authorization import sign_in
from asgiref.sync import sync_to_async
import pytz
from datetime import datetime


HELP_TEXT = """
Привет 👋, я бот по продаже различных товаров! У нас есть такие команды как:

<b>Помощь ⭐️</b> - помощь по командам бота
<b>Описание 📌</b> - адрес, контактные данные, график работы
<b>Каталог 🛒</b> - список товаров которые можно купить
<b>Просмотр своего профиля</b> - просмотр своего профиля

Но перед началом нужно <b>зарегистрироваться или войти</b> в свой профиль. 
Нажми на команду <b>Регистрация ✌️'</b> или <b>Войти 👋</b>
Если этого не сделаете, некоторые команды будут <b>не доступны</b> 🔴

Рады что вы используете данного бота 🦦
"""

# Command to start the bot
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
    except Exception as e:
        await message.reply(text=f"Ошибка: {str(e)}. Чтобы можно было общаться с ботом, "
                                 "ты можешь написать мне в личные сообщение: "
                                 "https://t.me/salo_kh")


# Help command
async def cmd_help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=HELP_TEXT, reply_markup=default_kb.markup)


# Description command
async def cmd_description(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text="Привет ✋, мы компания по продаже различных товаров!, "
                                "Мы очень рады что Вы используете наш сервис ❤️, мы работает с Понедельника до "
                                "Пятницы.\n9:00 - 21:00")
    await bot.send_location(chat_id=message.chat.id,
                            latitude=randrange(1, 100),
                            longitude=randrange(1, 100))


# Get profile command
# @dp.message_handler(commands='getprofile')
async def cmd_getprofile(message: types.Message):
    try:
        user = await get_user_by_chat_id(message.chat.id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        if not user.admin:
            await message.answer("У вас нет прав доступа к этой команде.")
            return

        args = message.get_args()
        if not args:
            await message.answer("Введите логин или chat_id пользователя, например: /getprofile user123")
            return

        searched_user = await get_user_by_chat_id_or_user_login(args)
        if searched_user:
            moscow_tz = pytz.timezone('Europe/Moscow')
            registered_at_moscow = searched_user.registered_at.astimezone(moscow_tz)
            
            profile_info = (
                f"👤 <b>Профиль пользователя:</b>\n"
                f"🔑 <b>Логин:</b> {searched_user.user_login}\n"
                f"💰 <b>Баланс:</b> {searched_user.balance}\n"
                f"👑 <b>Администратор:</b> {'Да' if searched_user.admin else 'Нет'}\n"
                f"📅 <b>Дата регистрации:</b> {registered_at_moscow.strftime('%d-%m-%Y %H:%M:%S')}\n"
                f"📝 <b>Комментарий:</b> {searched_user.comment or 'Нет комментариев'}"
            )
            await message.answer(profile_info, parse_mode='HTML')
        else:
            await message.answer("❌ Пользователь не найден.")
    except Exception as e:
        await message.answer(f"Ошибка при получении данных: {str(e)}")


# @dp.message_handler(commands='access')
async def cmd_access(message: types.Message):
    user = await get_user_by_chat_id(message.chat.id)
    if not user or not user.admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    args = message.get_args()
    if not args:
        await message.answer("Пожалуйста, укажите логин или chat_id пользователя для выдачи доступа.")
        return

    try:
        target_user = await get_user_by_chat_id_or_user_login(args)
        if target_user:
            target_user.admin = True
            await save_user(target_user)  
            await message.answer(f"Пользователь {target_user.user_login} теперь является администратором.")
        else:
            await message.answer("❌ Пользователь не найден.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


# @dp.message_handler(commands='giverub')
async def cmd_giverub(message: types.Message):
    # Проверяем, является ли пользователь администратором
    user = await get_user_by_chat_id(message.chat.id)
    if not user or not user.admin:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    # Получаем аргументы команды
    args = message.get_args().split()

    # Проверяем, указано ли количество рублей и является ли оно числом
    if len(args) != 2:
        await message.answer("Пожалуйста, укажите количество рублей и логин пользователя, например: /giverub 100 'username.'")
        return
    
    amount = args[0]
    target_login = args[1]

    # Проверка, что количество рублей является положительным числом
    if not amount.isdigit() or int(amount) <= 0:
        await message.answer("Количество рублей должно быть положительным числом.")
        return

    # Получаем пользователя по логину
    target_user = await get_user_by_chat_id_or_user_login(target_login)
    if target_user:
        target_user.balance += int(amount)
        await save_user(target_user)  # Сохраняем изменения
        await message.answer(f"Пользователю {target_user.user_login} было зачислено {amount} рублей.")
    else:
        await message.answer("❌ Пользователь с таким логином не найден.")



@sync_to_async
def get_user_by_chat_id_or_user_login(identifier):
    if identifier.isdigit():
        return TelegramUser.objects.filter(chat_id=int(identifier)).first()
    return TelegramUser.objects.filter(user_login=identifier).first()



@sync_to_async
def get_user_by_chat_id(chat_id):
    try:
        return TelegramUser.objects.get(chat_id=chat_id)
    except TelegramUser.DoesNotExist:
        return None
    
@sync_to_async
def save_user(user):
    user.save()


# Register default handlers
def default_handlers_register():
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_help, Text(equals='Помощь ⭐️'))
    dp.register_message_handler(cmd_description, Text(equals='Описание 📌'))
    dp.register_message_handler(cmd_getprofile, commands='getprofile')
    dp.register_message_handler(cmd_access, commands='access')
    dp.register_message_handler(cmd_giverub, commands='giverub')
