from connector import get_connection


async def add_user(telegram_id, username):
    con = await get_connection()
    try:
        await con.execute("""
            INSERT INTO users (telegram_id, username) VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE SET username = $2
        """, telegram_id, username)
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def get_user(telegram_id):
    con = await get_connection()
    try:
        user = await con.fetchrow("""
            SELECT * FROM users WHERE telegram_id = $1
        """, telegram_id)

        return user
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def add_note(telegram_id, title, content):
    con = await get_connection()
    try:
        await con.execute("""
            INSERT INTO notes (title, content, user_id) SELECT $1, $2, id
            FROM users WHERE telegram_id = $3
        """, title, content, telegram_id)
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def get_notes(telegram_id):
    con = await get_connection()
    try:
        notes = await con.fetch("""
            SELECT notes.id, notes.title, notes.created_at FROM notes
            JOIN users ON notes.user_id = users.id
            WHERE users.telegram_id = $1 ORDER BY notes.id
        """, telegram_id)
        return notes
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def get_note(telegram_id, note_id):
    con = await get_connection()
    try:
        note = await con.fetchrow("""
            SELECT notes.* FROM notes
            JOIN users ON notes.user_id = users.id
            WHERE users.telegram_id = $1
            AND notes.id = $2
        """, telegram_id, note_id)
        return note
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def update_note(telegram_id, note_id, title, content):
    con = await get_connection()
    try:
        result = await con.execute("""
            UPDATE notes SET title = $1, content = $2, updated_at = NOW()
            WHERE id = $3 AND user_id = (SELECT id FROM users WHERE telegram_id = $4 )
        """, title, content, note_id, telegram_id)

        return result
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def delete_note(telegram_id, note_id):
    con = await get_connection()
    try:
        result = await con.execute("""
            DELETE FROM notes WHERE id = $1 AND user_id = (
            SELECT id FROM users WHERE telegram_id = $2
            )
        """, note_id, telegram_id)
        return result
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()

async def delete_user(telegram_id):
    con = await get_connection()
    try:
        await con.execute("""
            DELETE FROM users WHERE telegram_id = $1
        """, telegram_id)
    except Exception as er:
        print("Ошибка: ",et)
    finally:
        await con.close()