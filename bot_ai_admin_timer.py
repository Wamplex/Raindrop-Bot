import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from datetime import datetime

TOKEN = "7807213915:AAEkplZ9d3AXmbX6U11R2GoFPHPhLnspaus"  # Замените на свой токен
ADMIN_ID = 7620745738
ADMINS = {ADMIN_ID}

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

user_deals = {}

class AdminManagementState(StatesGroup):
    add_admin = State()

def main_menu(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🤝 Создать сделку")],
        [KeyboardButton(text="🎁 Получить приз")],
        [KeyboardButton(text="📬 Отзывы")],
        [KeyboardButton(text="🛡 Где я гарант?")],
        [KeyboardButton(text="🛠 Поддержка")],
        [KeyboardButton(text="👤 Личный кабинет")]
    ]
    if user_id in ADMINS:
        buttons.append([KeyboardButton(text="🌐 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def admin_panel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Список сделок")],
            [KeyboardButton(text="🛠 Управление админами")],
            [KeyboardButton(text="🔙 Вернуться в меню")]
        ], resize_keyboard=True
    )

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("👋 Привет! Добро пожаловать! ", reply_markup=main_menu(message.from_user.id))

@router.message(F.text == "🤝 Создать сделку")
async def create_deal_handler(message: Message):
    user_id = message.from_user.id
    user_deals[user_id] = datetime.now()
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить сделку", callback_data="cancel_deal")]
    ])
    await message.answer("✍️ Опишите вашу сделку.", reply_markup=cancel_kb)
    await bot.send_message(ADMIN_ID, f"📬 Новая сделка от <a href='tg://user?id={user_id}'>{user_id}</a>.")
    asyncio.create_task(auto_cancel_deal(user_id))

@router.message(F.text == "🎁 Получить приз")
async def get_prize_handler(message: Message):
    await message.answer(
        "Перейдите по ссылке: https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO",
        reply_markup=main_menu(message.from_user.id)
    )
    await message.answer("Свяжитесь с администратором: @RaindropSpam_bot")

@router.message(F.text == "🌐 Админ-панель")
async def admin_panel_handler(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Вы в админ-панели", reply_markup=admin_panel_menu())
    else:
        await message.answer("У вас нет доступа!")

@router.message(F.text == "📋 Список сделок")
async def admin_deals_handler(message: Message):
    if is_admin(message.from_user.id):
        deals_list = "\n".join([f"{k}: {v}" for k, v in user_deals.items()]) or "Сделок нет"
        await message.answer(f"Список:
{deals_list}", reply_markup=admin_panel_menu())

@router.message(F.text == "🛠 Управление админами")
async def admin_management_handler(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите ID нового админа:", reply_markup=admin_panel_menu())
        await state.set_state(AdminManagementState.add_admin)

@router.message(AdminManagementState.add_admin)
async def add_admin(message: Message, state: FSMContext):
    new_admin_id = message.text
    if new_admin_id.isdigit():
        ADMINS.add(int(new_admin_id))
        await message.answer(f"Пользователь {new_admin_id} добавлен!", reply_markup=admin_panel_menu())
        await state.clear()
    else:
        await message.answer("Неверный ID.", reply_markup=admin_panel_menu())

@router.message(F.text == "🔙 Вернуться в меню")
async def back_to_menu(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=main_menu(message.from_user.id))

@router.message(F.text == "📬 Отзывы")
async def reviews_handler(message: Message):
    await message.answer("Перейдите по ссылке, чтобы прочитать отзывы: https://t.me/raindrop_reviews")

@router.message(F.text == "🛡 Где я гарант?")
async def guarantee_handler(message: Message):
    await message.answer(
        "Чаты, в которых я гарант:\nЧат 1: https://t.me/naytixa\nЧат 2: https://t.me/ChatFischS\nЧат 3: https://t.me/fischtradeschat"
    )

async def auto_cancel_deal(user_id: int):
    await asyncio.sleep(3600)
    if user_id in user_deals:
        del user_deals[user_id]
        await bot.send_message(user_id, "❌ Ваша сделка была отменена.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

