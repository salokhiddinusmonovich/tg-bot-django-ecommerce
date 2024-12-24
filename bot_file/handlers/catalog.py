from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, PreCheckoutQuery, LabeledPrice
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from asgiref.sync import sync_to_async
from ..loader import bot, dp
from ..models import Product, TelegramUser
from ..keyboards.default_kb import markup

CURRENCY = 'XTR'

class PurchaseStates(StatesGroup):
    choosing_product = State()
    confirming_purchase = State()
    waiting_for_payment = State()

# Buttons
cancel_button = KeyboardButton("Отмена ❌")
back_button = KeyboardButton("Назад ⬅️")
buy_button = KeyboardButton("Купить товар 🛒")
profile_button = KeyboardButton("Просмотр своего профиля")
cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)
back_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(back_button)

@dp.message_handler(Text(equals="Просмотр своего профиля"))
async def view_profile(message: types.Message):
    if message.chat.type == 'private':
        user, bought_products = await get_user(message.from_user.id)
        if user is None:
            await message.answer("Вы не зарегистрированы в системе. Пожалуйста, зарегистрируйтесь.", reply_markup=back_kb)
            return

        bought_products_text = ', '.join([product.name for product in bought_products]) if bought_products else "Нет купленных товаров"
        profile_info = (
            f"👤 Имя: {user.user_login}\n"
            f"🛒 Купленные товары: {bought_products_text}\n"
            f"📅 Дата регистрации: {user.registered_at.strftime('%d-%m-%Y')}\n"
        )

        await message.answer(profile_info, reply_markup=back_kb)

@dp.message_handler(Text(equals="Купить товар 🛒"), state="*")
async def choose_product(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.finish()
        if not await is_user_registered(message.from_user.id):
            await message.answer("Вы не зарегистрированы в системе. Пожалуйста, зарегистрируйтесь.", reply_markup=back_kb)
            return

        products = await get_available_products()
        if not products:
            await message.answer("К сожалению, доступных товаров нет.", reply_markup=back_kb)
            return

        product_buttons = [KeyboardButton(product.name) for product in products]
        product_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(*product_buttons).add(cancel_button)

        await message.answer("Выберите товар, который хотите купить:", reply_markup=product_kb)
        await PurchaseStates.choosing_product.set()

@dp.message_handler(state=PurchaseStates.choosing_product)
async def show_product_info(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        product_name = message.text.strip()
        if product_name == "Назад ⬅️":
            await state.finish()
            await message.answer("Вы вернулись в главное меню.", reply_markup=markup)
            return

        product = await get_product_by_name(product_name)

        if not product:
            await message.answer("Товар не найден. Попробуйте снова.", reply_markup=back_kb)
            return

        photo_id = product.photo.open('rb').read()
        product_info = (
            f"🛍️ Товар: {product.name}\n"
            f"💬 Описание: {product.description}\n"
            f"💰 : ⭐ {product.star}\n"
            f"ID товара: {product.id}\n"
        )

        await state.update_data(product_id=product.id)
        confirmation_kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Подтвердить покупку ✅", callback_data="confirm_purchase"),
            InlineKeyboardButton("Назад ⬅️", callback_data="back_to_products")
        )

        await bot.send_photo(chat_id=message.chat.id, photo=photo_id, caption=product_info, reply_markup=confirmation_kb)
        await PurchaseStates.confirming_purchase.set()

@dp.callback_query_handler(lambda c: c.data == "confirm_purchase", state=PurchaseStates.confirming_purchase)
async def confirm_purchase(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message = callback_query.message
    if message.chat.type == 'private':
        # Hide the "Подтвердить покупку" and "Назад" buttons
        await update_message_reply_markup(message)

        user_data = await get_user(callback_query.from_user.id)
        user = user_data[0]

        if not user:
            await message.answer("Вы не зарегистрированы в системе. Пожалуйста, зарегистрируйтесь.", reply_markup=back_kb)
            return

        data = await state.get_data()
        product_id = data.get("product_id")
        product = await get_product_by_id(product_id)

        if not product:
            await message.answer(f"Товар с ID {product_id} не найден. Попробуйте снова.", reply_markup=back_kb)
            return

        price = int(product.star)  # Convert to cents
        prices = [LabeledPrice(label=product.name, amount=price)]

        payment_keyboard = InlineKeyboardMarkup(row_width=1)
        payment_keyboard.add(InlineKeyboardButton("Оплатить", pay=True))
        payment_keyboard.add(InlineKeyboardButton("Отмена ❌", callback_data="cancel_purchase"))

        try:
            await bot.send_invoice(
                chat_id=message.chat.id,
                title=product.name,
                description=product.description,
                payload=f"product_{product.id}",
                provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",
                currency=CURRENCY,
                prices=prices,
                start_parameter="purchase_product",
                reply_markup=payment_keyboard
            )
            await PurchaseStates.waiting_for_payment.set()
        except Exception as e:
            print(f"Error sending invoice: {e}")
            await message.answer("Произошла ошибка при создании счета. Пожалуйста, попробуйте позже.", reply_markup=back_kb)
            await state.finish()

@dp.callback_query_handler(lambda c: c.data == "back_to_products", state=PurchaseStates.confirming_purchase)
async def back_to_products(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    products = await get_available_products()
    product_buttons = [KeyboardButton(product.name) for product in products]
    product_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(*product_buttons).add(cancel_button)
    await callback_query.message.answer("Выберите товар, который хотите купить:", reply_markup=product_kb)
    await PurchaseStates.choosing_product.set()

@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message, state: FSMContext):
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload

    product_id = int(payload.split('_')[1])

    product = await get_product_by_id(product_id)
    user, _ = await get_user(message.from_user.id)

    if not product or not user:
        await message.answer("Произошла ошибка при обработке платежа. Попробуйте снова.", reply_markup=back_kb)
        return

    await add_product_to_user(user, product)

    await message.answer(f"Спасибо за покупку! Вы приобрели {product.name}.", reply_markup=back_kb)

    product.stock -= 1
    await sync_to_async(product.save)()
    await message.answer("Товар успешно добавлен в ваш профиль.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "cancel_purchase", state=PurchaseStates.waiting_for_payment)
async def cancel_purchase(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    # Hide the "Отмена" button
    await update_message_reply_markup(callback_query.message)
    
    await callback_query.message.answer("Покупка отменена.", reply_markup=markup)
    await state.finish()

@dp.message_handler(Text(equals="Отмена ❌"), state="*")
async def cancel_action(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.finish()
        await message.answer("Действие отменено. Вы вернулись в главное меню.", reply_markup=markup)

@dp.message_handler(Text(equals="Назад ⬅️"), state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.finish()
        await message.answer("Вы вернулись в главное меню.", reply_markup=markup)

@sync_to_async
def is_user_registered(chat_id):
    return TelegramUser.objects.filter(chat_id=chat_id).exists()

@sync_to_async
def get_user(chat_id):
    user = TelegramUser.objects.filter(chat_id=chat_id).first()
    if user:
        bought_products = list(user.bought_products.all())
        return user, bought_products
    return None, []

@sync_to_async
def get_available_products():
    return list(Product.objects.filter(stock__gt=0))

@sync_to_async
def get_product_by_name(name):
    normalized_name = name.strip().lower() 
    return Product.objects.filter(name__iexact=normalized_name).first()

@sync_to_async
def get_product_by_id(product_id):
    return Product.objects.filter(id=product_id).first()

@sync_to_async
def add_product_to_user(user, product):
    user.bought_products.add(product)
    user.save()

async def update_message_reply_markup(message: types.Message):
    try:
        # Create a new keyboard without any buttons
        empty_keyboard = InlineKeyboardMarkup()
        
        # Edit the message to remove the buttons
        await message.edit_reply_markup(reply_markup=empty_keyboard)
    except Exception as e:
        print(f"Error updating message reply markup: {e}")

def catalog_handlers_register():
    dp.register_message_handler(view_profile, Text(equals="Просмотр своего профиля"))
    dp.register_message_handler(choose_product, Text(equals="Купить товар 🛒"), state="*")
    dp.register_message_handler(show_product_info, state=PurchaseStates.choosing_product)
    dp.register_callback_query_handler(confirm_purchase, lambda c: c.data == "confirm_purchase", state=PurchaseStates.confirming_purchase)
    dp.register_callback_query_handler(back_to_products, lambda c: c.data == "back_to_products", state=PurchaseStates.confirming_purchase)
    dp.register_callback_query_handler(cancel_purchase, lambda c: c.data == "cancel_purchase", state=PurchaseStates.waiting_for_payment)
    dp.register_message_handler(cancel_action, Text(equals="Отмена ❌"), state="*")
    dp.register_message_handler(back_to_main_menu, Text(equals="Назад ⬅️"), state="*")