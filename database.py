import sqlite3
from contextlib import closing
import random

DATABASE_FILE = "user_data.db"

def init_db():
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'العربية',
                balance REAL DEFAULT 0,
                account_number TEXT
            )
        ''')
        conn.commit()

generated_numbers = set()

import uuid
import time
import hashlib
import os

# تحميل الأرقام المولدة مسبقاً
def load_generated_numbers():
    if os.path.exists("generated_numbers.txt"):
        with open("generated_numbers.txt", "r") as file:
            return set(file.read().splitlines())
    return set()

generated_numbers = load_generated_numbers()

def save_generated_numbers():
    """حفظ الأرقام المولدة إلى ملف خارجي"""
    with open("generated_numbers.txt", "w") as file:
        file.write("\n".join(generated_numbers))

def generate_account_number(user_info):
    while True:
        # توليد UUID4
        unique_id = str(uuid.uuid4()).replace('-', '')[:8]  # أخذ أول 8 أحرف

        # إضافة الطابع الزمني
        timestamp = str(int(time.time()))  # الحصول على الطابع الزمني الحالي

        # دمج UUID والطابع الزمني
        account_number = unique_id + timestamp[-2:]  # استخدام آخر رقمين من الطابع الزمني

        # تشفير رقم الحساب مع معلومات المستخدم
        hash_object = hashlib.sha256((account_number + user_info).encode())
        final_account_number = str(int(hash_object.hexdigest(), 16))[:10]  # أخذ أول 10 أرقام من الهاش
        
        # التحقق من عدم وجود الرقم في الأرقام المولدة مسبقاً
        if final_account_number not in generated_numbers:
            formatted_account_number = f"LoL-{final_account_number}"  # إضافة بادئة LoL
            generated_numbers.add(formatted_account_number)
            save_generated_numbers()  # حفظ الرقم الجديد
            return formatted_account_number

def save_user_data(user_id, language, balance, account_number):
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, language, balance, account_number)
            VALUES (?, ?, ?, ?)
        ''', (user_id, language, balance, account_number))
        conn.commit()

def load_user_data(user_id):
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language, balance, account_number FROM users WHERE user_id = ?', (user_id,))
        data = cursor.fetchone()
    if data:
        return data
    else:
        account_number = generate_account_number()
        save_user_data(user_id, 'العربية', 0, account_number)
        return 'العربية', 0, account_number