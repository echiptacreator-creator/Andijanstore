import asyncio
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from database import (
    AsyncSessionLocal,
    engine
)
from models import Sale

from states import SaleCreate
from models import Expense
from states import ExpenseCreate
from datetime import datetime
from sqlalchemy import func
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F
from pyzbar.pyzbar import decode
from PIL import Image
from aiogram.filters import CommandStart

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
        ProductCreate.size_s
    )
    
    await message.answer(
        "📏 S razmer nechta?"
    )


@dp.message(ProductCreate.size_s)
async def get_s(message: Message, state: FSMContext):

    await state.update_data(
        s=int(message.text)
    )

    await state.set_state(
        ProductCreate.size_m
    )

    await message.answer(
        "📏 M razmer nechta?"
    )


@dp.message(ProductCreate.size_m)
async def get_m(message: Message, state: FSMContext):

    await state.update_data(
        m=int(message.text)
    )

    await state.set_state(
        ProductCreate.size_l
    )

    await message.answer(
        "📏 L razmer nechta?"
    )


@dp.message(ProductCreate.size_l)
async def get_l(message: Message, state: FSMContext):

    await state.update_data(
        l=int(message.text)
    )

    await state.set_state(
        ProductCreate.size_xl
    )

    await message.answer(
        "📏 XL razmer nechta?"
    )

@dp.message(ProductCreate.size_xl)
async def get_xl(message: Message, state: FSMContext):

    await state.update_data(
        xl=int(message.text)
    )

    await state.set_state(
        ProductCreate.size_xxl
    )
    
    await message.answer(
        "📏 XXL razmer nechta?"
    )

@dp.message(ProductCreate.size_xxl)
async def get_xxl(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        xxl=int(message.text)
    )

    await state.set_state(
        ProductCreate.size_xxxl
    )

    await message.answer(
        "📏 XXXL razmer nechta?"
    )

@dp.message(ProductCreate.size_xxxl)
async def get_xxxl(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        xxxl=int(message.text)
    )

    data = await state.get_data()

    total = (
        data["s"] +
        data["m"] +
        data["l"] +
        data["xl"] +
        data["xxl"] +
        data["xxxl"]
    )

    await state.update_data(
        quantity=total
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tasdiqlash")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        ProductCreate.confirm
    )

    await message.answer(
        f"""
📦 {data['name']}

S: {data['s']}
M: {data['m']}
L: {data['l']}
XL: {data['xl']}
XXL: {data['xxl']}
XXXL: {data['xxxl']}

📊 Jami: {total} dona

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
    
    total = (
        data["s"] +
        data["m"] +
        data["l"] +
        data["xl"] +
        data["xxl"] +
        data["xxxl"]
    )

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
        
            quantity=total,
        
            size_s=data["s"],
            size_m=data["m"],
            size_l=data["l"],
            size_xl=data["xl"],
            size_xxl=data["xxl"],
            size_xxxl=data["xxxl"]
        )

        session.add(product)

        await session.commit()
#============================================================
        caption = f"""
        🏷 {data['name']}
        
        💰 Narx: {data['sale_price']:,} so'm
        
        📦 Mavjud: {data['quantity']} dona
        """
        
        await bot.send_photo(
            chat_id=GROUP_ID,
            photo=data["image_file_id"],
            caption=caption
        )
       

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
a
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

    await state.set_state(
        SaleCreate.barcode
    )

    await message.answer(
        "📷 Shtrix kod yuboring yoki skaner qiling"
    )

@dp.message(SaleCreate.barcode)
async def get_barcode(
    message: Message,
    state: FSMContext
):

    sku = None

    # Skaner yuborgan matn
    if message.text:
        sku = message.text.strip()

    # Barcode rasmi
    elif message.photo:

        file = await bot.get_file(
            message.photo[-1].file_id
        )

        file_bytes = await bot.download_file(
            file.file_path
        )

        image = Image.open(file_bytes)

        decoded = decode(image)

        if decoded:
            sku = decoded[0].data.decode("utf-8")

    if not sku:

        await message.answer(
            "❌ Barcode o'qilmadi"
        )
        return

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product).where(
                Product.sku == sku
            )
        )

        product = result.scalar_one_or_none()

    if not product:

        await message.answer(
            f"❌ Mahsulot topilmadi\nSKU: {sku}"
        )
        return

    await state.update_data(
        product_id=product.id
    )

    await message.answer(
        f"""
📦 {product.name}

💰 {product.sale_price:,} so'm

Razmer tanlang
"""
    )

    await state.set_state(
        SaleCreate.size
    )

    await state.update_data(
        product_id=product.id
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"S ({product.size_s})",
                    callback_data="size_S"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"M ({product.size_m})",
                    callback_data="size_M"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"L ({product.size_l})",
                    callback_data="size_L"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"XL ({product.size_xl})",
                    callback_data="size_XL"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"XXL ({product.size_xxl})",
                    callback_data="size_XXL"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"XXXL ({product.size_xxxl})",
                    callback_data="size_XXXL"
                )
            ]
        ]
    )

    await state.set_state(
        SaleCreate.size
    )

    await message.answer(
        f"""
📦 {product.name}

💰 {product.sale_price:,} so'm

Razmer tanlang
""",
        reply_markup=kb
    )









async def main():

    await create_tables()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
