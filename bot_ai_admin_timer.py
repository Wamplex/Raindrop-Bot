import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ----------------------------
# Настройки
TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738  # ТВОЙ ID
DB_FILE = "shop.db"
# ----------------------------

# Включение логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Соединение с БД
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Создание таблиц, если их нет
c.execute('''CREATE TABLE IF NOT EXISTS products
             (id INTEGER PRIMARY KEY, name TEXT, category TEXT, mutation TEXT, price INTEGER, quantity INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders
             (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, item_name TEXT, action TEXT, status TEXT)''')
conn.commit()

# --- Кнопки ---
main_menu = InlineKeyboardMarkup(row_width=2)
main_menu.add(
    InlineKeyboardButton("\U0001F6D2 Товары", callback_data="products"),
    InlineKeyboardButton("\uD83D\uDCAC Отзывы", url="https://t.me/raindrop_reviews"),
    InlineKeyboardButton("\u2699\uFE0F Поддержка", callback_data="support"),
    InlineKeyboardButton("\U0001F464 Личный кабинет", callback_data="profile")
)

products_menu = InlineKeyboardMarkup(row_width=2)
products_menu.add(
    InlineKeyboardButton("\uD83C\uDF3F Fisch", callback_data="category_fish"),
    InlineKeyboardButton("\ud83c\udf47 BloxFruit", callback_data="category_bloxfruit")
)

admin_panel = InlineKeyboardMarkup(row_width=1)
admin_panel.add(
    InlineKeyboardButton("\uD83D\uDDC2 Просмотреть товары", callback_data="admin_products"),
    InlineKeyboardButton("\uD83D\uDCC4 История заказов", callback_data="admin_orders")
)

# --- Хендлеры ---

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("\uD83D\uDC4B Добро пожаловать!", reply_markup=main_menu)

@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("\ud83d\udd10 Админ-панель открыта.", reply_markup=admin_panel)
    else:
        await message.answer("\u274C У вас нет прав.")

@dp.callback_query_handler(text="products")
async def show_products(call: types.CallbackQuery):
    await call.message.edit_text("\uD83D\uDED2 Выберите категорию:", reply_markup=products_menu)

@dp.callback_query_handler(text="support")
async def support(call: types.CallbackQuery):
    await call.message.answer("\uD83D\uDCAC Напишите ваш вопрос. Администратор ответит вам лично.")

@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    user_id = call.from_user.id
    username = call.from_user.username
    c.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,))
    total_orders = c.fetchone()[0]
    await call.message.answer(f"\uD83E\uDDD1\u200D\uD83D\uDCBB Личный кабинет:\nID: {user_id}\nUsername: @{username}\nЗаказов: {total_orders}")

# --- Категории ---

@dp.callback_query_handler(text="category_fish")
async def show_fish(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    c.execute("SELECT DISTINCT name FROM products WHERE category=?", ("fish",))
    fish_list = c.fetchall()
    for fish in fish_list:
        markup.add(InlineKeyboardButton(fish[0], callback_data=f"fish_{fish[0]}"))
    markup.add(InlineKeyboardButton("\uD83D\uDCC8 Предложить своё", callback_data="propose_fish"))
    await call.message.edit_text("\uD83C\uDF0A Выберите рыбу:", reply_markup=markup)

@dp.callback_query_handler(text="category_bloxfruit")
async def show_bloxfruit(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    c.execute("SELECT DISTINCT name FROM products WHERE category=?", ("bloxfruit",))
    fruit_list = c.fetchall()
    for fruit in fruit_list:
        markup.add(InlineKeyboardButton(fruit[0], callback_data=f"fruit_{fruit[0]}"))
    markup.add(InlineKeyboardButton("\uD83D\uDCC8 Предложить своё", callback_data="propose_fruit"))
    await call.message.edit_text("\uD83C\uDF47 Выберите фрукт:", reply_markup=markup)

# --- Покупка ---

@dp.callback_query_handler(lambda call: call.data.startswith("fish_"))
async def fish_info(call: types.CallbackQuery):
    fish_name = call.data.split("_")[1]
    c.execute("SELECT mutation, price, quantity FROM products WHERE name=?", (fish_name,))
    fishes = c.fetchall()
    text = f"\uD83C\uDF0A {fish_name}:\n\n"
    for fish in fishes:
        mutation, price, qty = fish
        text += f"- {mutation}: {price}₽ ({qty} шт)\n"
    await call.message.edit_text(text)

@dp.callback_query_handler(lambda call: call.data.startswith("fruit_"))
async def fruit_info(call: types.CallbackQuery):
    fruit_name = call.data.split("_")[1]
    c.execute("SELECT mutation, price, quantity FROM products WHERE name=?", (fruit_name,))
    fruits = c.fetchall()
    text = f"\uD83C\uDF47 {fruit_name}:\n\n"
    for fruit in fruits:
        mutation, price, qty = fruit
        text += f"- {mutation}: {price}₽ ({qty} шт)\n"
    await call.message.edit_text(text)

# --- Сделка ---

@dp.callback_query_handler(text_startswith="propose")
async def propose(call: types.CallbackQuery):
    await call.message.answer("\u2709\uFE0F Отправьте сообщение с вашим товаром и желаемым обменом.")

# --- Админ панель ---

@dp.callback_query_handler(text="admin_products")
async def admin_products(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    c.execute("SELECT id, name, category, mutation, price, quantity FROM products")
    products = c.fetchall()
    text = "\uD83D\uDDC2 Все товары:\n\n"
    for p in products:
        text += f"{p[0]}. {p[1]} ({p[2]} - {p[3]}): {p[4]}₽ ({p[5]} шт)\n"
    await call.message.edit_text(text)

@dp.callback_query_handler(text="admin_orders")
async def admin_orders(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    c.execute("SELECT id, user_id, username, item_name, action, status FROM orders")
    orders = c.fetchall()
    text = "\uD83D\uDCC4 История заказов:\n\n"
    for o in orders:
        text += f"{o[0]}. {o[2]} ({o[1]}): {o[3]} [{o[4]}] - {o[5]}\n"
    await call.message.edit_text(text)

# --- Запуск ---

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

