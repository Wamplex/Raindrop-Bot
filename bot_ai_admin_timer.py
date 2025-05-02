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
    waiting_for_confirmation = State()

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

# === HANDLERS ===
@router.message(F.text == "/start")
async def start(message: Message):
    is_admin = message.from_user.id == ADMIN_ID
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu(is_admin))

@router.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer("<b>Смотрите отзывы здесь:</b>\nhttps://t.me/raindrop_reviews")

@router.message(F.text == "🛠 Поддержка")
async def support(message: Message, state: FSMContext):
    await message.answer("Напишите ваш вопрос. Администратор скоро ответит вам лично.")
    await state.set_state(SupportState.waiting_for_question)

@router.message(SupportState.waiting_for_question)
async def process_support(message: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"✉️ Новый вопрос от {message.from_user.id}:\n{message.text}")
    await message.answer("Ваш вопрос отправлен администратору.")
    await state.clear()

@router.message(F.text == "👤 Личный кабинет")
async def profile(message: Message):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT orders_count FROM users WHERE user_id = ?", (message.from_user.id,))
    row = cur.fetchone()
    orders = row[0] if row else 0
    await message.answer(f"<b>ID:</b> {message.from_user.id}\n<b>Количество заказов:</b> {orders}")
    conn.close()

@router.message(F.text == "🐠 Товары")
async def products(message: Message):
    await message.answer("Выберите категорию:", reply_markup=category_kb())

@router.message(F.text == "Создать сделку")
async def create_deal(message: Message, state: FSMContext):
    await message.answer("Введите username пользователя, с которым хотите создать сделку")
    await state.set_state(DealState.waiting_for_username)

@router.message(DealState.waiting_for_username)
async def handle_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="continue_deal")]
    ])
    await message.answer(f"Пользователь: <code>{message.text}</code>\nНажмите «Продолжить», чтобы описать сделку.", reply_markup=kb)

@router.callback_query(F.data == "continue_deal")
async def continue_deal(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Опишите вашу сделку.")
    await state.set_state(DealState.waiting_for_description)

@router.message(DealState.waiting_for_description)
async def handle_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    username = data.get("username")
    description = data.get("description")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить сделку", callback_data="confirm_deal")]
    ])
    await message.answer(f"Проверьте данные:\n👤 Пользователь: @{username}\n📄 Описание: {description}", reply_markup=kb)
    await state.set_state(DealState.waiting_for_confirmation)

@router.callback_query(F.data == "confirm_deal")
async def confirm_deal(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    username = data.get("username")
    description = data.get("description")
    await callback.message.edit_text(f"💼 Сделка с @{username}\n📄 Описание: {description}")
    await bot.send_message(ADMIN_ID, f"🆕 Новая сделка:\n👤 С кем: @{username}\n✏️ Описание: {description}\n📨 От: {callback.from_user.id}")
    await state.clear()

@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    category = callback.data.split("_")[1].capitalize()
    await callback.message.edit_text("Выберите товар:", reply_markup=products_kb(category))

@router.callback_query(F.data.startswith("product_"))
async def show_mutations(callback: types.CallbackQuery):
    name = callback.data.split("_", 1)[1]
    await callback.message.edit_text(f"Варианты товара <b>{name}</b>:", reply_markup=mutations_kb(name))

@router.callback_query(F.data.startswith("buy_"))
async def process_purchase(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, mutation, price, quantity FROM products WHERE id = ?", (product_id,))
    prod = cur.fetchone()
    if not prod:
        await callback.answer("Товар не найден", show_alert=True)
        return
    name, mutation, price, quantity = prod
    if quantity <= 0:
        await callback.answer("Товар закончился", show_alert=True)
        return

    cur.execute("UPDATE products SET quantity = quantity - 1 WHERE id = ?", (product_id,))
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (callback.from_user.id,))
    cur.execute("UPDATE users SET orders_count = orders_count + 1 WHERE user_id = ?", (callback.from_user.id,))
    cur.execute("INSERT INTO orders (user_id, product_id, quantity, total_price, created_at) VALUES (?, ?, 1, ?, ?)",
                (callback.from_user.id, product_id, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    await callback.message.answer(f"✅ Вы купили: <b>{name} ({mutation if mutation else 'Без мутации'})</b> за {price}₽")
    await bot.send_message(ADMIN_ID, f"<b>💰 Покупка:</b>\nID: {callback.from_user.id}\nТовар: {name} ({mutation})\nЦена: {price}₽")

@router.callback_query(F.data.startswith("suggest_"))
async def suggest_item(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SuggestState.waiting_for_suggestion)
    await callback.message.edit_text("Напишите, что вы хотите предложить. Администратор получит ваше сообщение.")

@router.message(SuggestState.waiting_for_suggestion)
async def receive_suggestion(message: Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"📦 Предложение товара от {message.from_user.id}:\n{message.text}")
    await message.answer("Спасибо за предложение! Мы рассмотрим его.")
    await state.clear()

# --- ADMIN PANEL ---
@router.message(F.text == "🛡 Админ-панель")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("<b>Админ-панель:</b>\n1. Просмотр товаров\n2. Изменить цену\n3. Изменить кол-во\n4. Удалить товар\n(будет реализовано в полном коде)")

# === MAIN ===
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
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
