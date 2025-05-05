import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

TOKEN = "7807213915:AAEkplZ9d3AXmbX6U11R2GoFPHPhLnspaus"  # Замените на свой токен
ADMIN_ID = 7620745738  # Ваш Telegram ID
ADMINS = {ADMIN_ID}

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_deals = {}  # Активные сделки

# Состояния FSM для управления админами
class AdminManagementState(StatesGroup):
    add_admin = State()

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
            [KeyboardButton(text="🔙 Вернуться в меню")]
        ], resize_keyboard=True
    )

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

@router.message(CommandStart())
async def start_handler(message: Message):
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

@router.callback_query(F.data == "cancel_deal")
async def cancel_deal_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_deals:
        del user_deals[user_id]
        await callback.message.edit_text("❌ Сделка была отменена.")

@router.message(F.text == "🎁 Получить приз")
async def get_prize_handler(message: Message):
    await message.answer(
        "Перейдите по ссылке, чтобы получить приз: https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO",
        reply_markup=main_menu(message.from_user.id)
    )
    await message.answer("Свяжитесь с администратором, чтобы забрать приз: @RaindropSpam_bot")

@router.message(F.text == "💬 Отзывы")
async def reviews_handler(message: Message):
    await message.answer("📢 Отзывы о нашей работе можно посмотреть здесь:\nhttps://t.me/your_reviews_channel")

@router.message(F.text == "🛡 Где я гарант?")
async def where_guarantee_handler(message: Message):
    await message.answer("🛡 Вы можете найти меня как гаранта здесь:\nhttps://t.me/your_guarantee_channel")

@router.message(F.text == "👤 Личный кабинет")
async def profile_handler(message: Message):
    user_id = message.from_user.id
    if user_id in user_deals:
        deal_time = user_deals[user_id].strftime("%Y-%m-%d %H:%M:%S")
        await message.answer(f"👤 Личный кабинет:\n\n📌 Активная сделка:\nСоздана: {deal_time}")
    else:
        await message.answer("👤 Личный кабинет:\n\nУ вас нет активных сделок.")

@router.message(F.text == "🌐 Админ-панель")
async def admin_panel_handler(message: Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы в админ-панели", reply_markup=admin_panel_menu())
    else:
        await message.answer("У вас нет доступа к админ-панели!")

@router.message(F.text == "📋 Список сделок")
async def admin_deals_handler(message: Message):
    if is_admin(message.from_user.id):
        if user_deals:
            deals_list = "\n".join([f"{key}: {val}" for key, val in user_deals.items()])
        else:
            deals_list = "Нет активных сделок."
        await message.answer(f"Список активных сделок:\n{deals_list}", reply_markup=admin_panel_menu())

@router.message(F.text == "🛠 Управление админами")
async def admin_management_handler(message: Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("Введите ID нового админа для добавления:", reply_markup=admin_panel_menu())
        await state.set_state(AdminManagementState.add_admin)

@router.message(AdminManagementState.add_admin)
async def add_admin(message: Message, state: FSMContext):
    new_admin_id = message.text
    if new_admin_id.isdigit() and int(new_admin_id) not in ADMINS:
        ADMINS.add(int(new_admin_id))
        await message.answer(f"Пользователь {new_admin_id} был добавлен в список админов!", reply_markup=admin_panel_menu())
    else:
        await message.answer("Неверный ID или пользователь уже является админом.", reply_markup=admin_panel_menu())
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
