import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

# === ЗАМЕНИ ЭТО НА СВОЙ ТОКЕН ===
TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
ADMIN_ID = 7620745738  # замени на свой Telegram ID

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
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="🌐 Админ-панель", callback_data="admin")
        ])

    await message.answer("Привет! Добро пожаловать в магазин.", reply_markup=kb)


@router.callback_query(F.data == "create_deal")
async def create_deal_callback(callback: CallbackQuery):
    await callback.message.edit_text("Опишите вашу сделку, пожалуйста. Укажите username второго участника, товары, цену и условия.")


@router.callback_query(F.data == "guarantee_chats")
async def guarantee_chats_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡 Где я гарант:\n"
        "Чат 1: https://t.me/naytixa\n"
        "Чат 2: https://t.me/ChatFischS\n"
        "Чат 3: https://t.me/fischtradeschat"
    )


@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    await callback.message.edit_text("Напишите ваш вопрос. Администратор скоро свяжется с вами.")


@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.message.edit_text(f"👤 Ваш ID: {callback.from_user.id}\n📦 Кол-во сделок: 0")


@router.callback_query(F.data == "admin")
async def admin_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("У вас нет доступа.", show_alert=True)
        return
    await callback.message.edit_text(
        "🌐 Админ-панель:\n\n"
        "1. Сделать рассылку\n"
        "2. Посмотреть активных пользователей\n"
        "3. Ответить на обращение\n"
        "4. Изменить кнопки меню\n"
        "5. Настройки бота"
    )


# === Регистрируем router и запускаем ===
dp.include_router(router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # Удаляет Webhook, если был
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
