import os
import streamlit as st

def get_secret(key: str, default=None):
    # محاولة القراءة من st.secrets (بيئة النشر)
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    # الرجوع إلى متغيرات البيئة (بيئة التطوير)
    return os.getenv(key, default)

LEMONSQUEEZY_API_KEY = get_secret("LEMONSQUEEZY_API_KEY")
LEMONSQUEEZY_STORE_ID = get_secret("LEMONSQUEEZY_STORE_ID")
LEMONSQUEEZY_WEBHOOK_SECRET = get_secret("LEMONSQUEEZY_WEBHOOK_SECRET")
MONTHLY_VARIANT_ID = get_secret("MONTHLY_VARIANT_ID")

# رسائل تأكيد للتصحيح
if LEMONSQUEEZY_API_KEY:
    print(f"✅ Config loaded: API Key starts with {LEMONSQUEEZY_API_KEY[:8]}...")
else:
    print("❌ Config failed: LEMONSQUEEZY_API_KEY is missing!")
