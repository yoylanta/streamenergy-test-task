from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
import logging
import asyncio
from aiogram import Router

def read_token_from_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.readline().strip()

API_TOKEN = read_token_from_file('token.txt')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
print("Logging configuration set up successfully!")

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    logger.info(f"User {message.from_user.id} started the conversation")
    try:
        await message.reply("Welcome to the Notes Bot!")
    except Exception as e:
        logger.error(f"Error responding to /start command: {e}")

@dp.message(F.text)
async def echo(message: types.Message):
    logger.info(f"User {message.from_user.id} sent  a message: {message.text}")
    try:
        await message.answer(f"You said: {message.text}")
    except Exception as e:
        logger.error(f"Error responding to user message: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())