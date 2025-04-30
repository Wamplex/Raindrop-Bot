
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# 🔐 ВСТАВЬ СЮДА ТВОЙ ТОКЕН В КАВЫЧКАХ:
BOT_TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
ADMIN_ID = 7620745738  # Замени на свой Telegram ID
REVIEWS_LINK = "https://t.me/raindrop_reviews"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ===================== STATES =====================
class DealStates(StatesGroup):
    waiting_username = State()
    waiting_description = State()

class OfferStates(StatesGroup):
    waiting_offer = State()

class SupportStates(StatesGroup):
    waiting_question = State()

# ===================== FAKE DATA =====================
users = {}
orders = {}
products = [
    {"category": "Fisch", "name": "Shark", "mutations": "Toxic, Lightning", "quantity": 3, "price": 100},
    {"category": "Fisch", "name": "Salmon", "mutations": "None", "quantity": 10, "price": 50},
    {"category": "Bloxfruit", "name": "Dragon", "quantity": 2, "price": 200},
    {"category": "Bloxfruit", "name": "Leopard", "quantity": 5, "price": 150},
]
deals = []

# ===================== KEYBOARDS =====================
def main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="🐠 Товары", callback_data="products")],
        [InlineKeyboardButton(text="💬 Отзывы", url=REVIEWS_LINK)],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")]
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="🛡 Админ-панель", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def category_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Fisch", callback_data="cat_fisch")],
        [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="cat_bloxfruit")]
    ])

# ===================== HANDLERS =====================
@dp.message(F.text, F.chat.type == "private")
async def start_handler(message: Message):
    is_admin = message.from_user.id == ADMIN_ID
    users[message.from_user.id] = users.get(message.from_user.id, {"orders": 0})
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu(is_admin))

@dp.callback_query(F.data == "products")
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=category_menu())

@dp.callback_query(F.data == "cat_fisch")
async def show_fisch(callback: CallbackQuery):
    text = "🎣 Fisch:

"
    for product in products:
        if product["category"] == "Fisch":
            text += f"<b>{product['name']}</b> — {product['price']}₽ ({product['quantity']} шт)
"
            if "mutations" in product:
                text += f"  🧬 Мутации: {product['mutations']}
"
    text += "
➕ <b>Предложить своё</b>: /offer_fisch"
    await callback.message.edit_text(text)

@dp.callback_query(F.data == "cat_bloxfruit")
async def show_bloxfruit(callback: CallbackQuery):
    text = "🍇 Bloxfruit:

"
    for product in products:
        if product["category"] == "Bloxfruit":
            text += f"<b>{product['name']}</b> — {product['price']}₽ ({product['quantity']} шт)
"
    text += "
➕ <b>Предложить своё</b>: /offer_bloxfruit"
    await callback.message.edit_text(text)

@dp.message(F.text == "/offer_fisch")
@dp.message(F.text == "/offer_bloxfruit")
async def offer_product(message: Message, state: FSMContext):
    await message.answer("Опишите товар, который хотите предложить:")
    await state.set_state(OfferStates.waiting_offer)

@dp.message(OfferStates.waiting_offer)
async def receive_offer(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(
        ADMIN_ID,
        f"➕ <b>Новое предложение товара</b> от @{message.from_user.username} ({message.from_user.id}):

{message.text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✅ Принять", callback_data="accept_offer"),
             InlineKeyboardButton("❌ Отклонить", callback_data="decline_offer")]
        ])
    )
    await message.answer("Ваше предложение отправлено администратору.")

@dp.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите ваш вопрос. Администратор ответит вам лично.")
    await state.set_state(SupportStates.waiting_question)

@dp.message(SupportStates.waiting_question)
async def receive_support(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(ADMIN_ID, f"🛠 <b>Вопрос в поддержку</b> от @{message.from_user.username} ({message.from_user.id}):

{message.text}")
    await message.answer("Ваш вопрос отправлен.")

@dp.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders_count = users.get(user_id, {}).get("orders", 0)
    await callback.message.answer(f"👤 Ваш ID: {user_id}
🛍 Количество заказов: {orders_count}")

@dp.callback_query(F.data == "create_deal")
async def start_deal(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите @username второго участника сделки:")
    await state.set_state(DealStates.waiting_username)

@dp.message(DealStates.waiting_username)
async def input_deal_user(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Теперь опишите, в чём заключается сделка:")
    await state.set_state(DealStates.waiting_description)

@dp.message(DealStates.waiting_description)
async def input_deal_description(message: Message, state: FSMContext):
    data = await state.get_data()
    deals.append({
        "user1": message.from_user.id,
        "user2": data["username"],
        "description": message.text,
        "status": "pending"
    })
    await state.clear()
    await bot.send_message(
        ADMIN_ID,
        f"🤝 <b>Новая сделка</b> от @{message.from_user.username} ({message.from_user.id})

"
        f"Участник: {data['username']}
Описание: {message.text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✅ Принять", callback_data="accept_deal"),
             InlineKeyboardButton("❌ Отклонить", callback_data="decline_deal")]
        ])
    )
    await message.answer("Сделка отправлена администратору на рассмотрение.")

@dp.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    await callback.message.answer("🛡 Админ-панель

(функции модерации будут добавлены позже)")

# ===================== START =====================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
