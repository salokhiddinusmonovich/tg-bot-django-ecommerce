from aiogram import types
from asgiref.sync import sync_to_async

from ..loader import bot, dp
from ..keyboards import sign_inup_kb
from ..models import Product
from aiogram.dispatcher.filters import Text
from .authorization import sign_in
from ..keyboards.default_kb import markup
import asyncio
from django.db.models import QuerySet
from threading import Thread
from ..models import Product, TelegramUser
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import sync_to_async


back_button = KeyboardButton("Назад ⬅️")
back_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(back_button)


# Обработчик кнопки "Просмотр своего профиля"
@dp.message_handler(Text(equals="Просмотр своего профиля"))
async def view_profile(message: types.Message):
    user, bought_products = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Вы не зарегистрированы в системе. Пожалуйста, зарегистрируйтесь.", reply_markup=back_kb)
        return

    bought_products_text = ', '.join([product.name for product in bought_products]) if bought_products else "Нет купленных товаров"
    profile_info = (
        f"👤 Имя: {user.user_login}\n"
        f"💰 Баланс: {user.balance} рублей\n"
        f"🛒 Купленные товары: {bought_products_text}\n"
        f"📅 Дата регистрации: {user.registered_at.strftime('%d-%m-%Y')}\n"
    )

    await message.answer(profile_info, reply_markup=back_kb)

# Обработчик кнопки "Назад ⬅️"
@dp.message_handler(Text(equals="Назад ⬅️"))
async def back_to_main_menu(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=markup)



def send_products(chat_id, products):
    for product in products:
        # Read the product image as bytes
        photo_id = product.photo.open('rb').read()
        caption = f"Товар 🚀: {product.name}\nОписание 💬: {product.description}\nЦена 💰: {product.price} рублей"
        bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)



# @dp.message_handler(Text(equals='Каталог 🛒'))
async def show_products(message: types.Message):
    if not sign_in['current_state']:
        await message.answer("Вы не вошли в аккаунт, попробуйте войти в профиль ‼️", reply_markup=sign_inup_kb.markup)
        return

    products = get_all_products_sync()

    if products:
        await bot.send_message(chat_id=message.chat.id, text="Вот все доступные товары 👇")
        

        thread = Thread(target=send_products, args=(message.chat.id, products))
        thread.start()
    else:
        await bot.send_message(chat_id=message.chat.id, text="К сожалению, в данный момент нет доступных товаров. Пожалуйста, попробуйте позже.")

@sync_to_async
def get_all_products_sync():
    return list(Product.objects.all())


@sync_to_async
def get_user(chat_id):
    # Преобразуем QuerySet в объект, чтобы избежать ленивой оценки
    user = TelegramUser.objects.filter(chat_id=chat_id).first()
    if user:
        # Преобразуем список купленных товаров в Python-список
        bought_products = list(user.bought_products.all())
        return user, bought_products
    return None, []



def catalog_handlers_register():
    dp.register_message_handler(show_products, Text(equals='Каталог 🛒'))
    dp.register_message_handler(view_profile, Text(equals="Просмотр своего профиля"))