from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, Updater
from database import load_user_data, save_user_data
import logging
import json

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_bot():
    dispatcher.add_handler(CommandHandler('start', handle_message))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('حسابي', handle_account_info))
    dispatcher.add_handler(CommandHandler('اقتراح', suggestion))
    dispatcher.add_handler(CommandHandler('سحب', handle_withdraw))
    dispatcher.add_handler(CommandHandler('إيداع', handle_deposit))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    init_db()
    start_bot()