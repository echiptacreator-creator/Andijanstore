import asyncio

from database import engine
from models import Base
from sqlalchemy import text
from sqlalchemy import text

async def create():

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
        
        await conn.execute(text("""
        ALTER TABLE products
        ADD COLUMN IF NOT EXISTS is_posted BOOLEAN DEFAULT FALSE
        """))

        print("XXL va XXXL qo'shildi")


asyncio.run(create())
