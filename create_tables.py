import asyncio

from database import engine
from sqlalchemy import text


async def create():

    async with engine.begin() as conn:

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_xxl INTEGER DEFAULT 0
        """))

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_xxxl INTEGER DEFAULT 0
        """))

        print("OK")


asyncio.run(create())
