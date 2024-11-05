from aiogram.dispatcher.filters.state import State, StatesGroup

class ForgotPasswordState(StatesGroup):
    user_login = State()
    user_password = State()
    user_password_2 = State()