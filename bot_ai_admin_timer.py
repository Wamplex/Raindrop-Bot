from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
import asyncio
import logging

TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"  # Замени на свой токен
ADMIN_ID = 7620745738  # Замени на свой Telegram ID

# Включаем логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="🎁 Забрать приз", url="https://link_to_prize")],
        [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
        [InlineKeyboardButton(text="🛡 Где я гарант?", callback_data="guarantee_chats")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")]
    ])

    if message.from_user.id == ADMIN_ID:
        kb.inline_keyboard.append([InlineKeyboardButton(text="🌐 Админ-панель", callback_data="admin")])
    
    await message.answer("Добро пожаловать в главное меню!", reply_markup=kb)

@router.callback_query(F.data == "create_deal")
async def create_deal(callback: CallbackQuery):
    await callback.message.edit_text("Опишите вашу сделку, пожалуйста. Укажите username второго участника, товары, цену и условия.")

@router.callback_query(F.data == "guarantee_chats")
async def guarantee_chats(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡 Где я гарантирую сделки:\n\n"
        "Чат 1: https://t.me/naytixa\n"
        "Чат 2: https://t.me/ChatFischS\n"
        "Чат 3: https://t.me/fischtradeschat"
    )

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text("Напишите свой вопрос, и админ скоро вам ответит.")

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    await callback.message.edit_text(f"👤 Ваш ID: {callback.from_user.id}\n📦 Сделок: 0")

@router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text(
        "🌐 Админ-панель:\n\n"
        "1. Сделать рассылку\n"
        "2. Посмотреть активных пользователей\n"
        "3. Ответить на обращение\n"
        "4. Изменить кнопки меню\n"
        "5. Настройки бота"
    )

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
