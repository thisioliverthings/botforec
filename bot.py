from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, Updater
from database import load_user_data, save_user_data
import logging
import json

# إعداد نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل النصوص من ملف JSON
with open('help_text.json', 'r', encoding='utf-8') as f:
    help_texts = json.load(f)

OWNER_CHAT_ID = '7161132306'  # ضع هنا معرف الدردشة الخاص بك

class TraderBot:
    def __init__(self):
        self.language = None
        self.balance = 0
        self.account_number = None

    def handle_message(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        username = update.effective_user.username or "غير متوفر"
        welcome_message = (
            f"<b>🎉 مرحبًا بك، {username}! في بوت 𝗟𝗼𝗹𝗶 𝗧𝗿𝗮𝗱𝗲𝗿𝗕𝗼𝘁! 💰</b>\n\n"
            "<b>✨ هنا حيث يجتمع الترفيه والإثارة مع إدارة أموالك.</b>\n"
            "<b>🌟 استعد لمغامرات ممتعة وتحديات مثيرة!</b>\n\n"
            "<b>📜 لبدء رحلتك، استخدم الأمر <code>help</code> لتتعرف على جميع المزايا المتاحة لك.</b>\n"
            "<b>💡 نحن هنا لجعل تجربتك مميزة وممتعة!</b>"
        )
        context.bot.send_message(chat_id=update.message.chat_id, text=welcome_message, parse_mode='HTML')

    def suggestion(self, update: Update, context: CallbackContext) -> None:
        user_id = update.message.from_user.id
        suggestion_text = ' '.join(context.args)

        if suggestion_text:
            context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"اقتراح من المستخدم {user_id}: {suggestion_text}")
            update.message.reply_text("✅ تم إرسال اقتراحك بنجاح.")
        else:
            update.message.reply_text("❌ يرجى كتابة اقتراحك بعد الأمر.")

    def help_command(self, update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("📜 الأوامر الأساسية", callback_data='help_section_1')],
            [InlineKeyboardButton("💰 نظام النقاط", callback_data='help_section_2')],
            [InlineKeyboardButton("🌍 إدارة اللغة", callback_data='help_section_3')],
            [InlineKeyboardButton("🎟️ العضويات", callback_data='help_section_4')],
            [InlineKeyboardButton("🎁 العروض والمكافآت", callback_data='help_section_5')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup)

    def button(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query

        if query.data in help_texts:
            query.edit_message_text(text=help_texts[query.data], parse_mode='HTML', reply_markup=self.create_help_buttons())
        elif query.data == 'help_menu':
            reply_markup_menu = self.create_menu_buttons()
            query.edit_message_text(text="📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup_menu)
        elif query.data == 'confirm_exit':
            reply_markup_confirm = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ نعم، الخروج", callback_data='exit_help')],
                [InlineKeyboardButton("🔙 لا، العودة", callback_data='help_menu')]
            ])
            query.edit_message_text(text="⚠️ هل أنت متأكد أنك تريد الخروج؟", reply_markup=reply_markup_confirm)
        elif query.data == 'exit_help':
            query.edit_message_text(text="✅ تم الخروج من قائمة المساعدة. إذا كنت بحاجة إلى مساعدة أخرى، اكتب 'help'.", reply_markup=None)

    def handle_start(self, update: Update, context: CallbackContext) -> None:
        self.handle_message(update, context)

    def handle_account_info(self, update: Update) -> None:
        user_id = update.message.from_user.id
        language, balance, account_number = load_user_data(user_id)

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

    def handle_deposit(self, update: Update, command: str) -> None:
        user_id = update.message.from_user.id
        language, balance, account_number = load_user_data(user_id)

        try:
            amount = float(command.split()[1])
            if amount > 0:
                balance += amount
                save_user_data(user_id, language, balance, account_number)
                update.message.reply_text(f"💵 تم إيداع <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
            else:
                update.message.reply_text("❌ <b>خطأ:</b> يجب أن يكون المبلغ أكبر من صفر.", parse_mode='HTML')
        except (ValueError, IndexError):
            update.message.reply_text(
                "❌ <b>خطأ:</b> صيغة الأمر غير صحيحة.\n"
                "يجب عليك كتابة الأمر كالتالي:\n"
                "<b>إيداع \"المبلغ\"</b>\n"
                "مثال: <code>إيداع 100</code> لإضافة 100 وحدة.",
                parse_mode='HTML'
            )

    def handle_withdraw(self, update: Update, command: str) -> None:
        user_id = update.message.from_user.id
        language, balance, account_number = load_user_data(user_id)

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

    def handle_transfer(self, update: Update, command: str) -> None:
        user_id = update.message.from_user.id
        language, balance, account_number = load_user_data(user_id)

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

    def handle_balance(self, update: Update) -> None:
        user_id = update.message.from_user.id
        language, balance, account_number = load_user_data(user_id)
        update.message.reply_text(f"💰 رصيدك الحالي هو: <b>{balance}</b>.", parse_mode='HTML')

    def handle_commands(self, update: Update, context: CallbackContext) -> None:
        command = update.message.text.strip()
        user_id = update.message.from_user.id

    # الأوامر المعروفة
        known_commands = ['/start', '/help', 'حسابي', 'اقتراح', 'إيداع', 'سحب', 'تحويل', 'رصيدي']

        if command in known_commands:
            try:
                language, balance, account_number = load_user_data(user_id)

                if command == '/start':
                    self.handle_start(update, context)
                elif command.lower() in ['/help', 'مساعدة']:
                    self.help_command(update, context)
                elif command == 'حسابي':
                    self.handle_account_info(update)
                elif command.startswith('اقتراح'):
                    self.suggestion(update, context)
                elif command.startswith('إيداع'):
                    self.handle_deposit(update, command)
                elif command.startswith('سحب'):
                    self.handle_withdraw(update, command)
                elif command.startswith('تحويل'):
                    self.handle_transfer(update, command)
                elif command == 'رصيدي':
                    self.handle_balance(update)

            except Exception as e:
                logger.error(f"Error handling command: {e}")
                update.message.reply_text("❌ حدث خطأ أثناء معالجة الأمر. يرجى المحاولة لاحقًا.")
        else:
        # لا تفعل شيئًا إذا لم يكن الأمر معروفًا
            pass

    def run(self) -> None:
        updater = Updater("8119443898:AAFwm5E368v-Ov-M_XGBQYCJxj1vMDQbv-0", use_context=True)

        dp = updater.dispatcher
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_commands))
        dp.add_handler(CommandHandler('start', self.handle_start))
        dp.add_handler(CommandHandler('help', self.help_command))
      

        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    bot = TraderBot()
    bot.run()