from aiogram.fsm.state import State, StatesGroup

class ProductCreate(StatesGroup):
    image = State()
    name = State()
    purchase_price = State()
    sale_price = State()

    sizes = State()
    
    confirm = State()


class ProductSearch(StatesGroup):
    select_product = State()
    page = State()

class ExpenseCreate(StatesGroup):

    title = State()
    amount = State()
    payment_type = State()


class SaleCreate(StatesGroup):

    sku = State()
    size = State()
    quantity = State()

    payment = State()
    extras = State()

    confirm = State()
