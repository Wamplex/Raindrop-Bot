import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "твой_токен"
ADMIN_ID = 7620745738
REVIEWS_LINK = "https://t.me/raindrop_reviews"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ========== ВРЕМЕННОЕ ХРАНЕНИЕ ==========
products = {
    "Fisch": [
        {"name": "Kraken", "mutations": "Shiny", "quantity": 1, "price": 40},
        {"name": "Leviathan", "mutations": "", "quantity": 2, "price": 30},
    ],
    "Bloxfruit": [
        {"name": "Leopard", "quantity": 1, "price": 155},
        {"name": "Gas", "quantity": 1, "price": 175},
        {"name": "Dough", "quantity": 2, "price": 115},
        {"name": "Venom", "quantity": 1, "price": 50},
    ]
}

deals = []

# ========== СОСТОЯНИЯ ==========
class DealStates(StatesGroup):
    waiting_username = State()
    waiting_description = State()

class OfferStates(StatesGroup):
    waiting_offer = State()

class SupportStates(StatesGroup):
    waiting_question = State()

# ========== КЛАВИАТУРЫ ==========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton("🐠 Товары", callback_data="products")],
        [InlineKeyboardButton("💬 Отзывы", url=REVIEWS_LINK)],
        [InlineKeyboardButton("🛠 Поддержка", callback_data="support")],
        [InlineKeyboardButton("👤 Личный кабинет", callback_data="profile")]
    ])

def category_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🎣 Fisch", callback_data="cat_fisch")],
        [InlineKeyboardButton("🍇 Bloxfruit", callback_data="cat_bloxfruit")]
    ])

# ========== ХЭНДЛЕРЫ ==========
@dp.message(F.text, F.chat.type == "private")
async def start(message: Message):
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu())

@dp.callback_query(F.data == "products")
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=category_menu())

@dp.callback_query(F.data == "cat_fisch")
async def show_fisch(callback: CallbackQuery):
    text = "🎣 Fisch:\n\n"
    for item in products["Fisch"]:
        text += f"<b>{item['name']}</b> — {item['price']}₽ ({item['quantity']} шт)\n"
        if item['mutations']:
            text += f"  🧬 Мутации: {item['mutations']}\n"
    text += "\n➕ <b>Предложить своё</b>: /offer_fisch"
    await callback.message.edit_text(text)

@dp.callback_query(F.data == "cat_bloxfruit")
async def show_bloxfruit(callback: CallbackQuery):
    text = "🍇 Bloxfruit:\n\n"
    for item in products["Bloxfruit"]:
        text += f"<b>{item['name']}</b> — {item['price']}₽ ({item['quantity']} шт)\n"
    text += "\n➕ <b>Предложить своё</b>: /offer_bloxfruit"
    await callback.message.edit_text(text)

@dp.message(F.text == "/offer_fisch")
@dp.message(F.text == "/offer_bloxfruit")
async def offer_command(message: Message, state: FSMContext):
    await message.answer("Опишите товар, который хотите предложить:")
    await state.set_state(OfferStates.waiting_offer)

@dp.message(OfferStates.waiting_offer)
async def receive_offer(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(
        ADMIN_ID,
        f"➕ <b>Новое предложение</b> от @{message.from_user.username} ({message.from_user.id}):\n{message.text}"
    )
    await message.answer("Ваше предложение отправлено админу.")

@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите ваш вопрос:")
    await state.set_state(SupportStates.waiting_question)

@dp.message(SupportStates.waiting_question)
async def support_question(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(ADMIN_ID, f"🛠 Поддержка от @{message.from_user.username} ({message.from_user.id}):\n{message.text}")
    await message.answer("Ваш вопрос отправлен.")

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    await callback.message.answer(f"👤 Ваш ID: <code>{callback.from_user.id}</code>")

@dp.callback_query(F.data == "create_deal")
async def start_deal(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите @username второго участника сделки:")
    await state.set_state(DealStates.waiting_username)

@dp.message(DealStates.waiting_username)
async def deal_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Теперь опишите сделку:")
    await state.set_state(DealStates.waiting_description)

@dp.message(DealStates.waiting_description)
async def deal_description(message: Message, state: FSMContext):
    data = await state.get_data()
    deals.append({
        "from": message.from_user.username,
        "to": data['username'],
        "description": message.text
    })
    await state.clear()
    await bot.send_message(
        ADMIN_ID,
        f"🤝 <b>Новая сделка</b>\nОт: @{message.from_user.username}\nС: {data['username']}\nОписание: {message.text}"
    )
    await message.answer("Сделка отправлена на рассмотрение админу.")

# ========== СТАРТ ==========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
