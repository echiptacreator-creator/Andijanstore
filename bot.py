import asyncio
import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F

from aiogram.filters import CommandStart

from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from states import ProductCreate


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)

dp = Dispatcher(
    storage=MemoryStorage()
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="➕ Mahsulot qo'shish"
            )
        ]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "Andijon Store",
        reply_markup=menu
    )


@dp.message(F.text == "➕ Mahsulot qo'shish")
async def create_product(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ProductCreate.image
    )

    await message.answer(
        "📸 Mahsulot rasmini yuboring"
    )


@dp.message(ProductCreate.image)
async def get_image(
    message: Message,
    state: FSMContext
):

    if not message.photo:

        await message.answer(
            "Rasm yuboring"
        )

        return

    await state.update_data(
        image_file_id=message.photo[-1].file_id
    )

    await state.set_state(
        ProductCreate.name
    )

    await message.answer(
        "Mahsulot nomi?"
    )


@dp.message(ProductCreate.name)
async def get_name(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        name=message.text
    )

    await state.set_state(
        ProductCreate.purchase_price
    )

    await message.answer(
        "Kelish narxi?"
    )


@dp.message(ProductCreate.purchase_price)
async def get_purchase(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        purchase_price=int(message.text)
    )

    await state.set_state(
        ProductCreate.sale_price
    )

    await message.answer(
        "Sotuv narxi?"
    )


@dp.message(ProductCreate.sale_price)
async def get_sale(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        sale_price=int(message.text)
    )

    await state.set_state(
        ProductCreate.quantity
    )

    await message.answer(
        "Miqdori?"
    )


@dp.message(ProductCreate.quantity)
async def get_quantity(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        quantity=int(message.text)
    )

    data = await state.get_data()

    await message.answer(
        f"""
✅ Mahsulot qabul qilindi

📦 {data['name']}

💰 Kelish: {data['purchase_price']}
🏷 Sotuv: {data['sale_price']}
📊 Miqdor: {data['quantity']}
"""
    )

    await state.clear()


async def main():

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())