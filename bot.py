import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from database import init_db
from handlers import handle_commands
from handlers import correct_command
import json
import difflib
API_TOKEN = "8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0" 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_bot():
    dispatcher = updater.dispatcher

    # معالجة الأوامر المعروفة
    dispatcher.add_handler(CommandHandler('start', handle_message))
    dispatcher.add_handler(CommandHandler('help', handle_message))
    dispatcher.add_handler(CommandHandler('حسابي', handle_message))
    dispatcher.add_handler(CommandHandler('اقتراح', handle_message))
    dispatcher.add_handler(CommandHandler('سحب', handle_message))
    dispatcher.add_handler(CommandHandler('إيداع', handle_message))

    # تصحيح الأخطاء الشائعة
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, correct_command))

updater.start_polling()
updater.idle()

if __name__ == '__main__':
    init_db()
    start_bot()