import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def get_connection():
    try:  
        return await asyncpg.connect(
            user="postgres",
            password=os.getenv("PASSWORD_DB"),
            database="exam_pet",   
            host="localhost",
            port=5432
        )
        print("connect is okay")
    except Exception as er:
        print("Connection is error: ", er)

async def create_tables():
    con = await get_connection()
    try:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                content TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
            )
        """)

    except Exception as e:
        print("Ошибка создания таблиц:", e)

    finally:
        await con.close()