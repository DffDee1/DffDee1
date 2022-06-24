import requests
import xmltodict
import json
from fuzzywuzzy import fuzz
from config import flags

url_act = 'https://cbr.ru/scripts/XML_daily.asp?date_req='
file_actual = 'actual_values.json'


async def get_pop_vals_cb():
    response = requests.get(url_act)
    datas = xmltodict.parse(response.content)
    json.dumps(datas, ensure_ascii=False)
    mas = []
    for i in datas['ValCurs']['Valute']:
        if i['CharCode'] in ['USD', 'EUR', 'BYN', 'KZT', 'CNY', 'JPY']:
            try:
                mas.append([flags[i['CharCode'][:2]] + i['Name'], i['Value'], i['Nominal']])
            except KeyError:
                mas.append([i['Name'], i['Value'], i['Nominal']])

    return mas


async def get_value_cb(mess):
    response = requests.get(url_act)
    datas = xmltodict.parse(response.content)
    json.dumps(datas, ensure_ascii=False)
    mas = []
    for i in datas['ValCurs']['Valute']:
        if mess in ['ен', 'ена', 'йен', 'йена']:
            mess = 'иен'

        if fuzz.WRatio(mess, i['Name']) >= 80 or mess.upper() == i['CharCode']:
            try:
                mas.append([flags[i['CharCode'][:2]] + i['Name'], i['Value'], i['Nominal']])
            except KeyError:
                mas.append([i['Name'], i['Value'], i['Nominal']])

    return mas
