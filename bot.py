import asyncio
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

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
from database import AsyncSessionLocal
from models import Product
from sqlalchemy import select
import barcode
from barcode.writer import ImageWriter

from io import BytesIO
from aiogram.types import BufferedInputFile

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

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product)
        )

        count = len(
            result.scalars().all()
        )

        sku = f"AFK{count + 1:06d}"

        product = Product(
            sku=sku,
            name=data["name"],
            image_file_id=data["image_file_id"],
            purchase_price=data["purchase_price"],
            sale_price=data["sale_price"],
            quantity=data["quantity"]
        )
        session.add(product)
        await session.commit()
        
    code128.write(barcode_buffer)
    
    barcode_buffer.seek(0)
    
    barcode_image = Image.open(
        barcode_buffer
    ).convert("RGB")
    
    # 58x40 mm (203 dpi ≈ 464x320)
    label = Image.new(
        "RGB",
        (464, 320),
        "white"
    )
    
    draw = ImageDraw.Draw(label)
    
    try:
        title_font = ImageFont.truetype(
            "arial.ttf",
            22
        )
    
        price_font = ImageFont.truetype(
            "arial.ttf",
            38
        )
    
        sku_font = ImageFont.truetype(
            "arial.ttf",
            16
        )
    
    except:
    
        title_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        sku_font = ImageFont.load_default()
    
    
    # Mahsulot nomi
    draw.text(
        (10, 8),
        data["name"].upper()[:25],
        fill="black",
        font=title_font
    )
    
    # Narx
    draw.text(
        (10, 40),
        f"{data['sale_price']:,} so'm",
        fill="black",
        font=price_font
    )
    
    # SKU
    draw.text(
        (10, 88),
        sku,
        fill="black",
        font=sku_font
    )
    
    # Barcode
    barcode_image = barcode_image.resize(
        (430, 140)
    )
    
    label.paste(
        barcode_image,
        (17, 120)
    )
    
    final_buffer = BytesIO()
    
    label.save(
        final_buffer,
        format="PNG"
    )
    
    final_buffer.seek(0)
    
    label_file = BufferedInputFile(
        final_buffer.getvalue(),
        filename=f"{sku}.png"
    )
    
    await message.answer_photo(
        label_file,
        caption=f"""
    ✅ Mahsulot saqlandi
    
    📦 {data['name']}
    🏷 SKU: {sku}
    
    💰 Sotuv: {data['sale_price']:,} so'm
    📊 Miqdor: {data['quantity']}
    """
    )

    await state.clear()

from models import Base
from database import engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )


async def main():

    await create_tables()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
