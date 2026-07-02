import asyncio
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from database import (
    AsyncSessionLocal,
    engine
)
import json
import easyocr
import re
import cv2
import numpy as np
from models import Sale
from PIL import Image
from states import SaleCreate
from models import Expense
from states import ExpenseCreate
from datetime import datetime
from sqlalchemy import func
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F
from PIL import Image
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from states import (
    ProductCreate,
    ProductSearch
)
from database import AsyncSessionLocal
from models import (
    Product,
    Base
)
from sqlalchemy import select
import barcode
from barcode.writer import ImageWriter

from io import BytesIO
from aiogram.types import BufferedInputFile

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -5288325150
bot = Bot(TOKEN)

dp = Dispatcher(
    storage=MemoryStorage()
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🛒 Sotuv"
            )
        ],
        [
            KeyboardButton(
                text="➕ Mahsulot qo'shish"
            )
        ],
        [
            KeyboardButton(
                text="🧾 Narx chek chiqarish"
            )
        ],
        [
            KeyboardButton(
                text="📢 Mahsulotlarni chiqarish"
            )
        ],
        [
            KeyboardButton(
                text="💸 Harajat"
            )
        ],

        [
            KeyboardButton(
                text="📊 Hisobot"
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

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


@dp.message(F.text == "➕ Mahsulot qo'shish")
async def create_product(
    message: Message,
    state: FSMContext
):

    await state.clear()

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
        ProductCreate.sizes
    )

    await message.answer(
        "Razmerlarni kiriting.\n\n"
        "Misol:\n"
        "S=5\n"
        "M=8\n"
        "L=4\n\n"
        "yoki\n\n"
        "26=5\n"
        "28=10\n"
        "30=6"
    )

def parse_sizes(text: str):

    result = {}

    lines = text.replace(",", "\n").split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "=" not in line:
            continue

        size, qty = line.split("=")

        result[size.strip().upper()] = int(qty.strip())

    return result


async def save_product(
    message: Message,
    state: FSMContext
):

    result = {}

    lines = text.replace(",", "\n").split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "=" not in line:
            continue

        size, qty = line.split("=")

        result[size.strip().upper()] = int(
            qty.strip()
        )

    return result

@dp.message(ProductCreate.sizes)
async def get_sizes(
    message: Message,
    state: FSMContext
):
    try:
        sizes = parse_sizes(message.text)
    except:
        await message.answer(
            "❌ Format noto'g'ri.\n\n"
            "Misol:\n"
            "S=5\n"
            "M=10\n"
            "L=7\n\n"
            "yoki\n"
            "26=5\n"
            "28=8\n"
            "30=10"
        )
        return

    if not sizes:
        await message.answer(
            "❌ Hech qanday razmer topilmadi."
        )
        return

    total = sum(sizes.values())

    await state.update_data(
        sizes=sizes,
        quantity=total
    )

    data = await state.get_data()

    sizes_text = ""

    for size, qty in sizes.items():
        sizes_text += f"{size} = {qty} ta\n"

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tasdiqlash")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

    await state.set_state(ProductCreate.confirm)

    await message.answer(
        f"""
📦 Mahsulot: {data['name']}

📏 Razmerlar:

{sizes_text}

📦 Jami: {total} ta

Tasdiqlaysizmi?
""",
        reply_markup=kb
    )

@dp.message(
    ProductCreate.confirm,
    F.text == "✅ Tasdiqlash"
)
async def save_product(
    message: Message,
    state: FSMContext
):


    data = await state.get_data()

    if "sizes" not in data:
        await message.answer("❌ Razmerlar topilmadi.")
        return
        
    total = data["quantity"]

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
            quantity=data["quantity"],
            sizes=json.dumps(data["sizes"])
        )

        session.add(product)

        await session.commit()
#============================================================
        sizes_text = "\n".join(
            f"{k}: {v} ta"
            for k, v in data["sizes"].items()
        )
        
        caption = f"""
        🏷 {data['name']}
        
        💰 Narx: {data['sale_price']:,} so'm
        
        📦 Jami: {data['quantity']} ta
        
        📏 Razmerlar:
        
        {sizes_text}
        """
       

#============================================================
        
        await session.commit()
    
    code128 = barcode.get(
        "code128",
        sku,
        writer=ImageWriter()
    )
    
    barcode_buffer = BytesIO()
    
    code128.write(
        barcode_buffer,
        {
            "write_text": False,
            "module_height": 25,
            "module_width": 0.35,
            "quiet_zone": 2
        }
    )
    
    barcode_buffer.seek(0)
    
    barcode_image = Image.open(
        barcode_buffer
    ).convert("RGB")

    # 58x40 mm (203 dpi)
    label = Image.new(
        "RGB",
        (464, 320),
        "white"
    )
    
    draw = ImageDraw.Draw(label)
    
    try:
        title_font = ImageFont.truetype(
            "Nekst-Bold.ttf",
            34
        )
    
        price_font = ImageFont.truetype(
            "Nekst-Bold.ttf",
            56
        )
    
        sku_font = ImageFont.truetype(
            "Nekst-Bold.ttf",
            22
        )
    
    except:
        title_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        sku_font = ImageFont.load_default()
    
    
    # NOM
    name_text = data["name"].upper()
    
    if len(name_text) > 20:
        name_text = name_text[:20]
    
    bbox = draw.textbbox(
        (0, 0),
        name_text,
        font=title_font
    )
    
    draw.text(
        (
            (464 - (bbox[2] - bbox[0])) // 2,
            10
        ),
        name_text,
        fill="black",
        font=title_font
    )
    
    
    # NARX
    price_text = f"{data['sale_price']:,} so'm"
    
    bbox = draw.textbbox(
        (0, 0),
        price_text,
        font=price_font
    )
    
    draw.text(
        (
            (464 - (bbox[2] - bbox[0])) // 2,
            55
        ),
        price_text,
        fill="black",
        font=price_font
    )
    
    
    # BARCODE
    barcode_image = barcode_image.crop(
        (
            20,
            20,
            barcode_image.width - 20,
            barcode_image.height - 20
        )
    )
    
    barcode_image = barcode_image.resize(
        (430, 110)
    )
    
    label.paste(
        barcode_image,
        (17, 135)
    )
    
    
    # SKU
    bbox = draw.textbbox(
        (0, 0),
        sku,
        font=sku_font
    )
    
    draw.text(
        (
            (464 - (bbox[2] - bbox[0])) // 2,
            280
        ),
        sku,
        fill="black",
        font=sku_font
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
    
    sent_message = await message.answer_photo(
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
    
    await message.answer(
        "🏠 Bosh menyu",
        reply_markup=menu
    )


from sqlalchemy import text

async def create_tables():

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_xxl INTEGER DEFAULT 0
        """))

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_xxxl INTEGER DEFAULT 0
        """))


#from models import Base
#from database import engine

#async def create_tables():
 #   async with engine.begin() as conn:
  #      await conn.run_sync(
   #         Base.metadata.create_all
    #    )


@dp.message(F.text == "🧾 Narx chek chiqarish")
async def price_label(
    message: Message,
    state: FSMContext
):

    await state.clear()

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product)
        )

        products = result.scalars().all()

    await state.set_state(
        ProductSearch.select_product
    )
    
    await state.update_data(
        products=[p.name for p in products],
        page=0
    )
    
    await show_products(
        message,
        products,
        0
    )
    await state.update_data(
        page=0
    )


async def show_products(
    message: Message,
    products,
    page
):

    per_page = 10

    start = page * per_page
    end = start + per_page

    current = products[start:end]

    buttons = []

    for product in current:

        buttons.append(
            [KeyboardButton(text=product.name)]
        )

    nav = []

    if page > 0:
        nav.append(
            KeyboardButton(text="⬅️ Oldingi")
        )

    if end < len(products):
        nav.append(
            KeyboardButton(text="➡️ Keyingi")
        )
    if nav:
        buttons.append(nav)
    
    buttons.append(
        [
            KeyboardButton(
                text="❌ Bekor qilish"
            )
        ]
    )
    
    kb = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await message.answer(
        f"Sahifa: {page + 1}",
        reply_markup=kb
    )


    # shu yerda sen ishlatayotgan
    # barcode + etiketka kodi ishlaydi




@dp.message(
    ProductSearch.select_product,
    ~F.text.in_(
        [
            "➡️ Keyingi",
            "⬅️ Oldingi",
            "❌ Bekor qilish"
        ]
    )
)
async def select_product(
    message: Message,
    state: FSMContext
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product).where(
                Product.name == message.text
            )
        )

        product = result.scalar_one_or_none()

    if not product:

        await message.answer(
            "Mahsulot topilmadi"
        )
        return

    sku = product.sku

    code128 = barcode.get(
        "code128",
        sku,
        writer=ImageWriter()
    )

    barcode_buffer = BytesIO()

    code128.write(
        barcode_buffer,
        {
            "write_text": False,
            "module_height": 25,
            "module_width": 0.35,
            "quiet_zone": 2
        }
    )

    barcode_buffer.seek(0)

    barcode_image = Image.open(
        barcode_buffer
    ).convert("RGB")

    label = Image.new(
        "RGB",
        (464, 320),
        "white"
    )

    draw = ImageDraw.Draw(label)

    try:

        title_font = ImageFont.truetype(
            "Nekst-Bold.ttf",
            34
        )

        price_font = ImageFont.truetype(
            "Nekst-Bold.ttf",
            56
        )

        sku_font = ImageFont.truetype(
            "Nekst-Bold.ttf",
            22
        )

    except:

        title_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        sku_font = ImageFont.load_default()

    name_text = product.name.upper()

    bbox = draw.textbbox(
        (0, 0),
        name_text,
        font=title_font
    )

    draw.text(
        (
            (464 - (bbox[2] - bbox[0])) // 2,
            10
        ),
        name_text,
        fill="black",
        font=title_font
    )

    price_text = f"{product.sale_price:,} so'm"

    bbox = draw.textbbox(
        (0, 0),
        price_text,
        font=price_font
    )

    draw.text(
        (
            (464 - (bbox[2] - bbox[0])) // 2,
            55
        ),
        price_text,
        fill="black",
        font=price_font
    )

    barcode_image = barcode_image.crop(
        (
            20,
            20,
            barcode_image.width - 20,
            barcode_image.height - 20
        )
    )

    barcode_image = barcode_image.resize(
        (430, 110)
    )

    label.paste(
        barcode_image,
        (17, 135)
    )

    bbox = draw.textbbox(
        (0, 0),
        sku,
        font=sku_font
    )

    draw.text(
        (
            (464 - (bbox[2] - bbox[0])) // 2,
            280
        ),
        sku,
        fill="black",
        font=sku_font
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
        caption=f"{product.name}"
    )


@dp.message(
    ProductSearch.select_product,
    F.text == "❌ Bekor qilish"
)
async def cancel(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "Bosh menyu",
        reply_markup=menu
    )




@dp.message(
    ProductSearch.select_product,
    F.text == "➡️ Keyingi"
)
async def next_page(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    page = data.get("page", 0)

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product)
        )

        products = result.scalars().all()

    page += 1

    await state.update_data(
        page=page
    )

    await show_products(
        message,
        products,
        page
    )

@dp.message(
    ProductSearch.select_product,
    F.text == "⬅️ Oldingi"
)
async def prev_page(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    page = data.get("page", 0)

    if page > 0:
        page -= 1

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product)
        )

        products = result.scalars().all()

    await state.update_data(
        page=page
    )

    await show_products(
        message,
        products,
        page
    )
    

@dp.message(F.text == "📢 Mahsulotlarni chiqarish")
async def publish_products(message: Message):

    count = 0

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product)
            )

        products = result.scalars().all()

        for product in products:

            caption = f"""
⚽ {product.name}

💰 {product.sale_price:,} so'm

📏 Razmerlar: S • M • L • XL • XXL • XXXL

🚚 Yetkazib berish mavjud

🛒 Onlayn xarid:
Echipta ilovasi orqali

⚠️ Mahsulot soni cheklangan
"""

            await bot.send_photo(
                chat_id=GROUP_ID,
                photo=product.image_file_id,
                caption=caption
            )


            count += 1

        await session.commit()

    await message.answer(
        f"✅ {count} ta mahsulot guruhga chiqarildi"
    )

@dp.message(F.text == "💸 Harajat")
async def expense_start(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ExpenseCreate.title
    )

    await message.answer(
        "Harajat maqsadini kiriting"
    )

@dp.message(ExpenseCreate.title)
async def expense_title(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        title=message.text
    )

    await state.set_state(
        ExpenseCreate.amount
    )

    await message.answer(
        "Summani kiriting"
    )

@dp.message(ExpenseCreate.amount)
async def expense_amount(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "Faqat raqam kiriting"
        )

        return

    await state.update_data(
        amount=int(message.text)
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="💵 Naqd"
                ),
                KeyboardButton(
                    text="💳 Karta"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        ExpenseCreate.payment_type
    )

    await message.answer(
        "To'lov turini tanlang",
        reply_markup=kb
    )

@dp.message(ExpenseCreate.payment_type)
async def expense_save(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    async with AsyncSessionLocal() as session:

        expense = Expense(
            title=data["title"],
            amount=data["amount"],
            payment_type=message.text
        )

        session.add(expense)

        await session.commit()

    await state.clear()

    await message.answer(
        f"""
✅ Harajat saqlandi

📌 {data['title']}
💰 {data['amount']:,} so'm
{message.text}
        """,
        reply_markup=menu
    )


@dp.message(F.text == "📊 Hisobot")
async def report(
    message: Message
):

    today = datetime.now().date()

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Expense).where(
                func.date(
                    Expense.created_at
                ) == today
            )
        )

        expenses = result.scalars().all()

    total = sum(
        x.amount
        for x in expenses
    )

    text = f"""
📊 Bugungi hisobot

💸 Jami harajat:
{total:,} so'm

"""

    for item in expenses:

        text += (
            f"\n• {item.title}"
            f" - {item.amount:,}"
        )

    await message.answer(text)



@dp.message(F.text == "🛒 Sotuv")
async def start_sale(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await state.update_data(
        cart=[]
    )

    await state.set_state(
        SaleCreate.sku
    )

    await message.answer(
        "📷 SKU ni yuboring yoki skaner qiling"
    )

@dp.message(
    SaleCreate.sku,
    ~F.text.in_([
        "➕ Savat mahsulot",
        "✅ Sotuvni yakunlash",
        "❌ Bekor qilish"
    ])
)
async def get_sku(
    message: Message,
    state: FSMContext
):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product).where(
                Product.sku == message.text.upper()
            )
        )

        product = result.scalar_one_or_none()

    if not product:

        await message.answer(
            "❌ Mahsulot topilmadi"
        )

        return

    await state.update_data(
        product_id=product.id
    )
    
    buttons = []
    
    row1 = []
    row2 = []
    
    if product.size_s > 0:
        row1.append(
            KeyboardButton(text="S")
        )
    
    if product.size_m > 0:
        row1.append(
            KeyboardButton(text="M")
        )
    
    if product.size_l > 0:
        row1.append(
            KeyboardButton(text="L")
        )
    
    if product.size_xl > 0:
        row2.append(
            KeyboardButton(text="XL")
        )
    
    if product.size_xxl > 0:
        row2.append(
            KeyboardButton(text="XXL")
        )
    
    if product.size_xxxl > 0:
        row2.append(
            KeyboardButton(text="XXXL")
        )
    
    if row1:
        buttons.append(row1)
    
    if row2:
        buttons.append(row2)
    
    kb = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await state.set_state(
        SaleCreate.size
    )

    await message.answer(
        f"📏 {product.name}\n\nRazmer tanlang",
        reply_markup=kb
    )
    
    
@dp.message(SaleCreate.size)
async def get_size(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        size=message.text
    )

    await state.set_state(
        SaleCreate.quantity
    )

    await message.answer(
        "Nechta?"
    )

@dp.message(SaleCreate.quantity)
async def get_sale_quantity(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "Faqat son kiriting"
        )

        return

    qty = int(message.text)

    data = await state.get_data()

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product).where(
                Product.id == data["product_id"]
            )
        )

        product = result.scalar_one()

    available = 0

    if data["size"] == "S":
        available = product.size_s

    elif data["size"] == "M":
        available = product.size_m

    elif data["size"] == "L":
        available = product.size_l

    elif data["size"] == "XL":
        available = product.size_xl

    elif data["size"] == "XXL":
        available = product.size_xxl

    elif data["size"] == "XXXL":
        available = product.size_xxxl

    if qty > available:

        await message.answer(
            f"❌ Omborda faqat {available} dona mavjud"
        )

        return

    cart = data.get("cart", [])

    cart.append(
        {
            "product_id": product.id,
            "name": product.name,
            "size": data["size"],
            "quantity": qty,
            "price": product.sale_price
        }
    )

    await state.update_data(
        cart=cart
    )

    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    await state.set_state(
        SaleCreate.sku
    )
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="➕ Savat mahsulot"
                )
            ],
            [
                KeyboardButton(
                    text="✅ Sotuvni yakunlash"
                )
            ],
            [
                KeyboardButton(
                    text="❌ Bekor qilish"
                )
            ]
        ],
        resize_keyboard=True
    )
    
    cart_text = ""
    
    for i, item in enumerate(cart, start=1):
    
        cart_text += (
            f"{i}) {item['name']} "
            f"({item['size']}) "
            f"x{item['quantity']}\n"
        )
    
    await message.answer(
        f"""
    ✅ Savatga qo'shildi
    
    📦 {product.name}
    📏 {data['size']}
    🔢 {qty} dona
    
    ━━━━━━━━━━
    
    🛒 Savat:
    
    {cart_text}
    
    💰 Jami: {total:,} so'm
    """,
        reply_markup=kb
    )
@dp.message(
    SaleCreate.sku,
    F.text == "➕ Savat mahsulot"
)
async def add_more_products(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        SaleCreate.sku
    )

    await message.answer(
        "📦 SKU kiriting yoki skaner qiling"
    )

@dp.message(F.text == "❌ Bekor qilish")
async def cancel_sale(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "❌ Sotuv bekor qilindi",
        reply_markup=menu
    )

@dp.message(
    SaleCreate.sku,
    F.text == "✅ Sotuvni yakunlash"
)
async def finish_sale(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    cart = data.get(
        "cart",
        []
    )

    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="💵 Naqd"
                )
            ],
            [
                KeyboardButton(
                    text="💳 Karta"
                )
            ],
            [
                KeyboardButton(
                    text="🔀 Aralash"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        SaleCreate.payment
    )

    await message.answer(
        f"""
💰 Jami: {total:,} so'm

To'lov turini tanlang
""",
        reply_markup=kb
    )


@dp.message(SaleCreate.payment)
async def sale_payment(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        payment=message.text
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🎁 Sovg'a paket (+15 000)"
                )
            ],
            [
                KeyboardButton(
                    text="➡️ Davom etish"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.update_data(
        gift_price=0
    )

    await state.set_state(
        SaleCreate.extras
    )

    await message.answer(
        "🎁 Sovg'a paket kerakmi?",
        reply_markup=kb
    )

@dp.message(SaleCreate.extras)
async def sale_extras(
    message: Message,
    state: FSMContext
):

    if message.text == "🎁 Sovg'a paket (+15 000)":

        await state.update_data(
            gift_price=15000
        )

        await message.answer(
            "✅ Sovg'a paket qo'shildi"
        )

        return

    if message.text != "➡️ Davom etish":
        return

    data = await state.get_data()

    cart = data["cart"]

    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    total += data.get(
        "gift_price",
        0
    )

    text = "🧾 Yakuniy chek\n\n"

    for item in cart:

        text += (
            f"📦 {item['name']}\n"
            f"📏 {item['size']} x {item['quantity']}\n\n"
        )

    if data.get("gift_price", 0):

        text += (
            "🎁 Sovg'a paket\n"
            "15 000 so'm\n\n"
        )

    text += f"💰 Jami: {total:,} so'm"
    text += f"\n💳 To'lov: {data['payment']}"

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="✅ Tasdiqlash"
                )
            ],
            [
                KeyboardButton(
                    text="❌ Bekor qilish"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.update_data(
        final_total=total
    )

    await state.set_state(
        SaleCreate.confirm
    )

    await message.answer(
        text,
        reply_markup=kb
    )


@dp.message(
    SaleCreate.confirm,
    F.text == "✅ Tasdiqlash"
)
async def confirm_sale(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    cart = data["cart"]

    async with AsyncSessionLocal() as session:

        for item in cart:

            result = await session.execute(
                select(Product).where(
                    Product.id == item["product_id"]
                )
            )

            product = result.scalar_one()

            qty = item["quantity"]

            if item["size"] == "S":
                product.size_s -= qty

            elif item["size"] == "M":
                product.size_m -= qty

            elif item["size"] == "L":
                product.size_l -= qty

            elif item["size"] == "XL":
                product.size_xl -= qty

            elif item["size"] == "XXL":
                product.size_xxl -= qty

            elif item["size"] == "XXXL":
                product.size_xxxl -= qty

            product.quantity -= qty

        await session.commit()

    await state.clear()

    await message.answer(
        f"""
✅ Sotuv yakunlandi

💰 {data['final_total']:,} so'm
""",
        reply_markup=menu
    )




async def main():

    await create_tables()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
