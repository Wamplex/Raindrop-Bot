# telegram_shop_bot.py
# Расширенный Telegram-бот с базой данных, фильтрами и заявками на покупку/обмен

import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime

TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
conn = sqlite3.connect("shop.db")
c = conn.cursor()

# === База данных ===
c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price INTEGER,
    available BOOLEAN,
    quantity INTEGER,
    mutations TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    item TEXT,
    action TEXT,
    quantity INTEGER,
    time TEXT
)''')

conn.commit()

# === Главная клавиатура ===
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🐠 Товары")],
        [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🛠 Поддержка")],
        [KeyboardButton(text="👤 Личный кабинет")]
    ],
    resize_keyboard=True
)

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("😊 Привет! Это гарант-бот. Выбери раздел:", reply_markup=main_menu)

# Продолжение: меню "🐠 Товары", фильтры, просмотр товара, заявки, админка и т.д.
# Продолжение будет добавлено в следующих блоках
