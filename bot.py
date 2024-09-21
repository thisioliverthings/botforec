import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from database import init_db
from handlers import handle_commands, correct_command, button
import json
 
# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_bot():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', handle_commands))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_commands))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    init_db()
    start_bot()
    
    
    
    
    
    
    import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from database import init_db
from handlers import handle_commands, correct_command
import json
import difflib

API_TOKEN = "8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0" 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_bot():
    updater = Updater(API_TOKEN, use_context=True)
    
    # معالجة الأوامر المعروفة
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_commands))
    dispatcher.add_handler(CommandHandler('help', handle_commands))
    dispatcher.add_handler(CommandHandler('/حسابي', handle_commands))
    dispatcher.add_handler(CommandHandler('/اقتراح', handle_commands))
    dispatcher.add_handler(CommandHandler('/سحب', handle_commands))
    dispatcher.add_handler(CommandHandler('/إيداع', handle_commands))
    # تصحيح الأخطاء الشائعة
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, correct_command))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    init_db()
    start_bot()