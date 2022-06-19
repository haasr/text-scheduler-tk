from tkwindow import ReminderWindow
import config
#import config_private as config

THEMES = {
    'light': 'plastik',
    'dark': 'black'
}

window = ReminderWindow(config.BOT_ID, THEMES[config.THEME], config.PHONE_NUMBERS,
                        default_number_key=config.DEFAULT_NUMBER_KEY)