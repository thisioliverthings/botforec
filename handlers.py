from telegram import Update
from telegram.ext import CallbackContext
from database import load_user_data, save_user_data
import logging
from buttons import create_menu_buttons, create_help_buttons

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    language, balance, account_number = load_user_data(user_id)

    welcome_message = (
        "🎉 مرحبًا بك في بوت المرح والأموال! 💰\n\n"
        "هنا حيث يجتمع الترفيه والإثارة مع إدارة أموالك.\n"
        "✨ استعد لمغامرات ممتعة وتحديات مثيرة!\n\n"
        "للبدء، استخدم الأمر 'help' لتتعرف على جميع المزايا المتاحة لك.\n"
        "لا تنسَ التحقق من رصيدك وتحديث معلومات حسابك بانتظام!"
    )

    context.bot.send_message(chat_id=update.message.chat_id, text=welcome_message)

def suggestion(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    suggestion_text = ' '.join(context.args)

    if suggestion_text:
        context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"اقتراح من المستخدم {user_id}: {suggestion_text}")
        update.message.reply_text("✅ تم إرسال اقتراحك بنجاح.")
    else:
        update.message.reply_text("❌ يرجى كتابة اقتراحك بعد الأمر.")
#دالة الاوامر1 (الاساسيه)

#2 دالة الاوامر
# def help_command(update: Update, context: CallbackContext) -> None:
#     keyboard = [
#         [InlineKeyboardButton("✨ القسم 1: الأوامر الأساسية", callback_data='help_section_1')],
#         [InlineKeyboardButton("💰 القسم 2: نظام النقاط", callback_data='help_section_2')],
#         [InlineKeyboardButton("🌍 القسم 3: إدارة اللغة", callback_data='help_section_3')],
#         [InlineKeyboardButton("🎟️ القسم 4: العضويات", callback_data='help_section_4')],
#         [InlineKeyboardButton("🎁 القسم 5: العروض والمكافآت", callback_data='help_section_5')],
#         [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     if update.callback_query:
#         query = update.callback_query
#         query.message.reply_text("📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup)



# تحميل النصوص من ملف JSON
with open('help_text.json', 'r', encoding='utf-8') as f:
    help_texts = json.load(f)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    if query.data in help_texts:
        query.edit_message_text(text=help_texts[query.data], parse_mode='HTML', reply_markup=create_help_buttons())
    elif query.data == 'help_menu':
        reply_markup_menu = create_menu_buttons()
        query.edit_message_text(text="📚 مرحبًا! اختر قسمًا لعرض الشرح:", reply_markup=reply_markup_menu)
    elif query.data == 'confirm_exit':
        reply_markup_confirm = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ نعم، الخروج", callback_data='exit_help')],
            [InlineKeyboardButton("🔙 لا، العودة", callback_data='help_menu')]
        ])
        query.edit_message_text(text="⚠️ هل أنت متأكد أنك تريد الخروج؟", reply_markup=reply_markup_confirm)
    elif query.data == 'exit_help':
        query.edit_message_text(text="✅ تم الخروج من قائمة المساعدة. إذا كنت بحاجة إلى مساعدة أخرى، اكتب 'help'.", reply_markup=None)


# دالة لمعالجة الأوامر المدخلة من المستخدم
def handle_commands(update: Update, context: CallbackContext) -> None:
    command = update.message.text.strip()  # إزالة المسافات الزائدة من نص الأمر
    user_id = update.message.from_user.id  # معرف المستخدم
    language, balance, account_number = load_user_data(user_id)  # تحميل بيانات المستخدم

    try:
        # التعامل مع الأوامر المختلفة
        if command == '/start':
            handle_start(update, context)  # بدء التفاعل
        elif command.lower() in ['help', 'help/', '/help', 'مساعدة', 'مساعده']:
            handle_help(update, context)  # عرض المساعدة
        elif command == 'حسابي':
            handle_account_info(update, language, balance, account_number)  # عرض معلومات الحساب
        elif command.startswith('اقتراح'):
            suggestion(update, context)  # استدعاء دالة الاقتراحات
        else:
            update.message.reply_text("❌ الأمر غير معروف. حاول مرة أخرى.")  # رسالة للأوامر غير المعروفة
    except Exception:
        update.message.reply_text("❌ حدث خطأ أثناء معالجة الأمر")

def handle_command(update: Update, context: CallbackContext) -> None:
    command = update.message.text.split()[0].lower()  # تحديد الأمر المدخل

    try:
        if command == 'اقتراح':
            suggestion(update, context)  # استدعاء دالة الاقتراحات
        elif command == 'تغيير اللغة':
            handle_change_language(update)  # تغيير اللغة
        elif command == 'settings':
            handle_settings(update)  # إعدادات المستخدم
        elif command == 'info':
            handle_info(update)  # معلومات عن البوت
        elif command.startswith('إيداع'):
            handle_deposit(update, command, user_id, language, balance, account_number)  # إيداع الأموال
        elif command.startswith('سحب'):
            handle_withdraw(update, command, user_id, language, balance, account_number)  # سحب الأموال
        elif command.startswith('تحويل'):
            handle_transfer(update, command, user_id, language, balance, account_number)  # تحويل الأموال
        elif command == 'رصيدي':
            handle_balance(update, balance)  # عرض الرصيد
        else:
            update.message.reply_text("❌ الأمر غير معروف. حاول مرة أخرى.")  # رسالة افتراضية للأوامر غير المعروفة
    except Exception as e:
        logger.error(f"Error handling command: {e}")  # تسجيل أي أخطاء تظهر

def handle_start(update, context):
    handle_message(update, context)

def handle_help(update, context):
    # نص المساعدة المبدئي
    help_text = (
        "📚 <b>قائمة الأوامر:</b>\n"
        "للحصول على تفاصيل حول أي قسم، اضغط على الزر أدناه."
    )
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📜 الأوامر الأساسية", callback_data='help_section_1'),
            InlineKeyboardButton("📊 نظام النقاط والمحفظة", callback_data='help_section_2')
        ],
        [
            InlineKeyboardButton("🌐 إدارة اللغة", callback_data='help_section_3'),
            InlineKeyboardButton("💼 العضويات والاشتراكات", callback_data='help_section_4')
        ],
        [
            InlineKeyboardButton("🎁 عروض ومكافآت خاصة", callback_data='help_section_5'),
            InlineKeyboardButton("🔙 إغلاق", callback_data='close_help')
        ]
    ])
    update.message.reply_text(text=help_text, parse_mode='HTML', reply_markup=reply_markup)

def handle_account_info(update: Update, language, balance, account_number):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "غير متوفر"
    first_name = update.message.from_user.first_name or "غير متوفر"
    last_name = update.message.from_user.last_name or "غير متوفر"
    
    # معلومات إضافية
    user_joined_date = update.message.date.strftime("%Y-%m-%d")  # تاريخ الانضمام
    user_last_active = update.message.date.strftime("%Y-%m-%d %H:%M:%S")  # آخر نشاط
    account_status = "نشط" if balance > 0 else "غير نشط"  # حالة الحساب
    total_transactions = 5  # مثال: عدد المعاملات
    last_transaction_date = "2024-09-20"  # مثال: تاريخ آخر معاملة
    
    # نص الرسالة مع تحسينات
    account_info = (
        "🌟 **معلومات حسابك** 🌟\n"
        f"👤 **اسم المستخدم:** {username}\n"
        f"🧑 **الاسم الأول:** {first_name}\n"
        f"👥 **اسم العائلة:** {last_name}\n"
        f"📅 **اللغة:** {language}\n"
        f"💰 **الرصيد:** {balance} ج.م\n"
        f"🔑 **رقم الحساب:** {account_number}\n"
        f"🆔 **معرف المستخدم:** {user_id}\n"
        f"📅 **تاريخ الانضمام:** {user_joined_date}\n"
        f"🕒 **آخر نشاط:** {user_last_active}\n"
        f"⚖️ **حالة الحساب:** {account_status}\n"
        f"🔄 **عدد المعاملات:** {total_transactions}\n"
        f"📅 **تاريخ آخر معاملة:** {last_transaction_date}\n"
        "----------------------------------\n"
        "📩 **لأي استفسارات، لا تتردد في التواصل!**\n"
        "📈 **شكرًا لاستخدامك بوتنا!**\n"
        "🎉 **استمتع بتجربتك!**"
    )
    
    # إرسال الرسالة
    update.message.reply_text(account_info, parse_mode='HTML')

    # إضافة خيارات للتفاعل (مثل زر)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("إدارة الحساب", callback_data='manage_account')],
        [InlineKeyboardButton("عرض المعاملات", callback_data='view_transactions')]
    ])
    update.message.reply_text("💼 **اختر ما تريد القيام به:**", reply_markup=reply_markup)

def handle_change_language(update):
    update.message.reply_text("⚙️ يرجى تحديد اللغة الجديدة.")

def handle_settings(update):
    update.message.reply_text("🛠️ هنا يمكنك ضبط إعداداتك.")

def handle_deposit(update, command, user_id, language, balance, account_number):
    try:
        amount = float(command.split()[1])
        if amount > 0:
            balance += amount
            save_user_data(user_id, language, balance, account_number)
            update.message.reply_text(f"💵 تم إيداع <b>{amount}</b> بنجاح. رصيدك الجديد هو <b>{balance}</b>.", parse_mode='HTML')
        else:
            update.message.reply_text(
    "❌ <b>خطأ:</b> يجب أن يكون المبلغ أكبر من صفر.",
    parse_mode='HTML')
    except (ValueError, IndexError):
        update.message.reply_text(
    "❌ <b>خطأ:</b> صيغة الأمر غير صحيحة.\n"
    "يجب عليك كتابة الأمر كالتالي:\n"
    "<b>إيداع \"المبلغ\"</b>\n"
    "مثال: <code>إيداع 100</code> لإضافة 100 وحدة.",
    parse_mode='HTML')

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