import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold
from datetime import datetime, timedelta

API_TOKEN = "7807213915:AAGGA7EDq-e_8uUnpKfg4ZhUe-KfJfXKvUY"
ADMIN_ID = 5809260847  # Замени на свой Telegram ID

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Состояния
class Deal(StatesGroup):
    waiting_for_username = State()
    waiting_for_description = State()

# Главное меню
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="📩 Поддержка", callback_data="support")]
    ])

# Команда /start
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(f"Привет, {hbold(message.from_user.first_name)}!\nВыбери действие:", reply_markup=main_keyboard())

# Нажатие на кнопку "Создать сделку"
@dp.callback_query(F.data == "create_deal")
async def deal_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите username участника сделки:")
    await state.set_state(Deal.waiting_for_username)
    await state.update_data(start_time=datetime.now())
    await callback.answer()

# Получение username
@dp.message(Deal.waiting_for_username)
async def deal_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Опишите вашу сделку:")
    await state.set_state(Deal.waiting_for_description)

# Получение описания сделки
@dp.message(Deal.waiting_for_description)
async def deal_description(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data["username"]
    description = message.text

    text = f"💼 Новая сделка:\n👤 С кем: @{username}\n📝 Описание: {description}"

    await message.answer("Сделка отправлена на проверку.")
    await bot.send_message(ADMIN_ID, text)
    await state.clear()

# Поддержка
@dp.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    await callback.message.edit_text("Напишите сюда ваш вопрос, и админ вам ответит.")
    await bot.send_message(ADMIN_ID, f"📩 Пользователь @{callback.from_user.username or callback.from_user.id} открыл поддержку.")
    await callback.answer()

# Автоотмена сделки через 1 час
@dp.message()
async def check_timeout(message: Message, state: FSMContext):
    data = await state.get_data()
    start_time = data.get("start_time")
    if start_time and datetime.now() - start_time > timedelta(hours=1):
        await message.answer("⏰ Сделка отменена из-за бездействия.")
        await state.clear()

# Обработка ошибок (на всякий случай)
@dp.errors()
async def handle_errors(event, exception):
    return True  # подавляем все ошибки

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
