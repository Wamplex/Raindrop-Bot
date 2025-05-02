import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# 🔐 ВСТАВЬ СЮДА СВОЙ ТОКЕН
BOT_TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
ADMIN_ID = 7620745738  # Замени на свой ID

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# --- Состояния для FSM
class DealStates(StatesGroup):
    waiting_username = State()
    waiting_description = State()

# --- Главное меню
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Старт
@dp.message(F.text, F.chat.type == "private")
async def start(message: Message):
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu())

# --- Обработка кнопки создания сделки
@dp.callback_query(F.data == "create_deal")
async def create_deal(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите @username второго участника сделки:")
    await state.set_state(DealStates.waiting_username)

@dp.message(DealStates.waiting_username)
async def deal_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Теперь опишите, в чём заключается сделка:")
    await state.set_state(DealStates.waiting_description)

@dp.message(DealStates.waiting_description)
async def deal_description(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    await bot.send_message(
        ADMIN_ID,
        f"🤝 <b>Новая сделка</b> от @{message.from_user.username} ({message.from_user.id})\n\n"
        f"Участник: {data['username']}\nОписание: {message.text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✅ Принять", callback_data="accept_deal"),
             InlineKeyboardButton("❌ Отклонить", callback_data="decline_deal")]
        ])
    )
    await message.answer("Сделка отправлена администратору на рассмотрение.")

# --- Ответ администратора
@dp.callback_query(F.data.in_({"accept_deal", "decline_deal"}))
async def deal_decision(callback: CallbackQuery):
    decision = "принята" if callback.data == "accept_deal" else "отклонена"
    await callback.message.edit_text(callback.message.text + f"\n\n✅ Сделка {decision}.")

# --- Старт бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
