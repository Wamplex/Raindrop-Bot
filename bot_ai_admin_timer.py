import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

API_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Заменить на свой токен

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Главное меню
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="Fisch \U0001F41F", callback_data="fisch_menu"),
         InlineKeyboardButton(text="BloxFruit \U0001F34C", callback_data="fruit_menu")]
    ])
    return keyboard

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в бота торговли!\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "fisch_menu")
async def show_fisch_prices(callback: types.CallbackQuery):
    prices = """
<b>Цены на Fisch \U0001F41F</b>:
1. Nessie — 30₽
2. Northstar Serpent — 15₽
3. Leviathan — 30₽
4. Moby — 15₽
5. Meg — 10₽
6. Kraken — 35₽
7. Scylla — 20₽
8. Orca — 10₽
9. Octophant — 5₽
10. Blue Whale — 6₽
11. Eternal Frostwhale — 15₽
12. Treble Bass — 10₽
13. Mustard — 10₽
14. Long Pike — 20₽
15. Banana — 10₽
16. Tartaruga — 10₽
17. Sea Mine — 20₽
18. Turkey — 10₽
19. Lovestormeel — 10₽
20. Crowned Anglerfish — 5₽
21. Crystallized Seadragon — 5₽
<b>+2₽ обычная мутация</b>, <b>+5₽ за Shiny, SS и др.</b>, <b>+10₽ за Ancient</b>
"""
    await callback.message.edit_text(prices, reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "fruit_menu")
async def show_fruit_prices(callback: types.CallbackQuery):
    fruits = """
<b>Цены на BloxFruit \U0001F34C</b>:
Leopard — 155₽
Gas — 175₽
Dough — 115₽
Venom — 50₽
T-Rex — 80₽
Gravity — 75₽
Mammoth — 45₽
Creation — 40₽
Buddha — 60₽
Shadow — 35₽
Portal — 45₽
Spider — 25₽
Quake — 20₽
"""
    await callback.message.edit_text(fruits, reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "create_deal")
async def create_deal_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("Пожалуйста, напишите @юзернейм второго участника сделки и коротко, что за сделка.")
    await callback.answer()

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
