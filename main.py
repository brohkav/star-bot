
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

TOKEN = "8021837725:AAETUHRVuU1kvR_fK6DDiKwSJ5EqLECJzkc"
ADMIN_ID = 6973635029
KASPI_INFO = "4400430026331253 Бронислав В"
PRICE_PER_STAR = 9

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderStars(StatesGroup):
    waiting_for_amount = State()
    waiting_for_screenshot = State()
    waiting_for_username = State()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Добро пожаловать!Курс: 1 звезда = 9₸!Введите количество звёзд, которое хотите купить:")
    await dp.fsm.set_state(message.from_user.id, OrderStars.waiting_for_amount)

@dp.message(StateFilter(OrderStars.waiting_for_amount))
async def handle_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введите число.")
    amount = int(message.text)
    total = amount * PRICE_PER_STAR
    await state.update_data(amount=amount, total=total)
    await message.answer(f"Сумма к оплате: {total}₸
Переведите на Kaspi: {KASPI_INFO}
После оплаты отправьте скриншот чека.")
    await state.set_state(OrderStars.waiting_for_screenshot)

@dp.message(StateFilter(OrderStars.waiting_for_screenshot), content_types=types.ContentType.PHOTO)
async def handle_screenshot(message: types.Message, state: FSMContext):
    await state.update_data(screenshot=message.photo[-1].file_id)
    await message.answer("Отправьте ваш @username")
    await state.set_state(OrderStars.waiting_for_username)

@dp.message(StateFilter(OrderStars.waiting_for_username))
async def handle_username(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_photo(ADMIN_ID, photo=data['screenshot'], caption=(
        f"Заявка на покупку звёзд
Количество: {data['amount']}
Сумма: {data['total']}₸
Пользователь: {message.text}"
    ))
    await message.answer("Спасибо! Ожидайте подтверждение от администратора.")
    await state.clear()

@dp.message(Command("подтвердить"))
async def confirm_payment(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("У вас нет прав использовать эту команду.")
    parts = message.text.strip().split()
    if len(parts) < 2:
        return await message.answer("Введите имя пользователя через пробел после команды.")
    username = parts[1]
    await bot.send_message(username, "Ваши звезды были отправлены на баланс")
    await message.answer("Подтверждение отправлено.")

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
