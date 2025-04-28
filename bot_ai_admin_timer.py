import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm import FSMContext, State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
import aiosqlite

from config import TOKEN, ADMIN_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher(bot)

class OrderState(StatesGroup):
    waiting_for_username = State()
    waiting_for_deal_description = State()

# Функция для работы с базой данных
async def get_item(id, category):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute("SELECT * FROM items WHERE id = ? AND category = ?", (id, category))
        item = await cursor.fetchone()
        return item

# Главная страница
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤝 Создать сделку", "🐠 Товары", "💬 Отзывы", "🛠 Поддержка", "👤 Личный кабинет")
    
    await message.answer("Добро пожаловать! Что вы хотите сделать?", reply_markup=markup)

# Создание сделки
@dp.message_handler(text="🤝 Создать сделку")
async def create_deal(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Введите @юзернейм второго участника сделки:")
        await OrderState.waiting_for_username.set()

@dp.message_handler(state=OrderState.waiting_for_username)
async def deal_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text
    await message.answer("Опишите, что будет за сделка:")
    await OrderState.waiting_for_deal_description.set()

@dp.message_handler(state=OrderState.waiting_for_deal_description)
async def deal_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    
    deal_info = f"Новая сделка:\n\nУчастники:\n{data['username']}\nОписание: {data['description']}"
    await bot.send_message(ADMIN_ID, deal_info, reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("✅ Принять", "❌ Отклонить"))
    await state.finish()

# Обработка кнопок принятия/отклонения сделки
@dp.message_handler(lambda message: message.text in ["✅ Принять", "❌ Отклонить"], user_id=ADMIN_ID)
async def accept_or_reject(message: types.Message):
    if message.text == "✅ Принять":
        await message.answer("Сделка принята. Участникам отправлено уведомление.")
        await bot.send_message(ADMIN_ID, "Сделка подтверждена.")
        # Уведомление пользователю, который предложил сделку
        await bot.send_message(ADMIN_ID, "Сделка подтверждена.")
    elif message.text == "❌ Отклонить":
        await message.answer("Сделка отклонена.")
        # Уведомление пользователю, который предложил сделку
        await bot.send_message(ADMIN_ID, "Сделка отклонена.")

# Товары
@dp.message_handler(text="🐠 Товары")
async def show_products(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎣 Fisch", "🍇 Bloxfruit")
    await message.answer("Выберите категорию товаров", reply_markup=markup)

@dp.message_handler(text="🎣 Fisch")
async def show_fish(message: types.Message):
    # Пример: показываю рыбы
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Nessie", "Northstar Serpent", "Leviathan")
    await message.answer("Выберите рыбу", reply_markup=markup)

@dp.message_handler(lambda message: message.text in ["Nessie", "Northstar Serpent", "Leviathan"])
async def show_fish_mutations(message: types.Message):
    # Пример: показываю мутации
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Обычная", "Sparkling", "Shiny")
    await message.answer("Выберите мутацию", reply_markup=markup)

@dp.message_handler(text="🍇 Bloxfruit")
async def show_fruits(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Leopard", "Gas", "Dough")
    await message.answer("Выберите фрукт", reply_markup=markup)

# Поддержка
@dp.message_handler(text="🛠 Поддержка")
async def support(message: types.Message):
    await message.answer("Напишите ваш вопрос. Администратор скоро ответит вам лично.")

# Личный кабинет
@dp.message_handler(text="👤 Личный кабинет")
async def personal_cabinet(message: types.Message):
    user_id = message.from_user.id
    # Здесь будет логика получения статистики из базы данных по заказам
    await message.answer(f"Ваш ID: {user_id}\nКол-во заказов: 0")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
