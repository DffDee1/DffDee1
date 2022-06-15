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
async def echo(message: types.Message):
    # messages = await read(message.from_user.id)
    # await message.answer(messages)
    state = dp.current_state(user=message.from_user.id)
    await message.answer('1 - первое, 2 - второе')
    if message.text == '1':
        await state.set_state(TestStates.all()[1])
    elif message.text == '2':
        await state.set_state(TestStates.all()[2])
    else:
        await state.set_state(TestStates.TEST_STATE_3)


@dp.message_handler(state=TestStates.TEST_STATE_1)
async def first_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('Первый!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_2)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('Второй!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_3)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('3!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_4)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_5)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_6)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_7)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_8)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_9)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_10)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)

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
