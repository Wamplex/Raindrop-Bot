import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import os

# Вставьте сюда ваш токен
TOKEN = '7807213915:AAEkplZ9d3AXmbX6U11R2GoFPHPhLnspaus'
ADMIN_ID = 'ВАШ_ID'  # Замените на свой ID
admins = [ADMIN_ID]

logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("👤 Личный кабинет"))
keyboard.add(KeyboardButton("🤝 Создать сделку"))
keyboard.add(KeyboardButton("🎁 Получить приз"))

# Хэндлер для команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id in admins:
        admin_button = KeyboardButton("🛠 Админ панель")
        keyboard.add(admin_button)
    
    await message.answer("Добро пожаловать в бота! Выберите одну из опций:", reply_markup=keyboard)

# Хэндлер для кнопки "Личный кабинет"
@dp.message_handler(lambda message: message.text == "👤 Личный кабинет")
async def personal_account(message: types.Message):
    user_id = message.from_user.id
    # Логика личного кабинета
    await message.answer("Это ваш личный кабинет.\n\nЗдесь вы можете управлять своими сделками.")

# Хэндлер для кнопки "Создать сделку"
@dp.message_handler(lambda message: message.text == "🤝 Создать сделку")
async def create_deal(message: types.Message):
    # Запрос на создание сделки
    await message.answer("Опишите вашу сделку. Пожалуйста, предоставьте все детали.")

# Хэндлер для кнопки "Получить приз"
@dp.message_handler(lambda message: message.text == "🎁 Получить приз")
async def get_prize(message: types.Message):
    # Перенаправление по ссылке
    prize_link = "https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO"
    await message.answer(f"Вы можете забрать приз, перейдя по этой ссылке: {prize_link}")
    
    # Уведомление администратору
    for admin in admins:
        await bot.send_message(admin, f"Пользователь {message.from_user.username} запрашивает приз!")

# Хэндлер для кнопки "Админ панель" (доступна только администратору)
@dp.message_handler(lambda message: message.text == "🛠 Админ панель", user_id=admins)
async def admin_panel(message: types.Message):
    # Логика админ панели
    await message.answer("Это ваша админ панель.\n\nЗдесь вы можете управлять ботом и пользователями.")

# Хэндлер для администрирования пользователей (удаление, добавление админов и т.д.)
@dp.message_handler(commands=['add_admin'], user_id=admins)
async def add_admin(message: types.Message):
    # Добавление нового администратора
    new_admin_id = message.text.split(' ')[1]
    if new_admin_id.isdigit():
        admins.append(new_admin_id)
        await message.answer(f"Пользователь {new_admin_id} теперь является администратором!")
    else:
        await message.answer("Неверный ID пользователя.")

@dp.message_handler(commands=['remove_admin'], user_id=admins)
async def remove_admin(message: types.Message):
    # Удаление администратора
    admin_id_to_remove = message.text.split(' ')[1]
    if admin_id_to_remove in admins:
        admins.remove(admin_id_to_remove)
        await message.answer(f"Пользователь {admin_id_to_remove} больше не является администратором.")
    else:
        await message.answer("Этот пользователь не является администратором.")

@dp.message_handler(commands=['list_admins'], user_id=admins)
async def list_admins(message: types.Message):
    # Список администраторов
    admin_list = "\n".join(admins)
    await message.answer(f"Список администраторов:\n{admin_list}")

# Хэндлер для добавления нового пользователя
@dp.message_handler(commands=['add_user'], user_id=admins)
async def add_user(message: types.Message):
    # Добавление пользователя в базу данных или список
    new_user_id = message.text.split(' ')[1]
    if new_user_id.isdigit():
        # Логика добавления пользователя
        await message.answer(f"Пользователь {new_user_id} добавлен!")
    else:
        await message.answer("Неверный ID пользователя.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
