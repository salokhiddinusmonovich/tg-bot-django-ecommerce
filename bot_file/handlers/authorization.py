import re

from aiogram.dispatcher.filters import Text
from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password, check_password
from ..loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from ..models import TelegramUser
from ..states import auth_state, signin_state, forgot_password_state
from ..keyboards.registration_bg import markup, markup_cancel_forgot_password
from ..keyboards import default_kb, sign_inup_kb


new_user = {}
sign_in = {'current_state': False}
update_date = {}


REGISTRATION_TEXT = """
Для регистрации сначала напишите свой логин!

Из чего должен состоять логин?
    - Логин должен состоять только из <b>латинских букв</b>!
    - Длинна логина должна быть <b>больше 3 символов(букв и цифр)</b>
    - Логин должен быть <b>уникальным и не повторяющимися</b>
    
Перед тем как отрпавить логин перепроверьте его!
"""


# @dp.message_handler(Text(equals='Отмена ❌', ignore_case=True), state='*')
async def command_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_data()
    if current_state is None:
        return
    await state.finish()
    await message.answer(text="Операция успешно отменена 🙅‍", reply_markup=sign_inup_kb.markup)



# @dp.message_handler(Text(equals='Регистрация ✌️'), state='*')
async def prpcess_registration(message: types.Message):
    await message.answer(REGISTRATION_TEXT, reply_markup=markup)
    await auth_state.AuthState.user_login.set()



def authorization_handlers_register():
    dp.register_message_handler(command_cancel, Text(equals='Отмена ❌', ignore_case=True), state='*')
    dp.message_handler(Text(equals='Регистрация ✌️'), state='*')



