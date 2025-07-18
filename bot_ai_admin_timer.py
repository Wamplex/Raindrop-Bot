import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.bot import DefaultBotProperties
from datetime import datetime

TOKEN = "7807213915:AAG0p6X2sCjgEVNngfsgCHef87QVmFzUs0I"
ADMIN_ID = 7620745738
ADMINS = {ADMIN_ID}

# Здесь исправление: используем default=DefaultBotProperties(...)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

user_deals = {}
user_data = set()  # Список всех, кто запускал бота

class AdminManagementState(StatesGroup):
    add_admin = State()
    broadcast = State()

def main_menu(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🤝 Создать сделку")],
        [KeyboardButton(text="🎁 Получить приз")],
        [KeyboardButton(text="💬 Отзывы")],
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
            [KeyboardButton(text="📢 Массовая рассылка")],
            [KeyboardButton(text="🔙 Вернуться в меню")]
        ], resize_keyboard=True
    )

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

@router.message(CommandStart())
async def start_handler(message: Message):
    user_data.add(message.from_user.id)
    await message.answer("👋 Привет! Добро пожаловать! Выберите нужный раздел ниже:", reply_markup=main_menu(message.from_user.id))

@router.message(F.text == "🤝 Создать сделку")
async def create_deal_handler(message: Message):
    user_id = message.from_user.id
    user_deals[user_id] = datetime.now()
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить сделку", callback_data="cancel_deal")]
    ])
    await message.answer(
        "✍️ Опишите вашу сделку.\n\nУкажите username второго участника, условия, цену и детали.",
        reply_markup=cancel_kb
    )
    await bot.send_message(ADMIN_ID, f"📬 Новая сделка от <a href='tg://user?id={user_id}'>{user_id}</a>.")
    asyncio.create_task(auto_cancel_deal(user_id))

@router.message(F.text == "🎁 Получить приз")
async def get_prize_handler(message: Message):
    await message.answer(
        "Перейдите по ссылке, чтобы получить приз: https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO",
        reply_markup=main_menu(message.from_user.id)
    )
    await message.answer("Свяжитесь с администратором, чтобы забрать приз: @RaindropSpam_bot")

@router.message(F.text == "💬 Отзывы")
async def reviews_handler(message: Message):
    await message.answer("Отзывы доступны здесь: https://t.me/raindrop_reviews")

@router.message(F.text == "🛡 Где я гарант?")
async def guarantee_handler(message: Message):
    await message.answer(
        "Чаты в которых я гарант:\nЧат 1: https://t.me/GrowAGardenChatee\nЧат 2: https://t.me/ChatFischS\nЧат 3: https://t.me/cchatgrowagarden"
    )

@router.message(F.text == "👤 Личный кабинет")
async def profile_handler(message: Message):
    user_id = message.from_user.id
    active = user_deals.get(user_id)
    await message.answer(f"👤 Ваш профиль:\n🆔 ID: {user_id}\n📝 Сделка активна: {'Да' if active else 'Нет'}")

@router.message(F.text == "🌐 Админ-панель")
async def admin_panel_handler(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("Вы в админ-панели", reply_markup=admin_panel_menu())
    else:
        await message.answer("У вас нет доступа к админ-панели!")

@router.message(F.text == "📋 Список сделок")
async def admin_deals_handler(message: Message):
    if is_admin(message.from_user.id):
        if user_deals:
            deals_list = "\n".join([f"{key}: {val}" for key, val in user_deals.items()])
            await message.answer(f"Список активных сделок:\n{deals_list}", reply_markup=admin_panel_menu())
        else:
            await message.answer("Нет активных сделок.", reply_markup=admin_panel_menu())

@router.message(F.text == "🛠 Управление админами")
async def admin_management_handler(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите ID нового админа:", reply_markup=admin_panel_menu())
        await state.set_state(AdminManagementState.add_admin)
    else:
        await message.answer("У вас нет доступа к этой функции!")

@router.message(AdminManagementState.add_admin)
async def add_admin(message: Message, state: FSMContext):
    new_admin_id = message.text
    if new_admin_id.isdigit():
        new_admin_id = int(new_admin_id)
        if new_admin_id not in ADMINS:
            ADMINS.add(new_admin_id)
            await message.answer(f"Пользователь {new_admin_id} добавлен в админы.", reply_markup=admin_panel_menu())
        else:
            await message.answer("Пользователь уже является админом.", reply_markup=admin_panel_menu())
    else:
        await message.answer("Неверный ID.", reply_markup=admin_panel_menu())
    await state.clear()

@router.message(F.text == "📢 Массовая рассылка")
async def broadcast_handler(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите текст для рассылки всем пользователям:")
        await state.set_state(AdminManagementState.broadcast)

@router.message(AdminManagementState.broadcast)
async def do_broadcast(message: Message, state: FSMContext):
    sent, failed = 0, 0
    for uid in user_data:
        try:
            await bot.send_message(uid, message.text)
            sent += 1
        except:
            failed += 1
    await message.answer(f"Рассылка завершена. ✅ Отправлено: {sent}, ❌ Ошибок: {failed}", reply_markup=admin_panel_menu())
    await state.clear()

@router.message(F.text == "🔙 Вернуться в меню")
async def back_to_menu(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=main_menu(message.from_user.id))

async def auto_cancel_deal(user_id: int):
    await asyncio.sleep(3600)
    if user_id in user_deals:
        del user_deals[user_id]
        await bot.send_message(user_id, "❌ Ваша сделка была отменена из-за бездействия.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
