from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram import F
import logging
import asyncio
import requests
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State

def read_token_from_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.readline().strip()

API_TOKEN = read_token_from_file('token.txt')
FASTAPI_ENDPOINT = 'http://127.0.0.1:8080/notes'  

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

class NoteCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_tag = State()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    logger.info(f"User {message.from_user.id} started the conversation")
    try:
        await message.reply("Welcome to the Notes Bot! Use /new to create a new note.")
    except Exception as e:
        logger.error(f"Error responding to /start command: {e}")

@dp.message(Command(commands=['new']))
async def create_new_note(message: types.Message, state: FSMContext):
    await message.reply("Enter the note title:")
    await state.set_state(NoteCreation.waiting_for_title)
    
# Handle title input and ask for content
@dp.message(NoteCreation.waiting_for_title)
async def process_note_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.reply("Enter the note content:")
    await state.set_state(NoteCreation.waiting_for_content)

# Handle content input and ask for tags
@dp.message(NoteCreation.waiting_for_content)
async def process_note_content(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.reply("Enter the note tags (comma-separated):")
    await state.set_state(NoteCreation.waiting_for_tag)

# Handle tags input and create note via FastAPI
@dp.message(NoteCreation.waiting_for_tag)
async def process_note_tag(message: types.Message, state: FSMContext):
    await state.update_data(tag=message.text)
    note_data = await state.get_data()
    title = note_data.get('title')
    content = note_data.get('content')
    tag = note_data.get('tag')
    logger.info(f"Received note data - Title: {title}, Content: {content}, Tags: {tag}")
    tags = [t.strip() for t in tag.split(',')] if tag else []
    logger.info(f"Processed tags: {tags}")
    payload = {
        'title': title,
        'content': content,
        'tags': tags
    }
    try:
        response = requests.post(FASTAPI_ENDPOINT, json=payload)
        logger.info(f"FastAPI response status code: {response.status_code}")
        if response.status_code == 201:  # Assuming 201 for successful creation
            await message.reply("Note created successfully!")
        else:
            await message.reply("Failed to create the note. Please try again.")
    except requests.RequestException as e:
        logger.error(f"Error making request to FastAPI: {e}")
        await message.reply("Failed to create the note due to a request error. Please try again.")

    await state.clear()

async def start_bot():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start_bot())