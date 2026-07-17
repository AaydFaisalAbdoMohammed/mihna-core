import streamlit as st
import os

def get_secret(key: str, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

LEMONSQUEEZY_API_KEY = get_secret("LEMONSQUEEZY_API_KEY")
LEMONSQUEEZY_STORE_ID = get_secret("LEMONSQUEEZY_STORE_ID")
LEMONSQUEEZY_WEBHOOK_SECRET = get_secret("LEMONSQUEEZY_WEBHOOK_SECRET")
MONTHLY_VARIANT_ID = get_secret("MONTHLY_VARIANT_ID")

# رسائل تأكيد (تظهر في سجلات Streamlit)
if LEMONSQUEEZY_API_KEY:
    print(f"✅ Config loaded: API Key starts with {LEMONSQUEEZY_API_KEY[:8]}...")
else:
    print("❌ Config failed: LEMONSQUEEZY_API_KEY is missing in st.secrets!")
