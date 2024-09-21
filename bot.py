from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, Updater, MessageHandler, Filters
from database import load_user_data, save_user_data, init_db
import logging
import json
import difflib

# إعداد الـ Token الخاص بالبوت
API_TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'

KNOWN_COMMANDS = {'start', 'help', 'حسابي', 'اقتراح', 'سحب', 'إيداع'}

def correct_command(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.strip().lower()

    if message_text in KNOWN_COMMANDS:
        update.message.reply_text(
            f"❌ يبدو أنك نسيت كتابة '/' قبل الأمر. جرب كتابة: <b>/{message_text}</b>.",
            parse_mode='HTML'
        )
    else:
        closest_matches = difflib.get_close_matches(message_text, KNOWN_COMMANDS, n=1, cutoff=0.6)
        if closest_matches:
            suggested_command = closest_matches[0]
            update.message.reply_text(
                f"❌ لا يبدو أن الأمر <b>{message_text}</b> صحيح. هل كنت تقصد: <b>/{suggested_command}</b>؟",
                parse_mode='HTML'
            )

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_bot():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('help', help_command))  # تأكد من وجود دالة help_command
    dispatcher.add_handler(CommandHandler('حسابي', handle_account_info))  # تأكد من وجود دالة handle_account_info
    dispatcher.add_handler(CommandHandler('اقتراح', suggestion))  # تأكد من وجود دالة suggestion
    dispatcher.add_handler(CommandHandler('سحب', handle_withdraw))  # تأكد من وجود دالة handle_withdraw
    dispatcher.add_handler(CommandHandler('إيداع', handle_deposit))  # تأكد من وجود دالة handle_deposit
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, correct_command))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    init_db()
    start_bot()