import asyncio

from sqlalchemy import text

from database import engine
from models import Base


async def create():

    async with engine.begin() as conn:

        print("Creating tables...")

        await conn.run_sync(
            Base.metadata.create_all
        )

        print("Adding size columns...")

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_s INTEGER DEFAULT 0
        """))

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_m INTEGER DEFAULT 0
        """))

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_l INTEGER DEFAULT 0
        """))

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS size_xl INTEGER DEFAULT 0
        """))

        print("Done!")


if __name__ == "__main__":
    asyncio.run(create())
    
