from aiogram import Bot, Dispatcher, F, types
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram import Router
import asyncio

TOKEN = 'YOUR_BOT_TOKEN'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="💼 Создать сделку")],
    [KeyboardButton(text="🎁 Бесплатный приз")],
    [KeyboardButton(text="🛒 Товары")],
    [KeyboardButton(text="➕ Предложить товар")]
])

@dp.message(F.text == "/start")
async def start(message: Message):
    text = (
        "Этот бот предназначен для заключения сделок с другими пользователями, а также для покупки товаров.\n\n"
        "Вы можете:\n"
        "• Создать сделку\n"
        "• Получить бесплатный приз\n"
        "• Просмотреть доступные товары\n"
        "• Предложить свой товар\n\n"
        "Выберите одну из опций в меню ниже."
    )
    await message.answer(text, reply_markup=main_kb)

# 🎁 Бесплатный приз
@dp.message(F.text == "🎁 Бесплатный приз")
async def free_prize(message: Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎉 Забрать приз", url="https://t.me/virus_play_bot/app?startapp=inviteCodeuNWkBu8PylHXHXLO")]
    ])
    await message.answer("Чтобы забрать приз, нажмите кнопку ниже:", reply_markup=inline_kb)
    await message.answer("Свяжитесь с администрацией для получения приза: @RaindropSpam_bot")

# 💼 Сделка
@dp.message(F.text == "💼 Создать сделку")
async def create_deal_start(message: Message):
    await message.answer("Введите @username второй стороны сделки:")

    @dp.message()
    async def ask_deal_info(message: Message):
        username = message.text.strip()
        await message.answer(f"Отлично, теперь опишите вашу сделку с {username}:")

        @dp.message()
        async def final_deal(message: Message):
            deal_text = message.text.strip()
            await message.answer(f"✅ Сделка создана:\nПользователь: {username}\nОписание: {deal_text}")

# 🛒 Товары с кнопками покупки
@dp.message(F.text == "🛒 Товары")
async def show_products(message: Message):
    products = [
        {"name": "Fisch 100 шт", "price": "50₽"},
        {"name": "Fisch 300 шт", "price": "130₽"},
        {"name": "Fisch 500 шт", "price": "200₽"},
        {"name": "BloxFruit аккаунт (свежий)", "price": "120₽"},
        {"name": "BloxFruit аккаунт (прокачанный)", "price": "300₽"},
        {"name": "Nitro Discord", "price": "250₽"},
        {"name": "Spotify Premium 3 мес", "price": "90₽"},
        {"name": "YouTube Premium", "price": "70₽"},
    ]

    for product in products:
        button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить", callback_data=f"buy:{product['name']}")]
        ])
        await message.answer(f"🔹 <b>{product['name']}</b> — <i>{product['price']}</i>", reply_markup=button, parse_mode="HTML")

@dp.callback_query(F.data.startswith("buy:"))
async def handle_purchase(callback: types.CallbackQuery):
    product_name = callback.data.split(":", 1)[1]
    await callback.message.answer(f"🛍 Вы выбрали: <b>{product_name}</b>\n\nДля покупки свяжитесь с продавцом: @RaindropSpam_bot", parse_mode="HTML")
    await callback.answer()

# ➕ Предложить товар
@dp.message(F.text == "➕ Предложить товар")
async def suggest_product(message: Message):
    await message.answer("✍️ Напишите, какой товар вы хотите предложить:")

    @dp.message()
    async def get_suggestion(msg: Message):
        suggestion = msg.text
        await bot.send_message(chat_id="@RaindropSpam_bot", text=f"📩 Новое предложение от @{msg.from_user.username or msg.from_user.id}:\n{suggestion}")
        await msg.answer("✅ Ваше предложение отправлено администрации!")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
