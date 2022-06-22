import requests


async def get_price_of_pair(pair: str):
    pair = pair.upper()
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=' + pair
    response = requests.get(url)
    json_get = response.json()
    return json_get


async def check_pair(pair: str):
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=' + pair
    response = requests.get(url)
    if response.status_code == 200:
        return True
    else:
        return False


async def del_null(a):
    a = str(a)
    a = float(a)
    if a % 1 == 0:
        a = int(a)
    return a


async def print_price(json_get):
    pair = json_get['symbol']
    if 'USD' in pair:
        if 'USD' in pair[:4]:
            pair = pair[:4] + '/' + pair[4:]
    else:
        pair = pair[:3] + '/' + pair[3:]

    if 'BTC' in pair[2:]:
        text = 'Пара - ' + pair + '\nКурс - ' + json_get['price']
    else:
        x = round(float(json_get['price']), 2)
        x = str(x)
        text = 'Пара - ' + pair + '\nКурс - ' + x
    return text


async def get_price_usdt(message):
    # str1 = message.text.upper()
    str1 = message
    str1 = str1.split()

    if str1[1] != 'USDT':
        usdt = await get_price_of_pair(str1[1] + 'USDT')
        usdt = usdt['price']
        y = float(str1[0]) * float(usdt)
        rub = await get_price_of_pair('USDTRUB')
        rub = rub['price']
        rub_price = y * float(rub)
        seq = ''
        x = str(round(rub_price, 1))
        for i in range(len(x) + 3):
            seq += '='

        prnt = '🌐 ' + str1[0] + ' ' + str1[1] + ':\n' + seq \
               + '\n🇺🇸 ' + str(round(y, 2)) + '$\n🇷🇺 ' + str(round(rub_price, 1)) + '₽'
        return prnt

    else:
        rub = await get_price_of_pair('USDTRUB')
        rub = float(rub['price'])
        seq = ''
        x = str(round(rub, 1))
        for i in range(len(x) + 3):
            seq += '='

        prnt = '🌐 ' + str1[0] + ' ' + str1[1] + ':\n' + seq \
               + '\n🇷🇺 ' + str(round(rub, 1)) + '₽'
        return prnt


async def plus_func(message):
    str1 = message.text.upper()
    str1 = str1.split()
    usdt = await get_price_of_pair(str1[1] + 'USDT')
    usdt = usdt['price']
    y = float(str1[0]) * float(usdt)
    usdt2 = await get_price_of_pair(str1[4] + 'USDT')
    usdt2 = usdt2['price']
    y2 = float(str1[3]) * float(usdt2)
    x = y + y2
    rub = await get_price_of_pair('USDTRUB')
    rub = rub['price']
    rub_price = x * float(rub)

    prnt1 = '🇺🇸 ' + str1[0] + ' ' + str1[1] + ' = ' + str(y) + '$\n🇷🇺 ' + str1[3] + ' ' + str1[4] + ' = ' + \
            str(y2) + '$\n=====================\n🇺🇸 ' + str(round(x, 2)) + '$\n🇷🇺 ' + str(round(rub_price, 1)) + '₽'
    return prnt1
