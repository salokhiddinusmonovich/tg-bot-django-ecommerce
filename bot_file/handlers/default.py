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
from aiogram.types import PreCheckoutQuery
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

CURRENCY = 'XTR'


HELP_TEXT = """
Привет 👋, я бот по продаже различных товаров! У нас есть такие команды как:

<b>Помощь ⭐️</b> - помощь по командам бота
<b>Описание 📌</b> - адрес, контактные данные, график работы
<b>Купить товар 🛒</b> - список товаров которые можно купить
<b>Просмотр своего профиля</b> - просмотр своего профиля

Но перед началом нужно <b>зарегистрироваться или войти</b> в свой профиль. 
Нажми на команду <b>Регистрация 👌'</b> или <b>Войти 👋</b>
Если этого не сделаете, некоторые команды будут <b>не доступны</b> 🔴

Рады что вы используете данного бота 🦦
"""

# Command to start the bot
async def cmd_start(message: types.Message):
    if message.chat.type == 'private':
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
    if message.chat.type == 'private':
        await bot.send_message(chat_id=message.chat.id, text=HELP_TEXT, reply_markup=default_kb.markup)



# Get profile command
# @dp.message_handler(commands='getprofile')
async def cmd_getprofile(message: types.Message):
    if message.chat.type == 'private':
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
                await message.answer("Введите логин или chat_id пользователя, например: /getprofile 'username'")
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
    if message.chat.type == 'private':
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


# --------------------------------------------------------------------------------------

async def donate_dev(message: types.Message):
    await message.answer("Хотите поддержать? Нажмите на кнопку ниже для доната!: /donate")



@dp.message_handler(commands=['donate'])
async def donate_ongoing(message: types.Message) -> None:
    prices = [types.LabeledPrice(label="1 Star ⭐", amount=1)]  # Amount is in the smallest currency unit (e.g., cents)

    await message.bot.send_invoice(
        chat_id=message.chat.id,  # Correctly using the chat_id
        title="Support me with donation",
        description="Support with one star ⭐",
        payload="channel_support",  
        provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",  # Replace with your actual provider token
        currency=CURRENCY,  
        prices=prices,
        reply_markup=payment_keyboard(),
        start_parameter="donation_support",  # Optionally add start_parameter for future references
        # photo_url="https://your_image_url.com/photo.jpg",  # Optionally add a photo for the invoice
        # photo_size=512, 
        # photo_width=512, 
        # photo_height=512  
    )


def payment_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Оплатить 1 ⭐", pay=True)  # 'pay=True' indicates a payment button
    )
    return keyboard


@dp.pre_checkout_query_handler()
async def pre_checkout_handle(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message) -> None:
    successful_payment = message.successful_payment
    # Sending a visual confirmation emoji or animation before the payment details
    await message.answer("✨ Payment received! Processing your details... ✨")
    
    # Sending the payment details in a separate message
    await message.answer(
        f"Thank you for your payment! 🎉\n\n"
        f"Payment ID: {successful_payment.telegram_payment_charge_id}\n"
        f"Provider Payment Charge ID: {successful_payment.provider_payment_charge_id}"
    )
# ---------------------------------------------------------------------------------------------


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
    dp.register_message_handler(cmd_getprofile, commands='getprofile')
    dp.register_message_handler(cmd_access, commands='access')
    dp.register_message_handler(donate_dev, Text(equals='Поддержать меня!'))
