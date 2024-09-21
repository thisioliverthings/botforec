from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import load_user_data, save_user_data
import logging
import json
import difflib

# إعداد نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل النصوص من ملف JSON
with open('help_text.json', 'r', encoding='utf-8') as f:
    help_texts = json.load(f)




# قائمة الأوامر المعروفة
KNOWN_COMMANDS = {'start', 'help', 'حسابي', 'اقتراح', 'سحب', 'إيداع'}

def correct_command(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.strip().lower()  # إزالة المسافات والتعامل مع الأحرف الصغيرة

    if message_text in KNOWN_COMMANDS:
        update.message.reply_text(
            f"❌ يبدو أنك نسيت كتابة '/' قبل الأمر. جرب كتابة: <b>/{message_text}</b>.",
            parse_mode='HTML'
        )
    else:
        # محاولة إيجاد أمر قريب من النص المدخل باستخدام difflib
        closest_matches = difflib.get_close_matches(message_text, KNOWN_COMMANDS, n=1, cutoff=0.6)

        if closest_matches:
            suggested_command = closest_matches[0]
            update.message.reply_text(
                f"❌ لا يبدو أن الأمر <b>{message_text}</b> صحيح. هل كنت تقصد: <b>/{suggested_command}</b>؟",
                parse_mode='HTML'
            )
        else:
            # تجاهل الأوامر غير المعروفة
            pass


def handle_message(update: Update, context: CallbackContext) -> None:
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



def suggestion(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    suggestion_text = ' '.join(context.args)

    if suggestion_text:
        context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"اقتراح من المستخدم {user_id}: {suggestion_text}")
        update.message.reply_text("✅ تم إرسال اقتراحك بنجاح.")
    else:
        update.message.reply_text("❌ يرجى كتابة اقتراحك بعد الأمر.")

def help_command(update: Update, context: CallbackContext) -> None:
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


def load_help_texts():
    with open('help_text.json', 'r', encoding='utf-8') as f:
        return json.load(f)

help_texts = load_help_texts()

def button (update:Update,context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  # تأكد من إضافة هذه السطر

    reply_markup_help = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')],
        [InlineKeyboardButton("❌ خروج", callback_data='confirm_exit')],
        [InlineKeyboardButton("ℹ️ معلومات عن البوت", callback_data='bot_info')],
        [InlineKeyboardButton("📜 بنود الخدمة", callback_data='terms_and_privacy')]
    ])

    if query.data in help_texts:
        query.edit_message_text(text=help_texts[query.data], parse_mode='HTML', reply_markup=reply_markup_help)
    elif query.data == 'help_menu':
        reply_markup_menu = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 الأوامر الأساسية", callback_data='help_section_1')],
            [InlineKeyboardButton("📊 نظام النقاط والمحفظة", callback_data='help_section_2')],
            [InlineKeyboardButton("🌐 إدارة اللغة", callback_data='help_section_3')],
            [InlineKeyboardButton("💼 العضويات والاشتراكات", callback_data='help_section_4')],
            [InlineKeyboardButton("🎁 عروض ومكافآت خاصة", callback_data='help_section_5')],
            [InlineKeyboardButton("❌ خروج", callback_data='confirm_exit')]
        ])
        query.edit_message_text(text="📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup_menu)


def handle_commands(update: Update, context: CallbackContext) -> None:
    command = update.message.text.strip()
    user_id = update.message.from_user.id
    language, balance, account_number = load_user_data(user_id)

    try:
        if command == '/start':
            handle_start(update, context)
        elif command.lower() in ['help', 'help/', '/help', 'مساعدة', 'مساعده']:
            help_command(update, context)
        elif command == 'حسابي':
            handle_account_info(update, language, balance, account_number)
        elif command.startswith('اقتراح'):
            suggestion(update, context)
        else:
            update.message.reply_text("❌ الأمر غير معروف. حاول مرة أخرى.")
    except Exception as e:
        logger.error(f"Error handling command: {e}")
        update.message.reply_text("❌ حدث خطأ أثناء معالجة الأمر. يرجى المحاولة لاحقًا.")

def handle_start(update, context):
    handle_message(update, context)

def handle_account_info(update: Update, language, balance, account_number):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "غير متوفر"
    first_name = update.message.from_user.first_name or "غير متوفر"
    last_name = update.message.from_user.last_name or "غير متوفر"

    user_joined_date = update.message.date.strftime("%Y-%m-%d")
    user_last_active = update.message.date.strftime("%Y-%m-%d %H:%M:%S")
    account_status = "نشط" if balance > 0 else "غير نشط"
    total_transactions = 5
    last_transaction_date = "2024-09-20"

    account_info = (
        "🌟 <b>معلومات حسابك</b> 🌟\n"
        f"👤 <b>اسم المستخدم:</b> {username}\n"
        f"🧑 <b>الاسم الأول:</b> {first_name}\n"
        f"👥 <b>اسم العائلة:</b> {last_name}\n"
        f"📅 <b>اللغة:</b> {language}\n"
        f"💰 <b>الرصيد:</b> {balance} ج.م\n"
        f"🔑 <b>رقم الحساب:</b> {account_number}\n"
        f"🆔 <b>معرف المستخدم:</b> {user_id}\n"
        f"📅 <b>تاريخ الانضمام:</b> {user_joined_date}\n"
        f"🕒 <b>آخر نشاط:</b> {user_last_active}\n"
        f"⚖️ <b>حالة الحساب:</b> {account_status}\n"
        f"🔄 <b>عدد المعاملات:</b> {total_transactions}\n"
        f"📅 <b>تاريخ آخر معاملة:</b> {last_transaction_date}\n"
        "----------------------------------\n"
        "📩 <b>لأي استفسارات، لا تتردد في التواصل!</b>\n"
        "📈 <b>شكرًا لاستخدامك بوتنا!</b>\n"
        "🎉 <b>استمتع بتجربتك!</b>"
    )

    update.message.reply_text(account_info, parse_mode='HTML')

def handle_deposit(update, command, user_id, language, balance, account_number):
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

def handle_transfer(update, command, user_id, language, balance, account_number):
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

def handle_balance(update, balance):
    update.message.reply_text(f"💰 رصيدك الحالي هو: <b>{balance}</b>.", parse_mode='HTML')
def handle_change_language(update):
    # ملاحظة: هنا يمكنك إضافة خيارات للغة الجديدة من خلال الأزرار
    update.message.reply_text("⚙️ يرجى تحديد اللغة الجديدة باستخدام الأزرار.")

def handle_settings(update):
    update.message.reply_text("🛠️ هنا يمكنك ضبط إعداداتك.")

def handle_withdraw(update, command, user_id, language, balance, account_number):
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

def handle_transfer(update, command, user_id, language, balance, account_number):
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


def handle_balance(update, balance):
    update.message.reply_text(f"💰 رصيدك الحالي هو: <b>{balance}</b>.", parse_mode='HTML')

# إضافة المزيد من الوظائف مثل handle_deposit