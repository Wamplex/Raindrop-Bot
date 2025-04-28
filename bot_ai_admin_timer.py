import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = "7807213915:AAGtoLBhhKihds0Y-YGwfBFZiCAZvx-P76Y"
ADMIN_ID = 7620745738

bot = Bot(TOKEN)
dp = Dispatcher()

# Создание базы данных
conn = sqlite3.connect('shop.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    name TEXT,
    price INTEGER,
    quantity INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    orders INTEGER DEFAULT 0
)
''')

conn.commit()

# Клавиатуры
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🎯 Создать сделку")],
    [KeyboardButton(text="🐠 Товары")],
    [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🛠 Поддержка")],
    [KeyboardButton(text="👤 Личный кабинет")]
], resize_keyboard=True)

admin_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить товар"), KeyboardButton(text="📦 Все товары")],
    [KeyboardButton(text="✏ Изменить товар"), KeyboardButton(text="❌ Удалить товар")],
    [KeyboardButton(text="⬅️ Назад")]
], resize_keyboard=True)

support_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Назад")]
], resize_keyboard=True)

# Состояния FSM
class Deal(StatesGroup):
    waiting_username = State()
    waiting_description = State()

class Suggest(StatesGroup):
    waiting_text = State()

class EditProduct(StatesGroup):
    waiting_id = State()
    waiting_new_price = State()
    waiting_new_quantity = State()

# Команды
@dp.message(CommandStart())
async def start(message: types.Message):
    kb = main_kb
    if message.from_user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup(
            keyboard=main_kb.keyboard + [[KeyboardButton(text="🛡 Админ-панель")]],
            resize_keyboard=True
        )
    await message.answer("Добро пожаловать в магазин!", reply_markup=kb)

@dp.message(F.text == "🎯 Создать сделку")
async def create_deal(message: types.Message, state: FSMContext):
    await message.answer("Отправьте @юзернейм второго участника сделки:")
    await state.set_state(Deal.waiting_username)

@dp.message(Deal.waiting_username)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Теперь опишите суть сделки:")
    await state.set_state(Deal.waiting_description)

@dp.message(Deal.waiting_description)
async def get_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data["username"]
    description = message.text
    await bot.send_message(ADMIN_ID, f"Запрос на сделку:\nУчастник 1: @{message.from_user.username}\nУчастник 2: {username}\nОписание: {description}", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_deal_{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_deal_{message.from_user.id}")
            ]
        ]
    ))
    await message.answer("Запрос на сделку отправлен админу!")
    await state.clear()

@dp.callback_query(F.data.startswith("accept_deal_"))
async def accept_deal(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await bot.send_message(user_id, "✅ Ваша сделка одобрена администратором!")
    await callback.message.edit_text("Сделка принята.")

@dp.callback_query(F.data.startswith("decline_deal_"))
async def decline_deal(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await bot.send_message(user_id, "❌ Ваша сделка отклонена администратором.")
    await callback.message.edit_text("Сделка отклонена.")

@dp.message(F.text == "🐠 Товары")
async def show_categories(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Fisch", callback_data="category_fisch")],
        [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="category_bloxfruit")]
    ])
    await message.answer("Выберите категорию:", reply_markup=kb)

@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    cursor.execute("SELECT id, name, price, quantity FROM products WHERE category = ?", (category,))
    items = cursor.fetchall()
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=f"{item[1]} ({item[3]} шт)", callback_data=f"buy_{item[0]}")
    kb.button(text="➕ Предложить своё", callback_data=f"suggest_{category}")
    await callback.message.answer(f"Товары в категории {category}:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    cursor.execute("SELECT name, price, quantity FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if product and product[2] > 0:
        cursor.execute("UPDATE products SET quantity = quantity - 1 WHERE id = ?", (product_id,))
        conn.commit()
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (callback.from_user.id,))
        cursor.execute("UPDATE users SET orders = orders + 1 WHERE id = ?", (callback.from_user.id,))
        conn.commit()
        await bot.send_message(ADMIN_ID, f"Покупка!\nПользователь @{callback.from_user.username} купил {product[0]} за {product[1]}₽.")
        await callback.message.answer(f"Вы успешно купили {product[0]} за {product[1]}₽!")
    else:
        await callback.message.answer("Товара нет в наличии.")

@dp.callback_query(F.data.startswith("suggest_"))
async def suggest_item(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Опишите ваш товар и цену:")
    await state.set_state(Suggest.waiting_text)

@dp.message(Suggest.waiting_text)
async def get_suggestion(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"Новое предложение от @{message.from_user.username}:\n{message.text}", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data="accept_suggest"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data="decline_suggest")
            ]
        ]
    ))
    await message.answer("Ваше предложение отправлено администратору!")
    await state.clear()

@dp.message(F.text == "💬 Отзывы")
async def reviews(message: types.Message):
    await message.answer("Отзывы можно посмотреть здесь: @raindrop_reviews")

@dp.message(F.text == "🛠 Поддержка")
async def support(message: types.Message):
    await message.answer("Напишите ваш вопрос. Администратор ответит вам лично.", reply_markup=support_kb)

@dp.message(F.text == "👤 Личный кабинет")
async def profile(message: types.Message):
    cursor.execute("SELECT orders FROM users WHERE id = ?", (message.from_user.id,))
    orders = cursor.fetchone()
    orders = orders[0] if orders else 0
    await message.answer(f"Ваш ID: {message.from_user.id}\nКоличество заказов: {orders}")

@dp.message(F.text == "🛡 Админ-панель")
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Вы в админ-панели.", reply_markup=admin_kb)
    else:
        await message.answer("У вас нет доступа.")

# Админка действия
@dp.message(F.text == "📦 Все товары")
async def list_products(message: types.Message):
    cursor.execute("SELECT id, category, name, price, quantity FROM products")
    products = cursor.fetchall()
    text = "\n".join([f"ID {p[0]} | {p[1]} | {p[2]} | {p[3]}₽ | {p[4]} шт" for p in products])
    await message.answer(text or "Нет товаров.")

@dp.message(F.text == "✏ Изменить товар")
async def edit_product_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ID товара для изменения:")
    await state.set_state(EditProduct.waiting_id)

@dp.message(EditProduct.waiting_id)
async def edit_product_id(message: types.Message, state: FSMContext):
    await state.update_data(id=message.text)
    await message.answer("Введите новую цену:")
    await state.set_state(EditProduct.waiting_new_price)

@dp.message(EditProduct.waiting_new_price)
async def edit_product_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Введите новое количество:")
    await state.set_state(EditProduct.waiting_new_quantity)

@dp.message(EditProduct.waiting_new_quantity)
async def edit_product_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("UPDATE products SET price = ?, quantity = ? WHERE id = ?", (data["price"], message.text, data["id"]))
    conn.commit()
    await message.answer("Товар успешно обновлён.")
    await state.clear()

@dp.message(F.text == "❌ Удалить товар")
async def delete_product(message: types.Message):
    await message.answer("Отправьте ID товара для удаления:")

@dp.message(F.text.regexp(r"^\d+$"))
async def delete_product_by_id(message: types.Message):
    cursor.execute("DELETE FROM products WHERE id = ?", (message.text,))
    conn.commit()
    await message.answer("Товар удалён.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
