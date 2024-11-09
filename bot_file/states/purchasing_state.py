from aiogram.dispatcher.filters.state import StatesGroup, State


class PurchaseState(StatesGroup):
    choosing_product = State() 
    confirming_purchase = State() 