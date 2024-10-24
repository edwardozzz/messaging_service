import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F

API_TOKEN = '7981185062:AAG6sxlPQPMN5OU1g1uh3LGTazP_Latv2zo'  # Ваш токен бота

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Я ваш бот.")

@dp.message(F.text)
async def echo(message: types.Message):
    await message.answer(message.text)

if __name__ == "__main__":
    import asyncio

    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
