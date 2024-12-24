from aiogram.dispatcher.filters.state import StatesGroup, State


class PurchaseStates(StatesGroup):
    choosing_product = State()
    confirming_purchase = State()