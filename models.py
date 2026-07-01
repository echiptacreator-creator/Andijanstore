from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


# ==========================
# PRODUCTS
# ==========================

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    image_file_id: Mapped[str] = mapped_column(
        String(255)
    )

    purchase_price: Mapped[int] = mapped_column(
        Integer
    )

    sale_price: Mapped[int] = mapped_column(
        Integer
    )

    # Ombordagi jami soni
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    # JSON ko'rinishida saqlanadi
    # Misol:
    # {"S":5,"M":8}
    # {"26":7,"28":9}
    # {"FREE":15}
    sizes: Mapped[str] = mapped_column(
        String(1000),
        default="{}"
    )


# ==========================
# SALES
# ==========================

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        Integer
    )

    size: Mapped[str] = mapped_column(
        String(30)
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    payment_type: Mapped[str] = mapped_column(
        String(50)
    )

    bag_price: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    gift_price: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    total_price: Mapped[int] = mapped_column(
        Integer
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================
# EXPENSES
# ==========================

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    amount: Mapped[int] = mapped_column(
        Integer
    )

    payment_type: Mapped[str] = mapped_column(
        String(50)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
