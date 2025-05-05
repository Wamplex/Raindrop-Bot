from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
import asyncio
from datetime import datetime, timedelta

TOKEN = "7807213915:AAGGA7EDq-e_8uUnpKfg4ZhUe-KfJfXKvUY"
ADMIN_ID = 7620745738

bot = Bot(token=7807213915:AAGGA7EDq-e_8uUnpKfg4ZhUe-KfJfXKvUY)
dp = Dispatcher()
router = Router()

# Хранилище активных сделок (user_id: datetime создания)
active_deals = {}

# Главное меню
def main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="🤝 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="🎁 Забрать приз", url="https://link_to_prize")],
        [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
        [InlineKeyboardButton(text="🛡 Где я гарант?", callback_data="guarantee_chats")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="🌐 Админ-панель", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Добро пожаловать! Используйте кнопки ниже для взаимодействия с ботом.", 
                         reply_markup=main_menu(is_admin=(message.from_user.id == ADMIN_ID)))

@router.callback_query(F.data == "create_deal")
async def create_deal_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    active_deals[user_id] = datetime.now()
    cancel_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить сделку", callback_data="cancel_deal")]
    ])
    await callback.message.edit_text(
        "Опишите вашу сделку.\nУкажите username второго участника, товары, цену и условия.",
        reply_markup=cancel_button
    )
    await notify_admin(f"Новая сделка от @{callback.from_user.username or 'пользователь без username'}!")

@router.callback_query(F.data == "cancel_deal")
async def cancel_deal_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    active_deals.pop(user_id, None)
    await callback.message.edit_text("Сделка отменена.", reply_markup=main_menu(is_admin=(user_id == ADMIN_ID)))

@router.callback_query(F.data == "guarantee_chats")
async def guarantee_chats_callback(callback: CallbackQuery):
    text = "📌 Где я гарант?\n\n" \
           "Чат 1: https://t.me/naytixa\n" \
           "Чат 2: https://t.me/ChatFischS\n" \
           "Чат 3: https://t.me/fischtradeschat"
    await callback.message.edit_text(text)

@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    await callback.message.edit_text("Напишите ваш вопрос. Администратор скоро свяжется с вами.")
    await notify_admin(f"🛠 Обращение в поддержку от @{callback.from_user.username or 'пользователь без username'}")

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.message.edit_text(f"👤 Ваш ID: {callback.from_user.id}\n📦 Кол-во сделок: 0")

@router.callback_query(F.data == "admin")
async def admin_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    text = (
        "🌐 Админ-панель:\n\n"
        "1. Сделать рассылку\n"
        "2. Посмотреть активных пользователей\n"
        "3. Ответить на обращение\n"
        "4. Изменить кнопки меню\n"
        "5. Настройки бота"
    )
    await callback.message.edit_text(text)

# Проверка сделок на автоотмену
async def deal_timeout_checker():
    while True:
        now = datetime.now()
        expired_users = [user for user, time in active_deals.items() if now - time > timedelta(hours=1)]
        for user in expired_users:
            try:
                await bot.send_message(user, "⏳ Сделка отменена из-за бездействия.")
            except:
                pass
            active_deals.pop(user, None)
        await asyncio.sleep(60)

async def notify_admin(text: str):
    try:
        await bot.send_message(ADMIN_ID, text)
    except:
        pass

dp.include_router(router)

async def main():
    asyncio.create_task(deal_timeout_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
