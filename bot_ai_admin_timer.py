from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

@dp.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="🎁 Забрать приз", url="https://link_to_prize")],
        [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
        [InlineKeyboardButton(text="🛡 Где я гарант?", callback_data="guarantee_chats")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton(text="🌐 Админ-панель", callback_data="admin") if message.from_user.id == ADMIN_ID else None]
    ])
    kb.inline_keyboard = [row for row in kb.inline_keyboard if row[0] is not None]
    await message.answer("Привет! Добро пожаловать в магазин.", reply_markup=kb)

@dp.callback_query(F.data == "create_deal")
async def create_deal_callback(callback: CallbackQuery):
    await callback.message.edit_text("Опишите вашу сделку, пожалуйста. Укажите товары, количество и цену.")

@dp.callback_query(F.data == "guarantee_chats")
async def guarantee_chats_callback(callback: CallbackQuery):
    await callback.message.edit_text("Чат 1: https://t.me/naytixa\nЧат 2: https://t.me/ChatFischS\nЧат 3: https://t.me/fischtradeschat")

@dp.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    await callback.message.edit_text("Напишите ваш вопрос. Администратор скоро ответит вам лично.")

@dp.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.message.edit_text(f"Ваш ID: {callback.from_user.id}\nКоличество заказов: 0")

@dp.callback_query(F.data == "admin")
async def admin_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("🛡 Админ-панель:\nПросмотр, изменение и удаление товаров в разработке.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
