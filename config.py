import os
flags = {'US': 'πΊπΈ', 'EU': 'πͺπΊ', 'RU': 'π·πΊ', 'AU': 'π¦πΊ', 'JP': 'π―π΅', 'CN': 'π¨π³',
         'GB': 'π¬π§', 'HK': 'π­π°', 'CA': 'π¨π¦', 'SG': 'πΈπ¬', 'KZ': 'π°πΏ', 'BY': 'π§πΎ'}

TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8080)
