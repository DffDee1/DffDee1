import asyncio
import logging
import os

import aioschedule
import psycopg2
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from psycopg2 import Error

from config import *
from soupbruh import *
from utils import *

scheduler = AsyncIOScheduler()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
curs = conn.cursor()


try:
    create_table_query = '''
                CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                pair_name VARCHAR (100) NOT NULL UNIQUE,
                old_price REAL NOT NULL,
                amount REAL NOT NULL
                );'''
    curs.execute(create_table_query)
    conn.commit()

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL 1", error)
    curs.execute("rollback")

    create_table_query = '''
                    CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    pair_name VARCHAR (100) NOT NULL,
                    old_price REAL NOT NULL,
                    amount REAL NOT NULL
                    );'''
    curs.execute(create_table_query)
    conn.commit()


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


async def view_portf(message):
    try:
        curs.execute(f"SELECT * from users where chat_id = {message.chat.id}")
        checks = curs.fetchall()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL 3", error)
        curs.execute("rollback")

        curs.execute(f"SELECT * from users where chat_id = {message.chat.id}")
        checks = curs.fetchall()

    text = ''
    for i in checks:
        price = await get_price_of_pair(i[2])
        price = float(price['price'])
        percent = round((i[3] - price) / price * 100, 2)
        text += f'{i[2]} в кол-ве {i[4]}: {price} ({"+" if percent > 0 else ""}{percent}%)\n'

    return text


async def check_new_pair(message):
    try:
        curs.execute(f"SELECT pair_name from users where chat_id = {message.chat.id}")
        checks = curs.fetchall()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL 3", error)
        curs.execute("rollback")

        curs.execute(f"SELECT pair_name from users where chat_id = {message.chat.id}")
        checks = curs.fetchall()

    for i in checks:
        if message.text in i:
            return False
    return True


async def save(message):

    try:
        insert_query = """ INSERT INTO users (chat_id, pair_name, old_price, amount)
                                                                      VALUES (%s, %s, %s, %s)"""
        old_p = await get_price_of_pair(message.text)
        item_tuple = (message.chat.id, message.text, str(round(float(old_p['price']), 3)), 12345)
        curs.execute(insert_query, item_tuple)
        conn.commit()

    except (Exception, Error) as error:

        print("Ошибка при работе с PostgreSQL 2", error)
        curs.execute("rollback")

        insert_query = """ INSERT INTO users (chat_id, pair_name, old_price, amount)
                                                                              VALUES (%s, %s, %s, %s)"""
        old_p = await get_price_of_pair(message.text)
        item_tuple = (message.chat.id, message.text, str(round(float(old_p['price']), 3)), 12345)
        curs.execute(insert_query, item_tuple)
        conn.commit()


async def read(message):
    try:
        curs.execute(f"SELECT pair_name from users where chat_id = {message.chat.id}")
        checks = curs.fetchall()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL 3", error)
        curs.execute("rollback")

        curs.execute(f"SELECT pair_name from users where chat_id = {message.chat.id}")
        checks = curs.fetchall()
    return checks


async def menu(message):
    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in
                   ['Гос. валюты', 'Криптовалюты', '🔔Уведомления']])
    await bot.send_message(message.chat.id,
                           text="Вы вернулись в меню)",
                           reply_markup=keyboard)
    await state.set_state(TestStates.all()[1])


async def menu_add():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menus = types.KeyboardButton("🏠Меню")
    keyboard.add(menus)
    return keyboard


@dp.message_handler()
async def start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == '🏠Меню':
        await menu(message)

    keyboard.add(*[types.KeyboardButton(name) for name in
                   ['Гос. валюты', 'Криптовалюты', '🔔Уведомления']])
    text = 'Привет, {}! Я умею показывать курсы валют и обменники!\n' \
           'Ты можешь воспользоваться вариантами из фотографии или продолжить кнопками!' \
        .format(message.from_user.first_name)

    with open('commands.png', 'rb') as photo:
        await bot.send_photo(message.from_user.id,
                             photo,
                             caption=text,
                             reply_markup=keyboard)
        await state.set_state(TestStates.all()[1])


@dp.message_handler(state=TestStates.TEST_STATE_1)                                                        # FIRST CHOICE
async def first_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == 'Гос. валюты':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['Указать валюту', 'Выбрать валюту', '🏠Меню']])
        await state.set_state(TestStates.all()[0])
        await message.reply('Выберите вариант!',
                            reply=False,
                            reply_markup=keyboard)

    elif message.text == 'Криптовалюты':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['⌨Ввести свою пару', '📊Популярные пары', '🏠Меню']])
        await state.set_state(TestStates.all()[2])
        await message.reply('Выберите вариант',
                            reply=False,
                            reply_markup=keyboard)

    elif message.text == '🔔Уведомления':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['🔔Добавить пару', '🔕Удалить пару', 'Мои пары', '🏠Меню']])
        await state.set_state(TestStates.all()[4])
        text = 'Выберите вариант' + str(message.chat.id)
        await message.reply(text,
                            reply=False,
                            reply_markup=keyboard)


@dp.message_handler(state=TestStates.TEST_STATE_2)                                                              # CRYPTO
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message)
        return None

    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == '⌨Ввести свою пару':
        keyboard = await menu_add()
        await message.reply('Введите пару в формате "coin/coin"'
                            '\nНапример "btc/rub" без кавычек!',
                            reply=False,
                            reply_markup=keyboard)
        await state.set_state(TestStates.all()[9])

    elif message.text == '📊Популярные пары':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['🇷🇺RUB', '🇺🇸USDT', '🌐BTC', '🏠Меню']])
        await state.set_state(TestStates.all()[3])
        await message.reply('Пары к какой валюте предлагать?',
                            reply=False,
                            reply_markup=keyboard)

    else:
        await message.reply('Не понял тебя, воспользуйся кнопками.',
                            reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_3)                                                       # CRYPTO CHOICE
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message)
        return None

    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == '🇷🇺RUB':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['BTC/RUB', 'ETH/RUB', 'BNB/RUB', 'USDT/RUB', '🏠Меню']])
        await bot.send_message(message.chat.id,
                               text="Выберите пару",
                               reply_markup=keyboard)

    elif message.text == '🇺🇸USDT':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', '🏠Меню']])
        await bot.send_message(message.chat.id,
                               text="Выберите пару",
                               reply_markup=keyboard)

    elif message.text == '🌐BTC':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['ETH/BTC', 'BNB/BTC', 'XRP/BTC', '🏠Меню']])
        await bot.send_message(message.chat.id,
                               text="Выберите пару",
                               reply_markup=keyboard)

    else:
        await bot.send_message(message.chat.id,
                               text="Не понял тебя, воспользуйся клавиатурой.")
        return None

    await state.set_state(TestStates.all()[9])


@dp.message_handler(state=TestStates.TEST_STATE_4)                                                               # PORTF
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message)
        return None

    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == '🔔Добавить пару':
        keyboard = await menu_add()
        await message.reply('Введите слитно пару, которую хотите добавить в портфель.\n'
                            'Например, "btcrub" без кавычек.',
                            reply=False,
                            reply_markup=keyboard)
        await state.set_state(TestStates.all()[5])

    elif message.text == '🔕Удалить пару':
        # keyboard.add(*[types.KeyboardButton(name) for name in
        #                ['🇷🇺RUB', '🇺🇸USDT', '🌐BTC', '🏠Меню']])
        # await state.set_state(TestStates.all()[3])
        await message.reply('wait plz',
                            reply=False,
                            reply_markup=keyboard)

    elif message.text == 'Мои пары':
        aboba = await view_portf(message)
        await message.reply(aboba,
                            reply=False)

    else:
        await message.reply('Не понял тебя, воспользуйся кнопками.',
                            reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_5)                                                           # PORTF ADD
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message)
        return None

    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if await check_pair(message.text):

        if await check_new_pair(message):
            await save(message)
            await message.reply('Введите кол-во монет',
                                reply=False,
                                reply_markup=keyboard)
            await state.set_state(TestStates.all()[6])

        else:
            await message.reply('Эта пара уже добавлена вами, выберите другую!\n',
                                reply=False,
                                reply_markup=keyboard)

    elif message.text == '🔕Удалить пару':
        pass

    else:
        await message.reply('Не понял тебя, воспользуйся кнопками.',
                            reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_6)                                                       # PORTF PERCENT
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message)
        return None

    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    try:
        if int(message.text) > 0:
            try:
                insert_query = f"UPDATE users SET amount = {int(message.text)} WHERE amount = '12345'"
                curs.execute(insert_query)
                conn.commit()

            except (Exception, Error) as error:

                print("Ошибка при работе с PostgreSQL 4", error)
                curs.execute("rollback")

                insert_query = f"UPDATE users SET amount = {int(message.text)} WHERE amount = '12345'"
                curs.execute(insert_query)
                conn.commit()
            keyboard.add(*[types.KeyboardButton(name) for name in
                           ['🔔Добавить пару', '🔕Удалить пару', 'Мои пары', '🏠Меню']])
            await state.set_state(TestStates.all()[4])
            text = 'ура\n' \
                   'Выберите вариант' + str(message.chat.id)
            await message.reply(text,
                                reply=False,
                                reply_markup=keyboard)
            return None

    except ValueError:
        await message.reply('Введите число', reply=False)

    else:
        await message.reply('Не понял тебя, воспользуйся кнопками.',
                            reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_7)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('7!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_8)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('8!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_9)     # SOLO FUNC
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if '/' in message.text[1:]:
        str1 = message.text.upper()
        str1 = str1.split('/')
        price = await get_price_of_pair(str1[0] + str1[1])
        await bot.send_message(message.chat.id,
                               await print_price(price))

    elif 'pair' in message.text[:5]:
        price = await get_price_of_pair(message.text[5:].upper())
        await bot.send_message(message.chat.id,
                               await print_price(price))

    elif '+' in message.text:
        await bot.send_message(message.chat.id, await plus_func(message))

    elif message.text[0].isdigit():
        await bot.send_message(message.chat.id, await get_price_usdt(message))

    elif message.text == '🏠Меню':
        await menu(message)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['Гос. валюты', 'Криптовалюты', 'Уведомления']])
        await bot.send_message(message.chat.id,
                               'Не понял тебя, воспользуйся кнопками!', reply_markup=keyboard)
        await state.set_state(TestStates.all()[1])


@dp.message_handler(state=TestStates.TEST_STATE_0)                                                                 # GOS
async def first_test_state_case_met(message: types.Message):
    await menu(message)


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
