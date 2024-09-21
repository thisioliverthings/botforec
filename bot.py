from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, Updater
from database import load_user_data, save_user_data, init_db
import logging
import json
import difflib

# إعداد نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, api_token: str):
        self.updater = Updater(api_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.help_texts = self.load_help_texts()
        self.known_commands = {'start', 'help', 'حسابي', 'اقتراح', 'سحب', 'إيداع', 'تغيير اللغة', 'تحويل'}
        self.setup_handlers()

    def load_help_texts(self):
        with open('help_text.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_handlers(self):
        self.dispatcher.add_handler(CommandHandler('start', self.handle_commands))
        self.dispatcher.add_handler(CommandHandler('help', self.handle_commands))
    
    def correct_command(self, update: Update, context: CallbackContext) -> None:
        message_text = update.message.text.strip().lower()
        if message_text in self.known_commands:
            update.message.reply_text(
                f"❌ يبدو أنك نسيت كتابة '/' قبل الأمر. جرب كتابة: <b>/{message_text}</b>.",
                parse_mode='HTML'
            )
        else:
            closest_matches = difflib.get_close_matches(message_text, self.known_commands, n=1, cutoff=0.6)
            if closest_matches:
                suggested_command = closest_matches[0]
                update.message.reply_text(
                    f"❌ لا يبدو أن الأمر <b>{message_text}</b> صحيح. هل كنت تقصد: <b>/{suggested_command}</b>؟",
                    parse_mode='HTML'
                )

    def handle_commands(self, update: Update, context: CallbackContext) -> None:
        command = update.message.text
    # معالجة الأوامر
        if command == '/start':
            update.message.reply_text('مرحبا بك في البوت!')
        elif command == '/help':
            update.message.reply_text('هذه هي قائمة الأوامر المتاحة.')
        elif command == 'حسابي':
            update.message.reply_text('هنا معلومات حسابك.')
        elif command == 'اقتراح':
            update.message.reply_text('أرسل اقتراحك.')
        elif command == 'سحب':
            update.message.reply_text('كم تريد سحبه؟')
        elif command == 'إيداع':
            update.message.reply_text('كم تريد إيداعه؟')
        else:
            update.message.reply_text('لم أتعرف على هذا الأمر.')
    def handle_account_info(self, update, language, balance, account_number):
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "غير متوفر"
        first_name = update.message.from_user.first_name or "غير متوفر"
        last_name = update.message.from_user.last_name or "غير متوفر"

        account_info = (
            "🌟 <b>معلومات حسابك</b> 🌟\n"
            f"👤 <b>اسم المستخدم:</b> {username}\n"
            f"🧑 <b>الاسم الأول:</b> {first_name}\n"
            f"👥 <b>اسم العائلة:</b> {last_name}\n"
            f"📅 <b>اللغة:</b> {language}\n"
            f"💰 <b>الرصيد:</b> {balance} ج.م\n"
            f"🔑 <b>رقم الحساب:</b> {account_number}\n"
            f"🆔 <b>معرف المستخدم:</b> {user_id}\n"
            "----------------------------------\n"
            "📩 <b>لأي استفسارات، لا تتردد في التواصل!</b>\n"
            "📈 <b>شكرًا لاستخدامك بوتنا!</b>\n"
            "🎉 <b>استمتع بتجربتك!</b>"
        )

        update.message.reply_text(account_info, parse_mode='HTML')

    def handle_transfer(self, update, command, user_id, language, balance, account_number):
        try:
            parts = command.split()
            amount = float(parts[1])
            recipient = int(parts[3])
            recipient_data = load_user_data(recipient)
            if recipient_data:
                recipient_balance = recipient_data[1]
                if amount <= balance:
                    balance -= amount
                    recipient_balance += amount
                    save_user_data(user_id, language, balance, account_number)
                    save_user_data(recipient, recipient_data[0], recipient_balance, recipient_data[2])
                    update.message.reply_text(f"➡️ تم تحويل <b>{amount}</b> إلى <b>{recipient}</b> بنجاح.", parse_mode='HTML')
                else:
                    update.message.reply_text("❌ رصيدك غير كافٍ لإجراء هذه العملية.")
            else:
                update.message.reply_text("❓ لم يتم العثور على المستخدم الذي تحاول التحويل إليه.")
        except (ValueError, IndexError):
            update.message.reply_text("❌ صيغة الأمر غير صحيحة. يجب أن تكتب: تحويل [المبلغ] إلى [معرف المستلم].")

    def handle_deposit(self, update, command, user_id, language, balance, account_number):
        try:
            amount = float(command.split()[1])
            if amount > 0:
                balance += amount
                save_user_data(user_id, language, balance, account_number)
                update.message.reply_text(f"💵 تم إيداع <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
            else:
                update.message.reply_text("❌ <b>خطأ:</b> يجب أن يكون المبلغ أكبر من صفر.", PARSE_MODE='HTML')
        except (ValueError, IndexError):
            update.message.reply_text(
                "❌ <b>خطأ:</b> صيغة الأمر غير صحيحة.\n"
                "يجب عليك كتابة الأمر كالتالي:\n"
                "<b>إيداع \"المبلغ\"</b>\n"
                "مثال: <code>إيداع 100</code> لإضافة 100 وحدة.",
                parse_mode='HTML'
            )

    def handle_withdraw(self, update, command, user_id, language, balance, account_number):
        try:
            amount = float(command.split()[1])
            if amount > 0 and amount <= balance:
                balance -= amount
                save_user_data(user_id, language, balance, account_number)
                update.message.reply_text(f"💸 تم سحب <b>{amount}</b> بنجاح. رصيدك المتبقي هو <b>{balance}</b>.", parse_mode='HTML')
            elif amount > balance:
                update.message.reply_text("❌ رصيدك غير كافٍ للسحب.")
            else:
                update.message.reply_text("❌ يجب أن يكون المبلغ أكبر من صفر.")
        except (ValueError, IndexError):
            update.message.reply_text(
                "❌ <b>خطأ:</b> صيغة الأمر غير صحيحة.\n"
                "يجب عليك كتابة الأمر كالتالي:\n"
                "<b>سحب \"المبلغ\"</b>\n"
                "مثال: <code>سحب 50</code> لسحب 50 وحدة.",
                parse_mode='HTML'
            )

# الفئة لمعالجة الأزرار
class ButtonHandler:
    def __init__(self, bot: TelegramBot):
        self.bot = bot

    def button(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()

        reply_markup_help = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')],
            [InlineKeyboardButton("❌ خروج", callback_data='confirm_exit')]
        ])

        # تعديل نص الرسالة بناءً على النصوص المحملة في بوت
        query.edit_message_text(
            text=self.bot.help_texts.get('main_menu', 'لم يتم العثور على نص المساعدة.'),
            reply_markup=reply_markup_help
        )
        
# بداية تشغيل البوت
if __name__ == '__main__':
    init_db()
    TOKEN = '8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0'  # ضع توكن البوت هنا
    bot = TelegramBot(TOKEN)
    bot.updater.start_polling()
    bot.updater.idle()