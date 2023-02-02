from aiogram import Bot, Dispatcher, types
from config import TOKEN
from loguru import logger

bot = Bot(TOKEN)
dp = Dispatcher(bot)

logger.add('log_info.log',
           format="{time} - {level} - {message}",
           level='DEBUG')