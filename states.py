from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class ProductCreate(StatesGroup):

    image = State()

    name = State()

    purchase_price = State()

    sale_price = State()

    quantity = State()
    
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup

class ProductCreate(StatesGroup):
    image = State()
    name = State()
    purchase_price = State()
    sale_price = State()
    sizes = State()      # yangi
    quantity = State()


class ProductSearch(StatesGroup):

    select_product = State()


from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup

class ProductSearch(StatesGroup):
    select_product = State()
    page = State()


