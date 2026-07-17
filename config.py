import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env (إذا كان موجوداً)
load_dotenv()

def get_secret(key: str, default=None):
    """
    محاولة قراءة المفتاح من:
    1. st.secrets (إذا كان متاحاً)
    2. os.getenv (من متغيرات البيئة أو ملف .env)
    3. default (قيمة افتراضية)
    """
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

LEMONSQUEEZY_API_KEY = get_secret("LEMONSQUEEZY_API_KEY")
LEMONSQUEEZY_STORE_ID = get_secret("LEMONSQUEEZY_STORE_ID")
LEMONSQUEEZY_WEBHOOK_SECRET = get_secret("LEMONSQUEEZY_WEBHOOK_SECRET")
MONTHLY_VARIANT_ID = get_secret("MONTHLY_VARIANT_ID", "YOUR_VARIANT_ID")

# اختياري: طباعة رسالة تأكيد دون عرض المفاتيح (للتأكد من القراءة)
if LEMONSQUEEZY_API_KEY:
    print("✅ تم تحميل مفاتيح Lemon Squeezy بنجاح")
else:
    print("⚠️ مفاتيح Lemon Squeezy غير موجودة (تأكد من ملف .env أو متغيرات البيئة)")
