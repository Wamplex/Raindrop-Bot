import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime, timedelta

# Твой токен
TOKEN = "7807213915:AAEkplZ9d3AXmbX6U11R2GoFPHPhLnspaus"
ADMIN_ID = 7620745738  # замени на свой Telegram ID

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

user_deals = {}  # для отслеживания активных сделок и автоотмены

def main_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="🎁 Забрать приз", url="https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO")],
        [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
        [InlineKeyboardButton(text="🛡 Где я гарант?", callback_data="guarantee_chats")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton(text="🌐 Админ-панель", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("👋 Привет! Добро пожаловать! Выберите нужный раздел ниже:", reply_markup=main_menu(message.from_user.id))

@router.callback_query(F.data == "create_deal")
async def create_deal_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_deals[user_id] = datetime.now()
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить сделку", callback_data="cancel_deal")]
    ])
    await callback.message.edit_text(
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
    await callback.message.edit_text("❌ Сделка отменена.")
    await bot.send_message(ADMIN_ID, f"⚠️ Сделка пользователя {user_id} была отменена.")

async def auto_cancel_deal(user_id: int):
    await asyncio.sleep(3600)  # 1 час
    if user_id in user_deals:
        del user_deals[user_id]
        try:
            await bot.send_message(user_id, "⏳ Сделка отменена из-за бездействия.")
            await bot.send_message(ADMIN_ID, f"⌛ Сделка пользователя {user_id} была автоотменена.")
        except:
            pass

@router.callback_query(F.data == "guarantee_chats")
async def guarantee_chats_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡 Где я гарант?\n\n"
        "Чат 1: https://t.me/naytixa\n"
        "Чат 2: https://t.me/ChatFischS\n"
        "Чат 3: https://t.me/fischtradeschat"
    )

@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    await callback.message.edit_text("✉️ Напишите ваш вопрос. Админ скоро свяжется с вами.")
    await bot.send_message(ADMIN_ID, f"📩 Новый вопрос от <a href='tg://user?id={callback.from_user.id}'>{callback.from_user.id}</a>.")

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        f"👤 Ваш ID: <code>{callback.from_user.id}</code>\n"
        f"📦 Количество сделок: 0"
    )

@router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text(
        "🌐 <b>Админ-панель</b>\n\n"
        "1. 🔊 Сделать рассылку\n"
        "2. 📊 Активные пользователи\n"
        "3. 📥 Ответить на обращение\n"
        "4. ⚙️ Изменить кнопки меню\n"
        "5. 🛠 Настройки бота"
    )

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
