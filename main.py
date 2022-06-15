import logging
from config import *
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from db import *
from soupbruh import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from utils import *

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


async def save(user_id, text):
    await database.execute(f"INSERT INTO users(telegram_id, text) "
                           f"VALUES (:telegram_id, :text)", values={'telegram_id': user_id, 'text': text})


# async def read(user_id):
#     messages = await database.fetch_all('SELECT text '
#                                         'FROM messages '
#                                         'WHERE telegram_id = :telegram_id ',
#                                         values={'telegram_id': user_id})
#     return messages


async def read(user_id):
    result = await database.fetch_all('SELECT name '
                                      'FROM users '
                                      'WHERE id = :telegram_id ',
                                      values={'telegram_id': '95349539'})
    return result


@dp.message_handler()
async def start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.answer('Вы в меню, 1 - крипта, 2 - гос, 3 - home')
    await state.set_state(BotStates.FIRST_CHOICE)


@dp.message_handler(state=BotStates.FIRST_CHOICE)
async def first_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    if message.text == '1':
        await message.reply('Крипта! 1 - своя пара, 2 - популярные', reply=False)
        await state.set_state(BotStates.CRYPTO_CHOICE)
    elif message.text == '2':
        await message.reply('Гос! 1 - своя пара, 2 - популярные', reply=False)
        await state.set_state(BotStates.GOS_CHOICE)
    elif message.text == '3':
        await message.reply('Гос! 1 - своя пара, 2 - популярные', reply=False)
        await state.set_state(BotStates.MENU)


@dp.message_handler(state=BotStates.CRYPTO_CHOICE)
async def second_test_state_case_met(message: types.Message):
    await message.reply('cryptochoice!', reply=False)


@dp.message_handler(state=BotStates.CRYPTO_CHOICE)
async def second_test_state_case_met(message: types.Message):
    await message.reply('cryptochoice!', reply=False)


@dp.message_handler(state=BotStates.GOS_CHOICE)
async def second_test_state_case_met(message: types.Message):
    await message.reply('GOSS!!!!', reply=False)


@dp.message_handler(state=BotStates.MENU)
async def second_test_state_case_met(message: types.Message):
    await message.reply('MENU!!!!!', reply=False)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
