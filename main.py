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
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

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


async def menu(message, state):
    if state is not None:
        await state.set_state(TestStates.all()[1])

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in
                   ['Гос. валюты', 'Криптовалюты', 'Уведомления']])
    await bot.send_message(message.chat.id,
                     text="Вы вернулись в меню)",
                     reply_markup=keyboard)


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
        await menu(message, state)

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


@dp.message_handler(state=TestStates.TEST_STATE_1)      # FIRST CHOICE
async def first_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Гос. валюты':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['Указать валюту', 'Выбрать валюту', '🏠Меню']])
        await state.set_state(TestStates.all()[2])
        await message.reply('Выберите вариант!',
                            reply=False,
                            reply_markup=keyboard)

    elif message.text == 'Криптовалюты':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['⌨Ввести свою пару', '📊Популярные пары', '🏠Меню']])
        await state.set_state(TestStates.all()[3])
        await message.reply('Выберите вариант',
                            reply=False,
                            reply_markup=keyboard)

    elif message.text == '🔔Уведомления':
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['🔔Добавить пару', '🔕Удалить пару', '🏠Меню']])
        await state.set_state(TestStates.all()[5])
        await message.reply('Выберите вариант',
                            reply=False,
                            reply_markup=keyboard)


@dp.message_handler(state=TestStates.TEST_STATE_2)      # CRYPTO
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message, None)
        return None

    state = dp.current_state(user=message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == '⌨Ввести свою пару':
        await menu(message, None)
        keyboard = await menu_add()
        await message.reply('Введите пару в формате "coin/coin"'
                            '\nНапример "btc/rub" без кавычек!',
                            reply=False,
                            reply_markup=keyboard)

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


@dp.message_handler(state=TestStates.TEST_STATE_3)      # CRYPTO CHOICE
async def second_test_state_case_met(message: types.Message):
    if message.text == '🏠Меню':
        await menu(message, None)
        return None

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


@dp.message_handler(state=TestStates.TEST_STATE_4)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('4!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_5)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('5!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_6)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('6!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_7)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('7!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_8)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('8!', reply=False)


@dp.message_handler(state=TestStates.TEST_STATE_9)
async def second_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.reply('9!', reply=False)


@dp.message_handler(content_types=['text'])
def solo_funcs(message):
    if '/' in message.text[1:]:
        str1 = message.text.upper()
        str1 = str1.split('/')
        bot.send_message(message.chat.id,
                         await print_price(get_price_of_pair(str1[0] + str1[1])))

    elif 'pair' in message.text[:5]:
        bot.send_message(message.chat.id,
                         await print_price(get_price_of_pair(message.text[5:].upper())))

    elif '+' in message.text:
        bot.send_message(message.chat.id, await plus_func(message))

    elif message.text[0].isdigit():
        bot.send_message(message.chat.id, await get_price_usdt(message))

    elif message.text == '🏠Меню':
        menu(message, None)

    else:
        state = dp.current_state(user=message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['Гос. валюты', 'Криптовалюты', 'Уведомления']])
        bot.send_message(message.chat.id,
                         'Не понял тебя, воспользуйся кнопками!', reply_markup=keyboard)
        await state.set_state(TestStates.all()[1])


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
