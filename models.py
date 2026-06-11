from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from sqlalchemy import Integer


class Base(DeclarativeBase):
    pass


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

    quantity: Mapped[int] = mapped_column(
        Integer
    )
