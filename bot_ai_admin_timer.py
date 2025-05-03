from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio

TOKEN = "твой_токен_сюда"
ADMIN_ID = 7620745738

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# --- FSM ---
class AddFischState(StatesGroup):
    waiting_name = State()
    waiting_price = State()

class AddBloxState(StatesGroup):
    waiting_name = State()

class EditFischState(StatesGroup):
    waiting_new_name = State()
    waiting_new_price = State()

# --- Товары ---
fisch_items = {
    "Nessie": [("Nessie (Обычная)", 10), ("SSA Nessie", 15), ("SST Nessie", 20)],
    "Sea Leviathan": [("Sea Leviathan", 40)]
}

bloxfruit_items = ["Leopard", "Gas", "Dough (2x)", "Venom"]

@dp.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐠 Товары", callback_data="menu")],
        [InlineKeyboardButton(text="🛡 Админ-панель", callback_data="admin")] if message.from_user.id == ADMIN_ID else []
    ])
    kb.inline_keyboard = [row for row in kb.inline_keyboard if row]
    await message.answer("Привет! Добро пожаловать в магазин.", reply_markup=kb)

@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Fisch", callback_data="fisch")],
        [InlineKeyboardButton(text="🍇 Bloxfruit", callback_data="blox")]
    ])
    await callback.message.edit_text("Выберите категорию:", reply_markup=kb)

@dp.callback_query(F.data == "fisch")
async def fisch_callback(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for fish in fisch_items:
        kb.button(text=fish, callback_data=f"fish_{fish}")
    kb.adjust(2)
    await callback.message.edit_text("🎣 Fisch:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("fish_"))
async def fish_detail(callback: CallbackQuery):
    fish = callback.data.split("_", 1)[1]
    mutations = fisch_items.get(fish, [])
    kb = InlineKeyboardBuilder()
    kb.button(text="✏ Изменить", callback_data=f"edit_{fish}")
    kb.button(text="🗑 Удалить", callback_data=f"delete_{fish}")
    kb.adjust(2)
    text = f"🐟 {fish} — варианты:\n" + "\n".join(f"- {m[0]} — {m[1]}💎" for m in mutations)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "blox")
async def blox_callback(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for fruit in bloxfruit_items:
        kb.button(text=fruit, callback_data=f"blox_{fruit}")
    kb.adjust(2)
    await callback.message.edit_text("🍇 Bloxfruit:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("blox_"))
async def blox_detail(callback: CallbackQuery):
    fruit = callback.data.split("_", 1)[1]
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Удалить", callback_data=f"delete_blox_{fruit}")
    await callback.message.edit_text(f"🍇 {fruit}", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin")
async def admin_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить Fisch", callback_data="add_fisch")],
        [InlineKeyboardButton(text="➕ Добавить Bloxfruit", callback_data="add_blox")]
    ])
    await callback.message.edit_text("🛡 Админ-панель:", reply_markup=kb)

@dp.callback_query(F.data == "add_fisch")
async def add_fisch(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddFischState.waiting_name)
    await callback.message.edit_text("Введите название Fisch:")

@dp.message(AddFischState.waiting_name)
async def fisch_enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddFischState.waiting_price)
    await message.answer("Введите цену:")

@dp.message(AddFischState.waiting_price)
async def fisch_enter_price(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    try:
        price = int(message.text)
    except ValueError:
        return await message.answer("Введите число!")
    if name in fisch_items:
        fisch_items[name].append((name, price))
    else:
        fisch_items[name] = [(name, price)]
    await message.answer(f"Добавлен Fisch: {name} — {price}💎")
    await state.clear()

@dp.callback_query(F.data == "add_blox")
async def add_blox(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddBloxState.waiting_name)
    await callback.message.edit_text("Введите название Bloxfruit:")

@dp.message(AddBloxState.waiting_name)
async def blox_enter_name(message: Message, state: FSMContext):
    bloxfruit_items.append(message.text)
    await message.answer(f"Добавлен Bloxfruit: {message.text}")
    await state.clear()

@dp.callback_query(F.data.startswith("delete_"))
async def delete_item(callback: CallbackQuery):
    _, name = callback.data.split("_", 1)
    if name in fisch_items:
        del fisch_items[name]
        await callback.message.edit_text(f"Fisch '{name}' удалён.")
    elif name in bloxfruit_items:
        bloxfruit_items.remove(name)
        await callback.message.edit_text(f"Bloxfruit '{name}' удалён.")
    else:
        await callback.message.edit_text("Не найдено.")

@dp.callback_query(F.data.startswith("edit_"))
async def edit_fisch(callback: CallbackQuery, state: FSMContext):
    fish = callback.data.split("_", 1)[1]
    await state.update_data(old_name=fish)
    await state.set_state(EditFischState.waiting_new_name)
    await callback.message.edit_text("Введите новое название Fisch:")

@dp.message(EditFischState.waiting_new_name)
async def new_name(message: Message, state: FSMContext):
    await state.update_data(new_name=message.text)
    await state.set_state(EditFischState.waiting_new_price)
    await message.answer("Введите новую цену:")

@dp.message(EditFischState.waiting_new_price)
async def new_price(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        price = int(message.text)
    except ValueError:
        return await message.answer("Введите число!")
    old_name = data['old_name']
    new_name = data['new_name']
    if old_name in fisch_items:
        fisch_items.pop(old_name)
        fisch_items[new_name] = [(new_name, price)]
        await message.answer(f"Изменено: {old_name} -> {new_name} — {price}💎")
    await state.clear()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
