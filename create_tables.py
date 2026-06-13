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

        await conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS is_posted BOOLEAN DEFAULT FALSE
        """))
        
