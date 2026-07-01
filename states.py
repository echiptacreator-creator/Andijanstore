from aiogram.fsm.state import State, StatesGroup


# ==========================
# PRODUCT CREATE
# ==========================
class ProductCreate(StatesGroup):
    image = State()
    name = State()
    purchase_price = State()
    sale_price = State()

    # Misol:
    # S=5
    # M=8
    # L=10
    #
    # yoki
    #
    # 26=5
    # 28=8
    # 30=10
    sizes = State()

    confirm = State()


# ==========================
# PRODUCT SEARCH
# ==========================
class ProductSearch(StatesGroup):
    select_product = State()
    page = State()


# ==========================
# EXPENSE
# ==========================
class ExpenseCreate(StatesGroup):
    title = State()
    amount = State()
    payment_type = State()


# ==========================
# SALE
# ==========================
class SaleCreate(StatesGroup):
    sku = State()

    # Dinamik razmer (S, 26, FREE...)
    size = State()

    quantity = State()

    payment = State()
    extras = State()

    confirm = State()
