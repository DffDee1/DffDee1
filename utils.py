from aiogram.utils.helper import Helper, HelperMode, ListItem


class BotStates(Helper):
    mode = HelperMode.snake_case

    MENU = ListItem()
    FIRST_CHOICE = ListItem()
    CRYPTO_CHOICE = ListItem()
    GOS_CHOICE = ListItem()
    CRYPTO_POPULAR = ListItem()
    CRYPTO_PAIR = ListItem()
    NOTIF = ListItem()
    NOTIF_ADD = ListItem()
    NOTIF_PERCENT = ListItem()
    NOTIF_END = ListItem()
    NOTIF_DEL_PAIR = ListItem()
