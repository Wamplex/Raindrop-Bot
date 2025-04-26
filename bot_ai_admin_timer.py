import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import logging

# -----------------------------
# Настройки
TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwF8FZiCAZvx-P76Y"
ADMIN_ID = 7620745738
DB_FILE = "shop.db"
# -----------------------------

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# -----------------------------
# Инициализация базы данных

def create_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        category TEXT,
                        price INTEGER,
                        stock INTEGER,
                        mutation TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        username TEXT,
                        product TEXT,
                        action TEXT,
                        date TEXT)''')
    conn.commit()
    conn.close()

create_db()

# -----------------------------
# Кнопки

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("\ud83d\udc64 \u041b\u0438\u0447\u043d\u044b\u0439 \u043a\u0430\u0431\u0438\u043d\u0435\u0442", callback_data="profile"))
    kb.add(InlineKeyboardButton("\ud83d\udc20 \u0422\u043e\u0432\u0430\u0440\u044b", callback_data="products"))
    kb.add(InlineKeyboardButton("\ud83d\udd8a\ufe0f \u041e\u0442\u0437\u044b\u0432\u044b", url="https://t.me/raindrop_reviews"))
    kb.add(InlineKeyboardButton("\ud83d\udd27 \u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430", callback_data="support"))
    return kb

# -----------------------------
# Старт

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c! \ud83d\ude80", reply_markup=main_menu())

# -----------------------------
# Хэндлеры меню

@dp.callback_query_handler(lambda c: c.data == 'products')
async def products_menu(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("\ud83c\udf3f Fisch", callback_data="category_Fisch"))
    kb.add(InlineKeyboardButton("\ud83c\udf47 Bloxfruit", callback_data="category_Bloxfruit"))
    await call.message.edit_text("\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044e:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'profile')
async def profile(call: types.CallbackQuery):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (call.from_user.id,))
    count = cursor.fetchone()[0]
    conn.close()
    await call.message.edit_text(f"\ud83d\udc64 Ваш ID: <code>{call.from_user.id}</code>\n\ud83d\udd22 Заказов: {count}", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'support')
async def support(call: types.CallbackQuery):
    await call.message.edit_text("\ud83d\udcac Напишите свой вопрос. Администратор скоро свяжется с вами.", reply_markup=main_menu())

# -----------------------------
# Админ-панель

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("\ud83d\udd10 Админ-панель открыта. Здесь будут админ-функции.", reply_markup=main_menu())

# -----------------------------
# Запуск

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
