import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
from datetime import datetime

# === CONFIG ===
TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
ADMIN_ID = 7620745738

# === FSM ===
class SupportState(StatesGroup):
    waiting_for_question = State()

class SuggestState(StatesGroup):
    waiting_for_suggestion = State()

class DealState(StatesGroup):
    waiting_for_username = State()
    waiting_for_description = State()

class AdminState(StatesGroup):
    waiting_for_add_category = State()
    waiting_for_add_name = State()
    waiting_for_add_mutation = State()
    waiting_for_add_price = State()
    waiting_for_add_quantity = State()
    waiting_for_edit_price_id = State()
    waiting_for_edit_price_value = State()
    waiting_for_edit_quantity_id = State()
    waiting_for_edit_quantity_value = State()
    waiting_for_delete_id = State()

# === DATABASE ===
def get_db():
    return sqlite3.connect("shop.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        orders_count INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        mutation TEXT,
        price INTEGER NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
    add_test_product()

def add_test_product():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute("INSERT INTO products (category, name, mutation, price, quantity) VALUES (?, ?, ?, ?, ?)",
                    ("Fisch", "Test Fisch", "Скорость", 100, 10))
        cur.execute("INSERT INTO products (category, name, mutation, price, quantity) VALUES (?, ?, ?, ?, ?)",
                    ("Bloxfruit", "Test Blox", None, 200, 5))
        conn.commit()
    conn.close()

# === KEYBOARDS ===
def main_menu(is_admin=False):
    kb = [[
        KeyboardButton(text="Создать сделку")
    ], [
        KeyboardButton(text="🐠 Товары"),
        KeyboardButton(text="💬 Отзывы")
    ], [
        KeyboardButton(text="🛠 Поддержка"),
        KeyboardButton(text="👤 Личный кабинет")
    ]]
    if is_admin:
        kb.append([KeyboardButton(text="🛡 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def category_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍣 Fisch", callback_data="category_fisch")],
        [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="category_blox")]
    ])
    return kb

def products_kb(category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM products WHERE category = ?", (category,))
    items = cursor.fetchall()
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=item[0], callback_data=f"product_{item[0]}")
    kb.button(text="➕ Предложить своё", callback_data=f"suggest_{category}")
    return kb.adjust(1).as_markup()

def mutations_kb(name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, mutation, price, quantity FROM products WHERE name = ?", (name,))
    items = cursor.fetchall()
    kb = InlineKeyboardBuilder()
    for item in items:
        m = item[1] if item[1] else "Без мутации"
        text = f"{m} - {item[2]}₽ (x{item[3]})"
        kb.button(text=text, callback_data=f"buy_{item[0]}")
    return kb.adjust(1).as_markup()

# === BOT SETUP ===
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

# (остальные обработчики без изменений до админ-панели)

@router.message(F.text == "🛡 Админ-панель")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Добавить товар", callback_data="admin_add")],
        [InlineKeyboardButton(text="💲 Изменить цену", callback_data="admin_price")],
        [InlineKeyboardButton(text="📦 Изменить кол-во", callback_data="admin_quantity")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data="admin_delete")],
        [InlineKeyboardButton(text="📋 Все товары", callback_data="admin_all")]
    ])
    await message.answer("<b>Админ-панель:</b>", reply_markup=kb)

# === MAIN ===
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
