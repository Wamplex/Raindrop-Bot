from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, StateFilter
from aiogram import Router

import asyncio
import logging

TOKEN = "7807213915:AAHNcYeY27DuOtkJbwH_2lHbElfKd212FZU"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

dp.include_router(router)

class Deal(StatesGroup):
    writing_deal = State()

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🐠 Товары", callback_data="products")],
    [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/raindrop_reviews")],
    [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="cabinet")],
    [InlineKeyboardButton(text="🛡 Админ-панель", callback_data="admin")]
])

products_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎣 Fisch", callback_data="fisch")],
    [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="bloxfruit")]
])

support_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✏️ Написать в поддержку", callback_data="write_support")]
])

fisch_products = {
    "Sea Leviathan": {"price": 40, "mutations": ["Magma", "Sparkling Magma", "Solarblaze"]},
    "Nessie": {"price": 30, "mutations": ["SSA", "SST"]},
    "Northstar Serpent": {"price": 15, "mutations": ["Jolly", "SS"]}
    # Остальные рыбы ты можешь сам вписать по аналогии
}

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu)

@router.callback_query(F.data == "products")
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=products_menu)

@router.callback_query(F.data == "fisch")
async def show_fisch(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    for name in fisch_products:
        builder.button(text=name, callback_data=f"fisch_item:{name}")
    builder.button(text="➕ Предложить своё", callback_data="offer_fisch")
    await callback.message.edit_text("🎣 Выберите рыбу:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("fisch_item:"))
async def show_fisch_mutations(callback: CallbackQuery):
    name = callback.data.split(":")[1]
    data = fisch_products[name]
    builder = InlineKeyboardBuilder()
    for mutation in data["mutations"]:
        builder.button(text=mutation, callback_data=f"buy:{name}:{mutation}")
    await callback.message.edit_text(f"{name} - {data['price']}₽\nВыберите мутацию:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "bloxfruit")
async def show_bloxfruit(callback: CallbackQuery):
    fruits = ["Leopard", "Gas", "Dough", "Venom", "T-Rex", "Gravity", "Mammoth", "Creation", "Buddha", "Shadow", "Portal", "Spider", "Quake"]
    builder = InlineKeyboardBuilder()
    for fruit in fruits:
        builder.button(text=fruit, callback_data=f"buy:{fruit}:-")
    builder.button(text="➕ Предложить своё", callback_data="offer_bloxfruit")
    await callback.message.edit_text("🍇 Выберите фрукт:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("buy:"))
async def buy_handler(callback: CallbackQuery):
    _, name, mutation = callback.data.split(":")
    price = fisch_products.get(name, {}).get("price", 0)
    await callback.message.edit_text(f"Вы выбрали: {name} ({mutation})\nЦена: {price}₽\n\nДля покупки напишите администратору: @RaindropSpam_bot")
    await bot.send_message(ADMIN_ID, f"Новая покупка: {name} ({mutation}) от @{callback.from_user.username}")

@router.callback_query(F.data == "offer_fisch")
@router.callback_query(F.data == "offer_bloxfruit")
async def offer_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Опишите ваш товар и предложение:")
    await state.set_state(Deal.writing_deal)

@router.message(StateFilter(Deal.writing_deal))
async def handle_deal_offer(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(ADMIN_ID, f"Предложение товара от @{message.from_user.username}:\n{message.text}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data="accept_offer")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data="decline_offer")]
    ]))
    await message.answer("Ваше предложение отправлено!")

@router.callback_query(F.data == "support")
async def support_message(callback: CallbackQuery):
    await callback.message.edit_text("Напишите ваш вопрос. Администратор скоро ответит вам лично.", reply_markup=support_kb)

@router.callback_query(F.data == "cabinet")
async def cabinet(callback: CallbackQuery):
    await callback.message.edit_text(f"👤 Ваш ID: {callback.from_user.id}\nЗаказов: пока нет")

@router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.message.edit_text("🛡 Админ-панель:\nВыберите действие:")
    else:
        await callback.message.answer("Недоступно")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    asyncio.run(main())
