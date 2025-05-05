import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ChatPermissions

import os
import asyncio

# Ваш токен
TOKEN = '7807213915:AAEkplZ9d3AXmbX6U11R2GoFPHPhLnspaus'

# Настроим логирование
logging.basicConfig(level=logging.INFO)

# Создаём экземпляры бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Список администраторов (сюда можно добавлять ID пользователей)
admins = [123456789, 987654321]  # Замените на ID администраторов

# Функция для проверки является ли пользователь администратором
def is_admin(user_id: int):
    return user_id in admins

# Главная клавиатура
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👤 Личный кабинет"))
    keyboard.add(KeyboardButton("🤝 Создать сделку"))
    keyboard.add(KeyboardButton("🎁 Получить приз"))
    return keyboard

# Кнопка "Получить приз"
def prize_button():
    return [KeyboardButton("Получить приз")]

# Обработчик старта
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.from_user.id in admins:
        keyboard = main_menu()
        keyboard.add(KeyboardButton("🔧 Админ панель"))
    else:
        keyboard = main_menu()
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)

# Обработчик личного кабинета
@dp.message_handler(lambda message: message.text == "👤 Личный кабинет")
async def personal_account(message: types.Message):
    await message.answer("Это ваш личный кабинет.", reply_markup=main_menu())

# Обработчик кнопки "Создать сделку"
@dp.message_handler(lambda message: message.text == "🤝 Создать сделку")
async def create_deal(message: types.Message):
    await message.answer("Опишите вашу сделку:", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отмена")))
    # Обрабатываем описание сделки (состояние можно использовать для дальнейшей логики)

# Обработчик получения приза
@dp.message_handler(lambda message: message.text == "🎁 Получить приз")
async def get_prize(message: types.Message):
    await message.answer("Вы перенаправлены по ссылке: https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO")
    await message.answer("Свяжитесь с администратором, чтобы забрать приз — @RaindropSpam_bot", reply_markup=main_menu())

# Обработчик кнопки админ-панели
@dp.message_handler(lambda message: message.text == "🔧 Админ панель" and is_admin(message.from_user.id))
async def admin_panel(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📦 Просмотр сделок"))
    keyboard.add(KeyboardButton("🚫 Заблокировать пользователя"))
    keyboard.add(KeyboardButton("🔙 Назад"))
    await message.answer("Добро пожаловать в админ панель", reply_markup=keyboard)

# Просмотр сделок в админ панели
@dp.message_handler(lambda message: message.text == "📦 Просмотр сделок" and is_admin(message.from_user.id))
async def view_deals(message: types.Message):
    # Здесь будет логика отображения всех сделок (например, список сделок)
    await message.answer("Список сделок...", reply_markup=admin_panel_keyboard())

# Назначение администраторов
@dp.message_handler(lambda message: message.text == "🔧 Назначить админа" and is_admin(message.from_user.id))
async def add_admin(message: types.Message):
    await message.answer("Введите ID пользователя для назначения администратором.")

@dp.message_handler(lambda message: message.text.isdigit() and is_admin(message.from_user.id))
async def assign_admin(message: types.Message):
    user_id = int(message.text)
    if user_id not in admins:
        admins.append(user_id)
        await message.answer(f"Пользователь с ID {user_id} теперь администратор.")
    else:
        await message.answer("Этот пользователь уже является администратором.")

# Назад в меню админа
@dp.message_handler(lambda message: message.text == "🔙 Назад" and is_admin(message.from_user.id))
async def back_to_admin_menu(message: types.Message):
    await message.answer("Вы вернулись в админ панель", reply_markup=admin_panel_keyboard())

# Обработчик отмены
@dp.message_handler(lambda message: message.text == "Отмена")
async def cancel(message: types.Message):
    await message.answer("Операция отменена.", reply_markup=main_menu())

# Функция для получения клавиатуры админ-панели
def admin_panel_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📦 Просмотр сделок"))
    keyboard.add(KeyboardButton("🚫 Заблокировать пользователя"))
    keyboard.add(KeyboardButton("🔙 Назад"))
    return keyboard

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
