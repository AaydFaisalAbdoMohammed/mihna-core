#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX PRO HYBRID ENTERPRISE ARCHITECTURE. ALL RIGHTS RESERVED.
دمج المحرك الأمني والهندسي مع نظام الاشتراكات والإشعارات الفورية
===============================================================================
"""

import os
import re
import json
import uuid
import hashlib
import hmac
import time
import secrets
import logging
import requests
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# ----------------- Optional Heavy Dependencies -----------------
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =====================================================================
# 1. TRANSLATION DICTIONARY (ARABIC / ENGLISH)
# =====================================================================
TRANSLATIONS = {
    "ar": {
        "title": "🔥 PHOENIX PRO ENTERPRISE",
        "login_tab": "🔑 تسجيل الدخول",
        "signup_tab": "📝 إنشاء حساب جديد",
        "login_header": "دخول إلى منصة المعمارية",
        "signup_header": "حساب جديد (يتضمن 5 محاولات مجانية)",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "confirm_pass": "تأكيد كلمة المرور",
        "full_name": "الاسم الكامل",
        "login_btn": "تسجيل الدخول",
        "signup_btn": "إنشاء الحساب",
        "logout": "🚪 تسجيل الخروج",
        "user": "المستخدم",
        "credits_left": "⚡ المحاولات المتبقية",
        "plan_status": "الاشتراك الحالي",
        "gemini_key": "🔑 مفتاح Gemini API",
        "tg_title": "📲 إشعارات Telegram",
        "tg_test": "🔔 اختبار إشعار التلجرام",
        "email_title": "📧 إشعارات البريد (SMTP)",
        "smtp_user": "بريد المرسل (SMTP)",
        "smtp_pass": "كلمة مرور التطبيقات",
        "sub_title": "💳 خطط الاشتراك والتفعيل",
        "monthly": "🗓️ شهري ($29)",
        "yearly": "⭐ سنوي ($290)",
        "act_code": "رمز التفعيل / الكوبون",
        "activate": "تفعيل الكود",
        "tab_gen": "🚀 توليد المعمارية",
        "tab_analytics": "📊 التحليلات والأرشيف",
        "tab_export": "📦 التصدير والتوثيق",
        "client": "🏢 اسم العميل / الشركة",
        "budget": "💰 الميزانية التقديرية",
        "timeline": "⏱️ المدة الزمنية",
        "tech": "🛠️ التقنيات المفضلة",
        "scope": "📌 نطاق المشروع والمتطلبات التفصيلية",
        "generate_btn": "⚡ بدء التوليد والتوقيع المشفر",
        "history_title": "📋 الخطة الهندسية المعمارية المنشأة",
        "cost_gauge": "💰 التكلفة الكلية التقديرية",
        "days_gauge": "⏱️ إجمالي فترة التنفيذ",
        "confidence_gauge": "🎯 موثوقية المعمارية",
        "risk_score": "🚨 درجة المخاطرة",
        "accuracy": "🎯 نسبة الدقة والاعتماد",
        "total_days": "⏱️ إجمالي الأيام",
        "total_cost": "💰 التكلفة الكلية",
        "export_json": "📦 تصدير JSON المشفر",
        "export_excel": "📊 تصدير جدول Excel",
        "export_pdf": "📄 تصدير تقرير PDF",
        "theme_toggle": "مظهر الواجهة",
        "lang_toggle": "اللغة"
    },
    "en": {
        "title": "🔥 PHOENIX PRO ENTERPRISE",
        "login_tab": "🔑 Login",
        "signup_tab": "📝 Sign Up",
        "login_header": "Architecture Platform Portal",
        "signup_header": "New Account (Includes 5 Free Credits)",
        "email": "Email Address",
        "password": "Password",
        "confirm_pass": "Confirm Password",
        "full_name": "Full Name",
        "login_btn": "Sign In",
        "signup_btn": "Create Account",
        "logout": "🚪 Logout",
        "user": "User",
        "credits_left": "⚡ Remaining Credits",
        "plan_status": "Current Plan",
        "gemini_key": "🔑 Gemini API Key",
        "tg_title": "📲 Telegram Notifications",
        "tg_test": "🔔 Test Telegram Bot",
        "email_title": "📧 Email Notifications (SMTP)",
        "smtp_user": "Sender Email (SMTP)",
        "smtp_pass": "App Password",
        "sub_title": "💳 Subscription & Billing",
        "monthly": "🗓️ Monthly ($29)",
        "yearly": "⭐ Yearly ($290)",
        "act_code": "Activation Code / Coupon",
        "activate": "Activate Code",
        "tab_gen": "🚀 Generate Architecture",
        "tab_analytics": "📊 Analytics & Archive",
        "tab_export": "📦 Export & Docs",
        "client": "🏢 Client / Company Name",
        "budget": "💰 Estimated Budget",
        "timeline": "⏱️ Timeline / Duration",
        "tech": "🛠️ Preferred Tech Stack",
        "scope": "📌 Project Scope & Requirements",
        "generate_btn": "⚡ Generate & Sign Architecture",
        "history_title": "📋 Generated Architecture Plan",
        "cost_gauge": "💰 Total Estimated Cost",
        "days_gauge": "⏱️ Total Implementation Time",
        "confidence_gauge": "🎯 Architecture Confidence",
        "risk_score": "🚨 Risk Score",
        "accuracy": "🎯 Accuracy & Trust Ratio",
        "total_days": "⏱️ Total Days",
        "total_cost": "💰 Total Cost",
        "export_json": "📦 Export Signed JSON",
        "export_excel": "📊 Export Excel Sheet",
        "export_pdf": "📄 Export PDF Report",
        "theme_toggle": "Theme Mode",
        "lang_toggle": "Language"
    }
}

# =====================================================================
# 2. SYSTEM SECURITY & INTEGRITY ENGINE
# =====================================================================
class VaultSecurity:
    HMAC_KEY = os.getenv("HMAC_KEY", secrets.token_hex(32))

    @classmethod
    def get_fingerprint(cls) -> str:
        seed = f"{os.getenv('HOSTNAME', 'cloud_node')}-{datetime.datetime.now().isoformat()}-{uuid.uuid4()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:24]

    @classmethod
    def sign_payload(cls, payload: dict) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(cls.HMAC_KEY.encode(), payload_str.encode(), hashlib.sha512).hexdigest()[:32]

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

# =====================================================================
# 3. NOTIFICATION & COMMERCE ENGINE
# =====================================================================
class CommercialEngine:
    @staticmethod
    def send_telegram(plan: dict, bot_token: str, chat_id: str) -> bool:
        if not bot_token or not chat_id:
            return False
        
        msg = (
            f"🚀 *مشروع جديد PHOENIX PRO*\n\n"
            f"👤 *العميل:* {plan.get('client')}\n"
            f"💰 *الميزانية:* {plan.get('budget_str')}\n"
            f"📅 *المدة:* {plan.get('timeline')}\n"
            f"🔑 *التوقيع:* `{plan.get('signature', 'N/A')}`\n"
            f"⏱️ *التاريخ:* {plan.get('timestamp')}"
        )
        try:
            res = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, 
                timeout=5
            )
            return res.status_code == 200
        except Exception:
            return False

    @staticmethod
    def send_email(plan: dict, recipient_email: str, smtp_user: str, smtp_pass: str, smtp_host="smtp.gmail.com", smtp_port=587) -> bool:
        if not smtp_user or not smtp_pass or not recipient_email:
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔥 [PHOENIX PRO] الخطة الهندسية المعمارية - {plan.get('client')}"
            msg["From"] = smtp_user
            msg["To"] = recipient_email

            tasks_html = "".join([
                f"<li><b>{t.get('title')}</b> - المدة: {t.get('days')} أيام | التكلفة: ${t.get('cost')}</li>"
                for t in plan.get("tasks", [])
            ])

            html_body = f"""
            <div dir="rtl" style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #f1f5f9; padding: 20px; border-radius: 10px;">
                <h2 style="color: #3b82f6;">🚀 PHOENIX PRO - الخطة الهندسية المعمارية</h2>
                <p><b>🏛️ العميل:</b> {plan.get('client')}</p>
                <p><b>💰 الميزانية:</b> {plan.get('budget_str')}</p>
                <p><b>📅 المدة الزمنية:</b> {plan.get('timeline')}</p>
                <p><b>🔑 التوقيع الرقمي (HMAC):</b> <code>{plan.get('signature')}</code></p>
                <hr style="border: 1px solid #334155;">
                <h3>📝 الملخص التنفيذي:</h3>
                <p style="line-height: 1.6;">{plan.get('executive_summary')}</p>
                <hr style="border: 1px solid #334155;">
                <h3>🎯 مهام التنفيذ:</h3>
                <ul>{tasks_html}</ul>
            </div>
            """
            msg.attach(MIMEText(html_body, "html"))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            st.warning(f"تعذر إرسال البريد الإلكتروني: {str(e)}")
            return False

    @staticmethod
    def get_checkout_url(email: str, plan_type: str = "monthly") -> str:
        store_slug = os.getenv("LEMONSQUEEZY_STORE_SLUG", "mihna")
        return f"https://{store_slug}.lemonsqueezy.com/buy?checkout[email]={email.strip()}&plan={plan_type}"

# =====================================================================
# 4. AI ENGINE
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        lang_instruction = "اللغة العربية" if lang == "ar" else "English"
        
        prompt = f"""
        You are an Enterprise System Architect at PHOENIX PRO. Analyze this project:
        - Client: {req['client']}
        - Description & Scope: {req['desc']}
        - Budget: {req['budget']}
        - Timeline: {req['timeline']}
        - Preferred Technologies: {req['tech']}

        Output the result STRICTLY as a JSON object in {lang_instruction} with this exact schema:
        {{
            "client": "{req['client']}",
            "executive_summary": "Comprehensive architectural analysis here...",
            "tech_stack": ["Tech 1", "Tech 2"],
            "budget_str": "{req['budget']}",
            "timeline": "{req['timeline']}",
            "risk_score": 15,
            "confidence_score": 90,
            "tasks": [
                {{"title": "Task 1: Architecture Design", "days": 5, "cost": 1200, "priority": "High"}},
                {{"title": "Task 2: API & Core Engine", "days": 10, "cost": 2400, "priority": "Medium"}}
            ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            data = json.loads(match.group() if match else response.text)
            data["signature"] = VaultSecurity.sign_payload(data)
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            return data
        except Exception as e:
            raise ValueError(f"Failed to generate architecture: {str(e)}")

# =====================================================================
# 5. EXPORT ENGINE
# =====================================================================
class ExportEngine:
    @staticmethod
    def build_pdf(data: dict) -> bytes:
        if not REPORTLAB_AVAILABLE: return b""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>Enterprise Architecture Document: {data.get('client')}</b>", styles['Title']), Spacer(1, 12)]
        
        table_data = [["Task", "Days", "Cost ($)", "Priority"]]
        for t in data.get("tasks", []):
            table_data.append([t.get('title'), str(t.get('days')), f"${t.get('cost')}", t.get('priority')])
            
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
        ]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()

    @staticmethod
    def build_excel(tasks: list) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Architecture_Plan")
        return buffer.getvalue()

# =====================================================================
# 6. SESSION MANAGEMENT
# =====================================================================
def init_session():
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "eng.alhiadri2020@gmail.com": {
                "name": "AYAD FAISAL ABDO MOHAMMED",
                "password": VaultSecurity.hash_password("123456"),
                "credits": 5,
                "plan_status": "Free Trial (5 Credits)"
            }
        }
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if "current_user" not in st.session_state: st.session_state.current_user = None
    if "plans_history" not in st.session_state: st.session_state.plans_history = []
    if "selected_plan" not in st.session_state: st.session_state.selected_plan = None
    if "lang" not in st.session_state: st.session_state.lang = "ar"
    if "theme" not in st.session_state: st.session_state.theme = "dark"

# =====================================================================
# 7. ADVANCED HIGH-PERFORMANCE CSS INJECTION (FIXES & OPTIMIZATIONS)
# =====================================================================
def inject_custom_css():
    lang = st.session_state.lang
    theme = st.session_state.theme
    
    direction = "rtl" if lang == "ar" else "ltr"
    align_text = "right" if lang == "ar" else "left"
    
    if theme == "dark":
        bg_main = "#0b0f19"
        bg_sidebar = "#0f172a"
        bg_card = "#1e293b"
        bg_input = "#131b2e"
        text_color = "#f1f5f9"
        border_color = "#2e3a59"
        label_color = "#f8fafc"
        btn_bg = "linear-gradient(135deg, #1e293b 0%, #334155 100%)"
        btn_text = "#ffffff"
        btn_border = "#475569"
    else:
        bg_main = "#f8fafc"
        bg_sidebar = "#f1f5f9"
        bg_card = "#ffffff"
        bg_input = "#ffffff"
        text_color = "#0f172a"
        border_color = "#cbd5e1"
        label_color = "#1e293b"
        btn_bg = "linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)"
        btn_text = "#0f172a"
        btn_border = "#94a3b8"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700&display=swap');

        /* 🔴 1. FIX SIDEBAR COLLAPSE BUTTON & MATERIAL ICONS (إصلاح زر الإغلاق والأيقونات) */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stSidebarHeader"] *,
        [data-testid="stIcon"],
        [data-testid="stIcon"] *,
        [data-baseweb="icon"],
        [data-baseweb="icon"] * {{
            font-family: 'Material Icons', 'Material Symbols Outlined' !important;
            direction: ltr !important;
            white-space: nowrap !important;
            word-break: normal !important;
            overflow-wrap: normal !important;
        }}

        /* 🔵 2. BASE TYPOGRAPHY & LAYOUT CONTROL */
        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Cairo', 'Inter', sans-serif !important;
            direction: {direction};
            text-align: {align_text};
            background-color: {bg_main} !important;
            color: {text_color} !important;
            overflow-x: hidden !important;
        }}

        /* 🟣 3. SIDEBAR FIXES & TEXT WRAPPING (تنسيق القائمة الجانبية بشكل آمن) */
        [data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
            border-{'left' if lang == 'ar' else 'right'}: 1px solid {border_color} !important;
            width: 320px !important;
            min-width: 300px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.8rem !important;
            overflow-x: hidden !important;
        }}

        /* إبقاء التفاف النصوص آمن حصرياً لفقرات وشعارات الشريط الجانبي دون لمس الأيقونات */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] .stMarkdown span {{
            color: {text_color} !important;
            word-break: break-word !important;
            white-space: normal !important;
        }}

        /* 🟢 4. HIGH-CONTRAST SIDEBAR BUTTONS */
        [data-testid="stSidebar"] .stButton > button {{
            background: {btn_bg} !important;
            color: {btn_text} !important;
            border: 1px solid {btn_border} !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 0.5rem 1rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.25s ease-in-out !important;
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            border-color: #3b82f6 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(59, 130, 246, 0.3) !important;
        }}

        /* 🟡 5. INPUT FIELDS & LABELS */
        div[data-baseweb="field"] > label, .stTextInput > label, .stTextArea > label {{
            color: {label_color} !important;
            font-size: 0.98rem !important;
            font-weight: 700 !important;
            margin-bottom: 4px !important;
        }}

        .stTextInput input, .stTextArea textarea {{
            background-color: {bg_input} !important;
            color: {text_color} !important;
            border: 1.5px solid {border_color} !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
        }}

        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: #3b82f6 !important;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.4) !important;
        }}

        /* 🧡 6. CUSTOM CARDS & LAYOUT COMPONENTS */
        .plan-box {{
            background-color: {bg_card};
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}

        .task-card {{
            background-color: {bg_input};
            padding: 14px;
            border-radius: 8px;
            border-{'right' if lang == 'ar' else 'left'}: 4px solid #3b82f6;
            margin-bottom: 10px;
        }}

        .gauge-card {{
            background: {bg_card};
            border-radius: 12px;
            border: 1px solid {border_color};
            padding: 10px;
        }}

        .pay-btn {{
            display: block;
            background: linear-gradient(90deg, #2563eb, #4f46e5);
            color: white !important;
            text-align: center;
            padding: 10px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .hero-header {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            padding: 10px 0;
        }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 8. HELPER: CREATING SEMICIRCLE GAUGE CHARTS
# =====================================================================
def create_semicircle_gauge(value: float, max_val: float, title: str, prefix: str = "", suffix: str = "", color_scheme: str = "blue"):
    colors_map = {
        "blue": {"line": "#3b82f6", "gradient": ["#1e1b4b", "#1d4ed8", "#60a5fa"]},
        "green": {"line": "#10b981", "gradient": ["#064e3b", "#047857", "#34d399"]},
        "purple": {"line": "#8b5cf6", "gradient": ["#311042", "#6d28d9", "#c084fc"]}
    }
    scheme = colors_map.get(color_scheme, colors_map["blue"])
    text_c = "#f8fafc" if st.session_state.theme == "dark" else "#0f172a"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'prefix': prefix, 'suffix': suffix, 'font': {'size': 26, 'color': text_c, 'family': "Cairo"}},
        title={'text': f"<b>{title}</b>", 'font': {'size': 15, 'color': "#94a3b8"}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': scheme["line"], 'thickness': 0.25},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 1,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, max_val * 0.5], 'color': scheme["gradient"][0]},
                {'range': [max_val * 0.5, max_val * 0.85], 'color': scheme["gradient"][1]},
                {'range': [max_val * 0.85, max_val], 'color': scheme["gradient"][2]}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': text_c, 'family': "Cairo"},
        height=210,
        margin=dict(l=20, r=20, t=35, b=10)
    )
    return fig

# =====================================================================
# 9. AUTHENTICATION PAGE
# =====================================================================
def render_auth_page():
    t = TRANSLATIONS[st.session_state.lang]
    inject_custom_css()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div class="hero-header">{t["title"]}</div>', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs([t["login_tab"], t["signup_tab"]])
        
        with tab_login:
            st.subheader(t["login_header"])
            email = st.text_input(t["email"], key="login_email")
            password = st.text_input(t["password"], type="password", key="login_pass")
            
            if st.button(t["login_btn"], use_container_width=True, type="primary"):
                hashed_pass = VaultSecurity.hash_password(password)
                if email in st.session_state.users_db and st.session_state.users_db[email]["password"] == hashed_pass:
                    st.session_state.authenticated = True
                    st.session_state.current_user = st.session_state.users_db[email]
                    st.session_state.current_user["email"] = email
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid Email or Password.")
                    
        with tab_signup:
            st.subheader(t["signup_header"])
            new_name = st.text_input(t["full_name"], key="signup_name")
            new_email = st.text_input(t["email"], key="signup_email")
            new_pass = st.text_input(t["password"], type="password", key="signup_pass")
            confirm_pass = st.text_input(t["confirm_pass"], type="password", key="signup_confirm")
            
            if st.button(t["signup_btn"], use_container_width=True):
                if not new_name or not new_email or not new_pass:
                    st.error("Please fill all required fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif new_email in st.session_state.users_db:
                    st.error("Email is already registered.")
                else:
                    st.session_state.users_db[new_email] = {
                        "name": new_name,
                        "password": VaultSecurity.hash_password(new_pass),
                        "credits": 5,
                        "plan_status": "Free Trial (5 Credits)"
                    }
                    st.success("Account created successfully! Log in now.")

# =====================================================================
# 10. MAIN APPLICATION
# =====================================================================
def main():
    st.set_page_config(page_title="PHOENIX PRO | Hybrid Architecture", page_icon="🚀", layout="wide")
    init_session()
    inject_custom_css()
    
    t = TRANSLATIONS[st.session_state.lang]

    if not st.session_state.authenticated:
        render_auth_page()
        return

    user = st.session_state.current_user
    
    # ----------------- SIDEBAR COMMAND -----------------
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>⚙️ PHOENIX COMMAND</h2>", unsafe_allow_html=True)
        
        # 🌐 LANGUAGE & THEME TOGGLES
        c_lang, c_theme = st.columns(2)
        with c_lang:
            lang_label = "🌐 English" if st.session_state.lang == "ar" else "🌐 العربية"
            if st.button(lang_label, use_container_width=True):
                st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
                st.rerun()
        with c_theme:
            theme_label = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
            if st.button(theme_label, use_container_width=True):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                st.rerun()

        st.divider()
        st.caption(f"👤 {t['user']}: {user.get('name')}")
        st.caption(f"📧 {t['email']}: {user.get('email')}")
        
        user_credits = user.get("credits", 0)
        st.markdown(f"**{t['credits_left']}:** `{user_credits}` / 5")
        st.caption(f"{t['plan_status']}: {user.get('plan_status', 'Free')}")
        
        if st.button(t["logout"], use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
            
        st.divider()
        api_key = st.text_input(t["gemini_key"], type="password", value=os.getenv("GEMINI_API_KEY", ""))
        
        st.divider()
        # ----------------- TELEGRAM -----------------
        st.subheader(t["tg_title"])
        tg_bot_token = st.text_input("Telegram Bot Token", type="password", value=os.getenv("TELEGRAM_BOT_TOKEN", ""))
        tg_chat_id = st.text_input("Telegram Chat ID", value=os.getenv("TELEGRAM_CHAT_ID", "597154321"))
        if st.button(t["tg_test"], use_container_width=True):
            test_plan = {"client": "Test Project", "budget_str": "$1,000", "timeline": "1 Week", "signature": "TEST-123", "timestamp": "Now"}
            if CommercialEngine.send_telegram(test_plan, tg_bot_token, tg_chat_id):
                st.success("Telegram Notification Sent Successfully! 🚀")
            else:
                st.error("Failed to send Telegram notification.")

        st.divider()
        # ----------------- EMAIL (SMTP) -----------------
        st.subheader(t["email_title"])
        smtp_user = st.text_input(t["smtp_user"], value=os.getenv("SMTP_USER", ""))
        smtp_pass = st.text_input(t["smtp_pass"], type="password", value=os.getenv("SMTP_PASS", ""))
        
        st.divider()
        # ----------------- BILLING -----------------
        st.subheader(t["sub_title"])
        pay_email = st.text_input(t["email"], value=user.get('email'), key="billing_email")
        
        col_m, col_y = st.columns(2)
        with col_m:
            st.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email, "monthly")}" target="_blank" class="pay-btn">{t["monthly"]}</a>', unsafe_allow_html=True)
        with col_y:
            st.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email, "yearly")}" target="_blank" class="pay-btn">{t["yearly"]}</a>', unsafe_allow_html=True)
        
        act_code = st.text_input(t["act_code"], type="password")
        if st.button(t["activate"], use_container_width=True):
            if act_code in ["MONTHLY2026", "MONTHLY"]:
                user["credits"] += 30
                user["plan_status"] = "Monthly Pro"
                st.success("Activated Monthly Subscription (+30 Credits)!")
                st.rerun()
            elif act_code in ["ANNUAL2026", "YEARLY"]:
                user["credits"] += 500
                user["plan_status"] = "Yearly Pro"
                st.success("Activated Yearly Subscription (+500 Credits)!")
                st.rerun()
            elif act_code == "PRO2026":
                user["credits"] = 9999
                user["plan_status"] = "Unlimited Developer"
                st.success("Activated Unlimited Access!")
                st.rerun()
            else:
                st.error("Invalid Code.")

    # ----------------- DASHBOARD -----------------
    st.markdown(f'<div class="hero-header">{t["title"]}</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([t["tab_gen"], t["tab_analytics"], t["tab_export"]])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            client = st.text_input(t["client"], value="مؤسسة أفق" if st.session_state.lang == "ar" else "Horizon Corp")
            budget = st.text_input(t["budget"], value="8000 - 12000 $")
        with c2:
            timeline = st.text_input(t["timeline"], value="6 أسابيع" if st.session_state.lang == "ar" else "6 Weeks")
            tech = st.text_input(t["tech"], value="Flutter, Node.js, PostgreSQL")
            
        desc = st.text_area(
            t["scope"], 
            value="تطوير منصة سحابية متكاملة لإدارة العقود وتتبع عمليات الصيانة مع بوابات دفع إلكترونية متعددة ولوحة تحليلات تفاعلية." if st.session_state.lang == "ar" else "Develop an enterprise cloud portal for contract management and maintenance tracking with payment gateways.",
            height=130
        )
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        if st.button(t["generate_btn"], use_container_width=True, type="primary"):
            if not api_key:
                st.error("Please insert your Gemini API Key in the sidebar.")
            elif user.get("credits", 0) <= 0:
                st.error("❌ Out of credits. Please upgrade your plan.")
            else:
                with st.spinner("Analyzing Architecture & Deducting Credit..."):
                    req_payload = {"client": client, "budget": budget, "timeline": timeline, "tech": tech, "desc": desc}
                    try:
                        plan = PhoenixAI.generate_architecture(api_key, req_payload, lang=st.session_state.lang)
                        st.session_state.plans_history.append(plan)
                        st.session_state.selected_plan = plan
                        
                        user["credits"] -= 1
                        
                        if tg_bot_token and tg_chat_id:
                            CommercialEngine.send_telegram(plan, tg_bot_token, tg_chat_id)
                        if smtp_user and smtp_pass:
                            CommercialEngine.send_email(plan, user.get("email"), smtp_user, smtp_pass)

                        st.success(f"✅ Architecture generated! Remaining Credits: {user['credits']}")
                        st.rerun()
                    except Exception as err:
                        st.error(str(err))

        if st.session_state.selected_plan:
            plan = st.session_state.selected_plan
            st.markdown("---")
            st.markdown(f"### {t['history_title']}")
            
            st.markdown(f"""
            <div class="plan-box">
                <h4>🏛️ {plan.get('client')}</h4>
                <p><b>📅 Date:</b> {plan.get('timestamp')}</p>
                <p><b>🔑 Signature (HMAC):</b> <code>{plan.get('signature')}</code></p>
                <hr style="border-color:#334155;">
                <h5>📝 Executive Summary:</h5>
                <p style="line-height:1.7;">{plan.get('executive_summary')}</p>
                <hr style="border-color:#334155;">
                <h5>🛠️ Tech Stack:</h5>
                <p><code>{"  |  ".join(plan.get('tech_stack', []))}</code></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🎯 Action Tasks & Timeline:")
            for idx, task in enumerate(plan.get("tasks", []), 1):
                st.markdown(f"""
                <div class="task-card">
                    <b>{idx}. {task.get('title')}</b><br/>
                    ⏱️ {task.get('days')} Days | 
                    💰 ${task.get('cost')} | 
                    🔴 Priority: <code>{task.get('priority')}</code>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            tasks = p.get("tasks", [])
            total_days = sum([t.get('days', 0) for t in tasks])
            total_cost = sum([t.get('cost', 0) for t in tasks])
            confidence = p.get('confidence_score', 92)
            
            st.markdown(f"### 🎛️ Executive Gauges ({p.get('client')})")
            
            g_col1, g_col2, g_col3 = st.columns(3)
            with g_col1:
                st.markdown('<div class="gauge-card">', unsafe_allow_html=True)
                fig_cost = create_semicircle_gauge(total_cost, max(total_cost * 1.25, 10000), t["cost_gauge"], "$", color_scheme="green")
                st.plotly_chart(fig_cost, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with g_col2:
                st.markdown('<div class="gauge-card">', unsafe_allow_html=True)
                fig_days = create_semicircle_gauge(total_days, max(total_days * 1.3, 30), t["days_gauge"], suffix=" D", color_scheme="purple")
                st.plotly_chart(fig_days, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with g_col3:
                st.markdown('<div class="gauge-card">', unsafe_allow_html=True)
                fig_conf = create_semicircle_gauge(confidence, 100, t["confidence_gauge"], suffix="%", color_scheme="blue")
                st.plotly_chart(fig_conf, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric(t["risk_score"], f"{p.get('risk_score', 15)}%", delta="-2%")
            col_m2.metric(t["accuracy"], f"{confidence}%", delta="+5%")
            col_m3.metric(t["total_days"], f"{total_days} Days")
            col_m4.metric(t["total_cost"], f"${total_cost:,}")
            
            st.divider()
            
            if tasks:
                df = pd.DataFrame(tasks)
                g_col1, g_col2 = st.columns(2)
                
                with g_col1:
                    fig_scatter = px.scatter(df, x="days", y="cost", size="cost", color="priority", template="plotly_dark")
                    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                with g_col2:
                    fig_bar = px.bar(df, x="days", y="title", color="priority", orientation='h', template="plotly_dark")
                    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("💡 Please generate an architecture plan first.")

    with tab3:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            st.subheader("📦 Export Documents")
            st.code(f"Digital HMAC Signature: {p.get('signature')}", language="json")
            
            ec1, ec2, ec3 = st.columns(3)
            ec1.download_button(t["export_json"], json.dumps(p, ensure_ascii=False, indent=2), "plan.json", "application/json", use_container_width=True)
            ec2.download_button(t["export_excel"], ExportEngine.build_excel(p.get("tasks", [])), "plan.xlsx", use_container_width=True)
            if REPORTLAB_AVAILABLE:
                ec3.download_button(t["export_pdf"], ExportEngine.build_pdf(p), "plan.pdf", "application/pdf", use_container_width=True)
        else:
            st.info("No plan generated to export.")

if __name__ == "__main__":
    main()
