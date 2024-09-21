import logging
# إعداد تسجيل الأحداث
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # تسجيل السجلات في ملف
        logging.StreamHandler()            # طباعة السجلات في الطرفية
    ]
)

logger = logging.getLogger(__name__)

# مثال على كيفية استخدامه
logger.info("تم تفعيل البوت بنجاح!")
logger.warning("تحذير: هناك شيء غير معتاد!")
logger.error("خطأ: حدث خطأ!")
