from email.policy import default
from tkwindow import ReminderWindow
import groupme_bot_config as config

window = ReminderWindow(config.BOT_ID, config.PHONE_NUMBERS, default_number_key=config.DEFAULT_NUMBER_KEY)