import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from connector import create_tables
import function


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()


class AddNote(StatesGroup):
    title = State()
    content = State()

class ViewNote(StatesGroup):
    note_id = State()

class UpdateNote(StatesGroup):
    note_id = State()
    title = State()
    content = State()

class DeleteNote(StatesGroup):
    note_id = State()



@dp.message(Command("start"))
async def start_command(message: Message):
    await function.add_user(
        message.from_user.id,
        message.from_user.username
    )
    await message.answer(
        "Добро пожаловать в бот для заметок!\n\n"
        "Используйте /help для просмотра команд."
    )


@dp.message(Command("help"))
async def help_command(message: Message):

    await message.answer(
        "Доступные команды:\n\n"
        "/start - регистрация\n"
        "/add_note - добавить заметку\n"
        "/view_notes - посмотреть все заметки\n"
        "/view_note_details - посмотреть заметку по ID\n"
        "/update_note - изменить заметку\n"
        "/delete_note - удалить заметку\n"
        "/help - помощь"
    )


@dp.message(Command("add_note"))
async def add_note_command(message: Message, state: FSMContext):
    await message.answer("Введите заголовок заметки:")
    await state.set_state(AddNote.title)


@dp.message(AddNote.title)
async def add_note_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите текст заметки:")
    await state.set_state(AddNote.content)


@dp.message(AddNote.content)
async def add_note_content(message: Message, state: FSMContext):
    data = await state.get_data()
    await function.add_note(
        message.from_user.id,
        data["title"],
        message.text
    )
    await message.answer("Заметка добавлена.")
    await state.clear()


@dp.message(Command("view_notes"))
async def view_notes_command(message: Message):
    notes = await function.get_notes(message.from_user.id)
    if not notes:
        await message.answer("У вас пока нет заметок.")
        return
    text = "Ваши заметки:\n\n"
    for note in notes:
        text += (
            f"ID: {note['id']}\n"
            f"Заголовок: {note['title']}\n"
            f"Дата: {note['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        )
    await message.answer(text)


@dp.message(Command("view_note_details"))
async def view_note_details_command(
    message: Message,
    state: FSMContext
):
    await message.answer("Введите ID заметки:")
    await state.set_state(ViewNote.note_id)


@dp.message(ViewNote.note_id)
async def view_note_details(message: Message, state: FSMContext):
    try:
        note_id = int(message.text)
    except Exception:
        await message.answer("ID должен быть числом.")
        return
    note = await function.get_note(
        message.from_user.id,
        note_id
    )

    if note:
        await message.answer(
            f"ID: {note['id']}\n"
            f"Заголовок: {note['title']}\n"
            f"Текст: {note['content']}\n"
            f"Создана: "f"{note['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
            f"Обновлена: "
            f"{note['updated_at'].strftime('%d.%m.%Y %H:%M')}"
        )

    else:
        await message.answer("Заметка не найдена.")
    await state.clear()


@dp.message(Command("update_note"))
async def update_note_command(
    message: Message,
    state: FSMContext
):
    await message.answer("Введите ID заметки:")
    await state.set_state(UpdateNote.note_id)

@dp.message(UpdateNote.note_id)
async def update_note_id(
    message: Message,
    state: FSMContext
):
    try:
        note_id = int(message.text)
    except Exception:
        await message.answer("ID должен быть числом.")
        return
    note = await function.get_note(
        message.from_user.id,
        note_id
    )
    if not note:
        await message.answer("Заметка не найдена.")
        await state.clear()
        return

    await state.update_data(note_id=note_id)
    await message.answer("Введите новый заголовок:")
    await state.set_state(UpdateNote.title)


@dp.message(UpdateNote.title)
async def update_note_title(
    message: Message,
    state: FSMContext
):
    await state.update_data(title=message.text)
    await message.answer("Введите новый текст заметки:")
    await state.set_state(UpdateNote.content)


@dp.message(UpdateNote.content)
async def update_note_content(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()
    await function.update_note(
        message.from_user.id,
        data["note_id"],
        data["title"],
        message.text
    )
    await message.answer("Заметка обновлена.")
    await state.clear()

@dp.message(Command("delete_note"))
async def delete_note_command(
    message: Message,
    state: FSMContext
):
    await message.answer("Введите ID заметки:")
    await state.set_state(DeleteNote.note_id)


@dp.message(DeleteNote.note_id)
async def delete_note_id(
    message: Message,
    state: FSMContext
):
    try:
        note_id = int(message.text)
    except Exception:
        await message.answer("ID должен быть числом.")
        return
    note = await function.get_note(
        message.from_user.id,
        note_id
    )
    if not note:
        await message.answer("Заметка не найдена.")
        await state.clear()
        return
    await function.delete_note(
        message.from_user.id,
        note_id
    )
    await message.answer("Заметка удалена.")
    await state.clear()

async def main():
    await create_tables()
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())