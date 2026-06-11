from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from sqlalchemy import Integer


class Base(DeclarativeBase):
    pass


class Product(Base):

    __tablename__ = "products"

    id = mapped_column(
        primary_key=True
    )

    name = mapped_column(
        String(255)
    )

    image_file_id = mapped_column(
        String(255)
    )

    purchase_price = mapped_column(
        Integer
    )

    sale_price = mapped_column(
        Integer
    )

    quantity = mapped_column(
        Integer
    )