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

# === KEYBOARDS ===
def main_menu(is_admin=False):
    kb = [[
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

@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
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

# --- ADMIN PANEL ---
@router.message(F.text == "🛡 Админ-панель")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Просмотр товаров", callback_data="admin_view_products")],
        [InlineKeyboardButton(text="Изменить цену товара", callback_data="admin_edit_price")],
        [InlineKeyboardButton(text="Изменить количество товара", callback_data="admin_edit_quantity")],
        [InlineKeyboardButton(text="Удалить товар", callback_data="admin_delete_product")],
    ])
    await message.answer("<b>Админ-панель:</b>\n1. Просмотр товаров\n2. Изменить цену\n3. Изменить кол-во\n4. Удалить товар", reply_markup=kb)

@router.callback_query(F.data == "admin_view_products")
async def admin_view_products(callback: types.CallbackQuery):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, name, mutation, price, quantity FROM products")
    products = cursor.fetchall()
    response = "<b>Все товары:</b>\n"
    for prod in products:
        response += f"ID: {prod[0]} | Категория: {prod[1]} | Товар: {prod[2]} | Мутация: {prod[3] if prod[3] else 'Нет'} | Цена: {prod[4]}₽ | Кол-во: {prod[5]}\n"
    await callback.message.edit_text(response)
    conn.close()

# === MAIN ===
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


