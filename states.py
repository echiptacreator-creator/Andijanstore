from aiogram.fsm.state import State, StatesGroup


class ProductCreate(StatesGroup):
    image = State()
    name = State()
    purchase_price = State()
    sale_price = State()

    size_s = State()
    size_m = State()
    size_l = State()
    size_xl = State()
    size_xxl = State()
    size_xxxl = State()
    
    confirm = State()


class ProductSearch(StatesGroup):
    select_product = State()
    page = State()
