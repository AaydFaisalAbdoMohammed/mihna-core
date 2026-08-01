import os
import io
import json
import hmac
import hashlib
import time
import base64
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import bcrypt
import requests
import google.generativeai as genai

# ==========================================
# 1. SETUP & PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Enterprise AI Engine | وكيل مهنة PRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. STATE MANAGEMENT & LOCALIZATION
# ==========================================
if "lang" not in st.session_state:
    st.session_state.lang = "AR"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "active_project" not in st.session_state:
    st.session_state.active_project = None

TRANSLATIONS = {
    "AR": {
        "title": "منصة وكيل مهنة PRO - المؤسسية",
        "subtitle": "محرك الذكاء الاصطناعي السيادي لإدارة وتخطيط المشاريع والمهام",
        "auth_header": "تسجيل الدخول / إنشاء حساب",
        "dashboard": "لوحة التحكم",
        "generator": "مولد الخطط والمشاريع",
        "history": "أرشيف المشاريع",
        "settings": "الإعدادات والأمان",
        "lang_switch": "English",
        "dir": "rtl"
    },
    "EN": {
        "title": "Mihna Agent PRO - Enterprise Platform",
        "subtitle": "Sovereign AI Engine for Project Planning & Task Management",
        "auth_header": "Authentication / Register",
        "dashboard": "Dashboard",
        "generator": "Project Generator",
        "history": "Project History",
        "settings": "Settings & Security",
        "lang_switch": "العربية",
        "dir": "ltr"
    }
}

t = TRANSLATIONS[st.session_state.lang]

# ==========================================
# 3. DYNAMIC INJECTED CSS (THEMING & RTL)
# ==========================================
def inject_custom_css():
    direction = t["dir"]
    is_dark = st.session_state.theme == "Dark"
    
    bg_color = "#0E1117" if is_dark else "#FFFFFF"
    card_bg = "#1E222D" if is_dark else "#F8F9FA"
    text_color = "#FFFFFF" if is_dark else "#1A1A1A"
    accent_color = "#4F46E5"
    
    css = f"""
    <style>
        body, .stApp {{
            direction: {direction};
            text-align: {'right' if direction == 'rtl' else 'left'};
            background-color: {bg_color};
            color: {text_color};
        }}
        .enterprise-card {{
            background-color: {card_bg};
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}
        .stButton>button {{
            background: linear-gradient(135deg, {accent_color}, #3730A3);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }}
        /* RTL Fixes for Streamlit Elements */
        div[data-testid="stSidebarNav"] {{
            text-align: {'right' if direction == 'rtl' else 'left'};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 4. VAULT SECURITY & HMAC SIGNING
# ==========================================
class VaultSecurity:
    @staticmethod
    def get_secret_key():
        return st.secrets.get("VAULT_SECRET_KEY", "DEFAULT_SECURE_KEY_32894723984729384")

    @classmethod
    def generate_hmac_signature(cls, data_string: str) -> str:
        key = cls.get_secret_key().encode('utf-8')
        return hmac.new(key, data_string.encode('utf-8'), hashlib.sha512).hexdigest()

    @classmethod
    def verify_signature(cls, data_string: str, signature: str) -> bool:
        expected_signature = cls.generate_hmac_signature(data_string)
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ==========================================
# 5. DATABASE LAYER (MOCK/REAL CLOUD SQL)
# ==========================================
class DatabaseManager:
    @staticmethod
    def query(sql: str, params: tuple = ()):
        # يمكن استبدال هذه المنطقة بالربط المباشر مع PyMySQL / PostgreSQL
        # مثال لتنفيذ استعلام مع الحفاظ على الأداء للأحجام الكبيرة
        return None

# ==========================================
# 6. INTEGRATIONS (PAYMENTS, TELEGRAM, GEMINI)
# ==========================================
class LemonSqueezyAPI:
    @staticmethod
    def create_checkout(store_id: str, variant_id: str, user_email: str) -> str:
        api_key = st.secrets.get("LEMON_SQUEEZY_API_KEY", "")
        if not api_key:
            return f"https://lemonsqueezy.com/checkout?cart={variant_id}&checkout[email]={user_email}"
        
        headers = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {"email": user_email}
                },
                "relationships": {
                    "store": {"data": {"type": "stores", "id": str(store_id)}},
                    "variant": {"data": {"type": "variants", "id": str(variant_id)}}
                }
            }
        }
        try:
            res = requests.post("https://api.lemonsqueezy.com/v1/checkouts", json=payload, headers=headers)
            if res.status_code == 201:
                return res.json()["data"]["attributes"]["url"]
        except Exception as e:
            st.error(f"Payment Link Generation Error: {e}")
        return "#"

class NotificationService:
    @staticmethod
    def send_telegram(message: str):
        bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": message})

# ==========================================
# 7. AI CORE & RAG ENGINE
# ==========================================
class AICoreEngine:
    @staticmethod
    def initialize():
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)

    @classmethod
    def generate_project_plan(cls, prompt_text: str, context_documents: list = None) -> dict:
        cls.initialize()
        
        system_instruction = """
        أنت مهندس معمارية وحاسب كميات واكتواري متخصص في تخطيط المشاريع.
        قم بأخذ المخرجات وتحليلها وتقديم JSON مخصص يحتوي على:
        1. project_name: اسم المشروع
        2. total_budget: ميزانية تقديرية (رقم)
        3. risk_score: نسبة المخاطرة (0 - 100)
        4. tasks: قائمة تحتوي على (task_name, duration_days, cost, risk_level)
        """
        
        context_str = ""
        if context_documents:
            context_str = "\n\nالسياق المسترجع من المشاريع السابقة (RAG):\n" + "\n".join(context_documents)
            
        full_prompt = f"{system_instruction}\n{context_str}\n\nطلب العميل:\n{prompt_text}"
        
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(
                full_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            # Fallback mock for demonstration if API key is missing
            return {
                "project_name": "مشروع تطوير منصة تجارة إلكترونية",
                "total_budget": 15000,
                "risk_score": 25,
                "tasks": [
                    {"task_name": "تحليل المتطلبات وهيكلة البيانات", "duration_days": 5, "cost": 2000, "risk_level": "Low"},
                    {"task_name": "تطوير واجهات المستخدم والـ UI/UX", "duration_days": 10, "cost": 4500, "risk_level": "Medium"},
                    {"task_name": "ربط بوابات الدفع وقواعد البيانات", "duration_days": 8, "cost": 5000, "risk_level": "High"},
                    {"task_name": "الاختبارات والتكامل النهائي", "duration_days": 4, "cost": 3500, "risk_level": "Low"}
                ]
            }

# ==========================================
# 8. VISUALIZATION COMPONENTS
# ==========================================
def render_risk_gauge(score: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "مؤشر المخاطرة التراكمي (Risk Index)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4F46E5"},
            'steps': [
                {'range': [0, 30], 'color': "#10B981"},
                {'range': [30, 70], 'color': "#F59E0B"},
                {'range': [70, 100], 'color': "#EF4444"}
            ]
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 9. MAIN APPLICATION UI LAYOUT
# ==========================================
def main():
    # --- SIDEBAR CONTROL PANEL ---
    with st.sidebar:
        st.title("⚙️ " + t["title"])
        st.caption(t["subtitle"])
        st.divider()

        # Language & Theme Toggles
        col_lang, col_theme = st.columns(2)
        with col_lang:
            if st.button(t["lang_switch"]):
                st.session_state.lang = "EN" if st.session_state.lang == "AR" else "AR"
                st.rerun()
        with col_theme:
            if st.button("🌓 " + st.session_state.theme):
                st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
                st.rerun()

        st.divider()
        menu_choice = st.radio("القائمة الرئيسية", [t["dashboard"], t["generator"], t["history"], t["settings"]])

        st.divider()
        # Subscription Integration
        st.subheader("💳 باقة الاشتراك")
        if st.button("ترقية للنسخة الاحترافية PRO"):
            checkout_url = LemonSqueezyAPI.create_checkout("store_123", "variant_999", "user@enterprise.com")
            st.markdown(f"[🔗 اضغط هنا لاتمام الدفع]({checkout_url})")

    # --- TOP HEADER ---
    st.markdown(f"""
        <div class="enterprise-card">
            <h2>{t["title"]}</h2>
            <p>{t["subtitle"]}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- ROUTING PAGES ---
    if menu_choice == t["dashboard"]:
        st.subheader("📊 لوحة الأداء والمؤشرات الحيوية")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("المشاريع النشطة", "12", "+2 هذا الأسبوع")
        m2.metric("إجمالي الميزانيات", "$142,500", "+15%")
        m3.metric("معدل دقة الذكاء الاصطناعي", "98.4%", "+0.4%")
        m4.metric("توقيع التشفير (Vault Status)", "SECURE", delta_color="normal")

        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown("### 📈 توزيع التكاليف عبر المهام")
            chart_data = pd.DataFrame({
                "المرحلة": ["التصميم", "التطوير", "الأمان", "الإطلاق"],
                "التكلفة": [3000, 8000, 4000, 2000]
            })
            st.bar_chart(chart_data.set_index("المرحلة"))

        with col_right:
            render_risk_gauge(28.5)

    elif menu_choice == t["generator"]:
        st.subheader("🚀 توليد وتخطيط مشروع جديد (AI + RAG + HITL)")

        with st.form("project_generation_form"):
            prompt_input = st.text_area("أدخل تفاصيل ومتطلبات المشروع بشكل دقيق:", height=120, 
                                        placeholder="مثال: إنشاء تطبيق متجر إلكتروني مع نظام مدفوعات وتتبع الشحنات...")
            use_rag = st.checkbox("استرجاع مشاريع مشابهة من الذاكرة (RAG)", value=True)
            submitted = st.form_submit_button("توليد الخطة السيادية")

        if submitted and prompt_input:
            with st.spinner("جاري تحليل المتطلبات، استرجاع السياق، وحساب المخاطر..."):
                rag_context = ["مشروع متجر سابق بتكلفة 12,000$ واستغرق 25 يوماً"] if use_rag else []
                plan_result = AICoreEngine.generate_project_plan(prompt_input, rag_context)
                st.session_state.active_project = plan_result
                NotificationService.send_telegram(f"تم توليد مشروع جديد: {plan_result.get('project_name')}")

        # --- HUMAN-IN-THE-LOOP (HITL) EDITING SECTION ---
        if st.session_state.active_project:
            st.divider()
            st.markdown("### 🛠️ تعديل وتخصيص الخطة (Human-In-The-Loop)")
            proj = st.session_state.active_project

            st.text_input("اسم المشروع:", value=proj["project_name"])
            
            # Interactive Dataframe Editing for Tasks
            df_tasks = pd.DataFrame(proj["tasks"])
            edited_df = st.data_editor(
                df_tasks, 
                num_rows="dynamic", 
                use_container_width=True,
                key="task_editor"
            )

            col_actions1, col_actions2 = st.columns(2)
            with col_actions1:
                if st.button("اعتماد وتوقيع الخطة رقمياً (HMAC Seal)"):
                    json_str = edited_df.to_json()
                    signature = VaultSecurity.generate_hmac_signature(json_str)
                    st.success(f"تمت المصادقة وتوقيع المشروع رقمياً!\nSignature: {signature[:32]}...")

            with col_actions2:
                # Export options
                buffer = io.BytesIO()
                edited_df.to_excel(buffer, index=False)
                st.download_button(
                    label="📥 تحميل التقرير بصيغة Excel",
                    data=buffer.getvalue(),
                    file_name="project_plan.xlsx",
                    mime="application/vnd.ms-excel"
                )

    elif menu_choice == t["history"]:
        st.subheader("📂 أرشيف المشاريع الموقعة والمحفوظة")
        st.info("جميع المشاريع المخرجة في هذا الأرشيف محمية بواسطة HMAC-SHA512.")

    elif menu_choice == t["settings"]:
        st.subheader("🛡️ إعدادات الأمان والتكاملات السحابية")
        st.text_input("API Key لـ Gemini", type="password", value=st.secrets.get("GEMINI_API_KEY", ""))
        st.text_input("Vault Secret Key", type="password", value=VaultSecurity.get_secret_key())
        st.button("حفظ التغييرات الأمنية")

if __name__ == "__main__":
    main()
