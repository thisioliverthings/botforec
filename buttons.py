from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_help_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data='help_menu')],
        [InlineKeyboardButton("❌ خروج", callback_data='confirm_exit')],
        [InlineKeyboardButton("ℹ️ معلومات عن البوت", callback_data='bot_info')],
        [InlineKeyboardButton("📜 بنود الخدمة", callback_data='terms_and_privacy')]
    ])

def create_menu_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 الأوامر الأساسية", callback_data='help_section_1')],
        [InlineKeyboardButton("📊 نظام النقاط والمحفظة", callback_data='help_section_2')],
        [InlineKeyboardButton("🌐 إدارة اللغة", callback_data='help_section_3')],
        [InlineKeyboardButton("💼 العضويات والاشتراكات", callback_data='help_section_4')],
        [InlineKeyboardButton("🎁 عروض ومكافآت خاصة", callback_data='help_section_5')],
        [InlineKeyboardButton("❌ خروج", callback_data='confirm_exit')]
    ])