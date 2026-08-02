#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX PRO ENTERPRISE ARCHITECTURE v7.0 - ULTIMATE SaaS PLATFORM
تحديث UI/UX: تحسين الواجهات الزجاجية، إصلاح القائمة الجانبية وإضافة تأكيد كلمة المرور
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
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# ----------------- Optional Heavy Dependencies -----------------
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =====================================================================
# 1. TRANSLATION DICTIONARY ENGINE
# =====================================================================
TRANSLATIONS = {
    "ar": {
        "title": "🧠 PHOENIX PRO ENTERPRISE",
        "subtitle": "منصة الهندسة المعمارية وإدارة المشاريع المشفرة",
        "login_tab": "🔑 تسجيل الدخول",
        "signup_tab": "📝 حساب جديد",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "full_name": "الاسم الكامل / المنظمة",
        "login_btn": "تسجيل الدخول",
        "signup_btn": "إنشاء الحساب",
        "logout": "🚪 تسجيل الخروج",
        "user": "المستخدم",
        "credits": "⚡ المحاولات المتبقية",
        "plan": "نوع الاشتراك",
        "gemini_key": "🔑 مفتاح Gemini API",
        "tg_title": "📲 إشعارات Telegram",
        "email_title": "📧 إشعارات البريد (SMTP)",
        "sub_title": "💳 الترقية والتفعيل",
        "tab_gen": "🚀 توليد الخطة والهندسة",
        "tab_analytics": "📊 التحليلات التفاعلية",
        "tab_dashboard": "🗄️ الأرشيف ومشاريعي",
        "tab_export": "📦 التصدير والتوثيق",
        "client": "🏢 اسم العميل / المشروع",
        "budget": "💰 الميزانية المقدرة",
        "timeline": "⏱️ الجدول الزمني",
        "tech": "🛠️ التقنيات المفضلة",
        "scope": "📌 وصف ونطاق المشروع",
        "generate_btn": "⚡ بدء التوليد والتوقيع المشفر",
        "risk_score": "🚨 درجة المخاطرة",
        "accuracy": "🎯 نسبة الثقة والاعتماد",
        "total_days": "⏱️ إجمالي الأيام",
        "total_cost": "💰 التكلفة الكلية التقديرية",
        "export_json": "📦 تصدير JSON المشفر",
        "export_excel": "📊 تصدير جدول Excel",
        "export_pdf": "📄 تصدير تقرير PDF",
        "activate_code": "رمز التفعيل / الكوبون",
        "activate_btn": "تفعيل الكود",
        "monthly": "🗓️ شهري ($29)",
        "yearly": "⭐ سنوي ($290)"
    },
    "en": {
        "title": "🧠 PHOENIX PRO ENTERPRISE",
        "subtitle": "Enterprise Architecture & Encrypted Systems Platform",
        "login_tab": "🔑 Login",
        "signup_tab": "📝 Sign Up",
        "email": "Email Address",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "full_name": "Full Name / Organization",
        "login_btn": "Sign In",
        "signup_btn": "Create Account",
        "logout": "🚪 Logout",
        "user": "User",
        "credits": "⚡ Remaining Credits",
        "plan": "Current Plan",
        "gemini_key": "🔑 Gemini API Key",
        "tg_title": "📲 Telegram Alerts",
        "email_title": "📧 Email Alerts (SMTP)",
        "sub_title": "💳 Subscription & Plans",
        "tab_gen": "🚀 Generate Architecture",
        "tab_analytics": "📊 Interactive Analytics",
        "tab_dashboard": "🗄️ Projects Archive",
        "tab_export": "📦 Secure Export",
        "client": "🏢 Client / Project Name",
        "budget": "💰 Estimated Budget",
        "timeline": "⏱️ Target Timeline",
        "tech": "🛠️ Preferred Tech Stack",
        "scope": "📌 Project Scope & Vision",
        "generate_btn": "⚡ Generate & Sign Document",
        "risk_score": "🚨 Risk Score",
        "accuracy": "🎯 Confidence Rate",
        "total_days": "⏱️ Total Duration",
        "total_cost": "💰 Estimated Total Cost",
        "export_json": "📦 Export Signed JSON",
        "export_excel": "📊 Export Excel Sheet",
        "export_pdf": "📄 Export PDF Document",
        "activate_code": "Activation Code",
        "activate_btn": "Activate Code",
        "monthly": "🗓️ Monthly ($29)",
        "yearly": "⭐ Yearly ($290)"
    }
}

# =====================================================================
# 2. SECURITY & INTEGRITY ENGINE
# =====================================================================
class VaultSecurity:
    HMAC_KEY = os.getenv("HMAC_KEY", secrets.token_hex(32))

    @classmethod
    def sign_payload(cls, payload: dict) -> str:
        clean_payload = {k: v for k, v in payload.items() if k not in ["signature", "timestamp"]}
        payload_str = json.dumps(clean_payload, sort_keys=True)
        return hmac.new(cls.HMAC_KEY.encode(), payload_str.encode(), hashlib.sha512).hexdigest()[:32]

    @classmethod
    def hash_password(cls, password: str) -> str:
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode(), salt).decode()
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        if BCRYPT_AVAILABLE and hashed.startswith("$2b$"):
            try:
                return bcrypt.checkpw(password.encode(), hashed.encode())
            except Exception:
                return False
        return hashlib.sha256(password.encode()).hexdigest() == hashed

# =====================================================================
# 3. DATABASE MANAGEMENT ENGINE
# =====================================================================
class DatabaseManager:
    @staticmethod
    def get_db_connection():
        if not PYMYSQL_AVAILABLE:
            return None
        try:
            conn_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
            db_user = os.environ.get('DB_USER')
            db_pass = os.environ.get('DB_PASSWORD')
            db_name = os.environ.get('DB_NAME')

            if conn_name and db_user and db_pass and db_name:
                return pymysql.connect(
                    unix_socket=f"/cloudsql/{conn_name}",
                    user=db_user,
                    password=db_pass,
                    database=db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
        except Exception as e:
            logging.error(f"CloudSQL Connection Fail: {e}")
        return None

    @classmethod
    def save_project(cls, user_id: str, plan_data: dict) -> bool:
        conn = cls.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO projects (user_id, client_name, summary, budget_range, tech_stack, signature, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                    (
                        user_id,
                        plan_data.get('client'),
                        plan_data.get('executive_summary'),
                        plan_data.get('budget_str'),
                        json.dumps(plan_data.get('tech_stack', [])),
                        plan_data.get('signature')
                    )
                )
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logging.error(f"DB Save Error: {e}")
        
        if "local_db_projects" not in st.session_state:
            st.session_state.local_db_projects = []
        st.session_state.local_db_projects.append(plan_data)
        return True

    @classmethod
    def fetch_user_projects(cls, user_id: str) -> list:
        conn = cls.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute("SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
                rows = cursor.fetchall()
                conn.close()
                return rows
            except Exception as e:
                logging.error(f"DB Fetch Error: {e}")
        return st.session_state.get("local_db_projects", [])

# =====================================================================
# 4. COMMERCE & NOTIFICATION ENGINE
# =====================================================================
class CommercialEngine:
    @staticmethod
    def send_telegram(plan: dict, bot_token: str, chat_id: str) -> bool:
        if not bot_token or not chat_id: return False
        msg = (
            f"🚀 *مشروع جديد PHOENIX PRO*\n\n"
            f"👤 *العميل:* {plan.get('client')}\n"
            f"💰 *الميزانية:* {plan.get('budget_str')}\n"
            f"📅 *المدة:* {plan.get('timeline')}\n"
            f"🔑 *التوقيع الرقمي:* `{plan.get('signature', 'N/A')}`\n"
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
        if not smtp_user or not smtp_pass or not recipient_email: return False
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
            <div dir="rtl" style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #f1f5f9; padding: 20px; border-radius: 12px; border: 1px solid #1e293b;">
                <h2 style="color: #3b82f6;">🚀 PHOENIX PRO - الخطة الهندسية المعمارية</h2>
                <p><b>🏛️ العميل:</b> {plan.get('client')}</p>
                <p><b>💰 الميزانية:</b> {plan.get('budget_str')}</p>
                <p><b>📅 المدة الزمنية:</b> {plan.get('timeline')}</p>
                <p><b>🔑 التوقيع الرقمي (HMAC):</b> <code>{plan.get('signature')}</code></p>
                <hr style="border: 1px solid #334155;">
                <h3>📝 الملخص التنفيذي:</h3>
                <p style="line-height: 1.6;">{plan.get('executive_summary')}</p>
                <hr style="border: 1px solid #334155;">
                <h3>🎯 المهام التنفيذية:</h3>
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
# 5. AI GENERATION ENGINE
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        lang_instruction = "اللغة العربية" if lang == "ar" else "English"

        prompt = f"""
        You are a Chief Systems Architect at PHOENIX PRO ENTERPRISE. Analyze this project requirements:
        - Client: {req['client']}
        - Description & Scope: {req['desc']}
        - Budget: {req['budget']}
        - Timeline: {req['timeline']}
        - Preferred Technologies: {req['tech']}

        Output STRICTLY a valid JSON object in {lang_instruction} with this schema:
        {{
            "client": "{req['client']}",
            "executive_summary": "Comprehensive analytical summary here...",
            "tech_stack": ["Tech 1", "Tech 2"],
            "budget_str": "{req['budget']}",
            "timeline": "{req['timeline']}",
            "risk_score": 20,
            "confidence_score": 92,
            "tasks": [
                {{"title": "Task 1: System Design", "description": "Details...", "days": 5, "cost": 1200, "priority": "High"}},
                {{"title": "Task 2: API & Core Engine", "description": "Details...", "days": 10, "cost": 2400, "priority": "Medium"}}
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
            raise ValueError(f"فشل معالجة التوليد الذكي: {str(e)}")

# =====================================================================
# 6. ANALYTICS & VISUAL ENGINE
# =====================================================================
class AnalyticsEngine:
    @staticmethod
    def compute_metrics(plan: dict) -> dict:
        tasks = plan.get("tasks", [])
        total_days = sum(t.get('days', 0) for t in tasks)
        total_cost = sum(t.get('cost', 0) for t in tasks)
        total_tasks = len(tasks)
        
        high_priority = sum(1 for t in tasks if t.get('priority') == 'High')
        high_ratio = high_priority / total_tasks if total_tasks else 0
        long_tasks = sum(1 for t in tasks if t.get('days', 0) > 5)
        long_ratio = long_tasks / total_tasks if total_tasks else 0

        risk_score = plan.get("risk_score", min(100, int((high_ratio * 0.6 + long_ratio * 0.4) * 100)))
        confidence_score = plan.get("confidence_score", max(50, min(99, 100 - int(risk_score * 0.35))))

        return {
            "total_days": total_days,
            "total_cost": total_cost,
            "total_tasks": total_tasks,
            "risk_score": risk_score,
            "confidence_score": confidence_score
        }

    @staticmethod
    def create_semi_gauge(val: float, title: str, color: str):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'suffix': "%", 'font': {'size': 26, 'color': "#ffffff", 'family': "Cairo"}},
            title={'text': f"<b>{title}</b>", 'font': {'size': 14, 'color': "#94a3b8", 'family': "Cairo"}},
            gauge={
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': color, 'thickness': 0.35},
                'bgcolor': "rgba(255, 255, 255, 0.05)",
                'borderwidth': 0,
                'steps': [{'range': [0, 100], 'color': 'rgba(255, 255, 255, 0.03)'}],
            }
        ))
        fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=0),
            height=160,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

# =====================================================================
# 7. EXPORT ENGINE
# =====================================================================
class ExportEngine:
    @staticmethod
    def build_pdf(data: dict) -> bytes:
        if not REPORTLAB_AVAILABLE: return b""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>Enterprise Architecture Document: {data.get('client')}</b>", styles['Title']), Spacer(1, 12)]

        table_data = [["Task Title", "Days", "Cost ($)", "Priority"]]
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
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Architecture_Tasks")
        return buffer.getvalue()

# =====================================================================
# 8. SESSION MANAGEMENT & CSS FIXES ENGINE (GLASSMORPHISM ADVANCED)
# =====================================================================
def init_session():
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "eng.alhiadri2020@gmail.com": {
                "name": "AYAD FAISAL ABDO MOHAMMED",
                "password": VaultSecurity.hash_password("123456"),
                "credits": 10,
                "plan_status": "Enterprise Pro"
            }
        }
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if "current_user" not in st.session_state: st.session_state.current_user = None
    if "selected_plan" not in st.session_state: st.session_state.selected_plan = None
    if "lang" not in st.session_state: st.session_state.lang = "ar"
    if "theme" not in st.session_state: st.session_state.theme = "dark"

def inject_custom_css():
    lang = st.session_state.lang
    theme = st.session_state.theme
    direction = "rtl" if lang == "ar" else "ltr"
    align_text = "right" if lang == "ar" else "left"

    if theme == "dark":
        bg_main, bg_sidebar = "#0b0f19", "#0f172a"
        text_color = "#f8fafc"
        label_color = "#cbd5e1"
        input_bg = "rgba(30, 41, 59, 0.65)"
        input_border = "rgba(255, 255, 255, 0.18)"
        input_focus_border = "#3b82f6"
    else:
        bg_main, bg_sidebar = "#f8fafc", "#ffffff"
        text_color = "#0f172a"
        label_color = "#334155"
        input_bg = "rgba(255, 255, 255, 0.85)"
        input_border = "rgba(15, 23, 42, 0.15)"
        input_focus_border = "#2563eb"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700&display=swap');

        /* 🔴 1. FIX SIDEBAR OVERLAY & MOBILE OVERFLOW */
        [data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
            z-index: 99999 !important;
            white-space: normal !important;
        }}
        
        [data-testid="stSidebar"] * {{
            word-break: normal !important;
            overflow-wrap: break-word !important;
        }}

        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stSidebarHeader"] *,
        [data-testid="stIcon"],
        [data-baseweb="icon"] {{
            font-family: 'Material Icons', 'Material Symbols Outlined' !important;
            direction: ltr !important;
        }}

        /* 🔵 2. BASE LAYOUT & TYPOGRAPHY */
        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Cairo', 'Inter', sans-serif !important;
            direction: {direction};
            text-align: {align_text};
            background-color: {bg_main} !important;
            color: {text_color} !important;
        }}

        /* 🟢 3. HIGH-CONTRAST GLASSMORPHISM INPUT FIELDS & LABELS */
        .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {{
            color: {label_color} !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            margin-bottom: 6px !important;
        }}

        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {{
            background: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 12px !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.25s ease-in-out !important;
        }}

        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within, div[data-baseweb="textarea"]:focus-within {{
            border-color: {input_focus_border} !important;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.4) !important;
        }}

        input, textarea {{
            color: {text_color} !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
        }}

        /* 🟣 4. MODERN HERO HEADER & CARDS */
        .hero-header {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            padding: 10px 0;
            line-height: 1.3;
        }}

        .stat-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(10px);
            margin-bottom: 12px;
        }}
        .stat-card .val {{
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-card .lbl {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 4px;
        }}

        .plan-box {{
            background: {input_bg};
            border: 1px solid {input_focus_border};
            border-radius: 14px;
            padding: 20px;
            margin-top: 15px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}

        .pay-btn {{
            display: block;
            background: linear-gradient(90deg, #2563eb, #4f46e5);
            color: white !important;
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: bold;
            margin-bottom: 5px;
        }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 9. INTERACTIVE HITL TASK EDITOR MODULE
# =====================================================================
def render_hitl_task_editor(plan: dict):
    st.markdown("### ✏️ تعديل ومراجعة المهام المباشرة (HITL Engine)")
    st.caption("يمكنك تعديل أي قيمة، وسيقوم المحرك بإعادة الحسابات والتوقيع الرقمي فوراً.")

    tasks = plan.get("tasks", [])
    updated_tasks = []

    for idx, task in enumerate(tasks):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                t_title = st.text_input(f"عنوان المهمة #{idx+1}", value=task.get('title'), key=f"t_title_{idx}")
            with col2:
                t_days = st.number_input(f"الأيام", min_value=1, value=task.get('days', 1), key=f"t_days_{idx}")
            with col3:
                t_cost = st.number_input(f"التكلفة ($)", min_value=0, value=task.get('cost', 100), step=50, key=f"t_cost_{idx}")
            with col4:
                p_opts = ["High", "Medium", "Low"]
                t_priority = st.selectbox(f"الأولوية", p_opts, index=p_opts.index(task.get('priority', 'Medium')), key=f"t_prio_{idx}")

            updated_tasks.append({
                "title": t_title,
                "days": t_days,
                "cost": t_cost,
                "priority": t_priority,
                "description": task.get("description", "")
            })

    if st.button("🔄 إعادة حساب التوقيع الرقمي والتحليلات فوراً", type="primary", use_container_width=True):
        plan["tasks"] = updated_tasks
        plan["signature"] = VaultSecurity.sign_payload(plan)
        st.session_state.selected_plan = plan
        st.success("✅ تم تحديث الخطة، التوقيع الرقمي المشفر، وإحصائيات المشروع بنجاح!")
        st.rerun()

# =====================================================================
# 10. AUTHENTICATION MODULE
# =====================================================================
def render_auth_page():
    t = TRANSLATIONS[st.session_state.lang]
    inject_custom_css()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div class="hero-header">{t["title"]}</div>', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs([t["login_tab"], t["signup_tab"]])

        with tab_login:
            email = st.text_input(t["email"], key="login_email")
            password = st.text_input(t["password"], type="password", key="login_pass")
            if st.button(t["login_btn"], use_container_width=True, type="primary"):
                user_record = st.session_state.users_db.get(email)
                if user_record and VaultSecurity.verify_password(password, user_record["password"]):
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_record
                    st.session_state.current_user["email"] = email
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")

        with tab_signup:
            new_name = st.text_input(t["full_name"], key="signup_name")
            new_email = st.text_input(t["email"], key="signup_email")
            new_pass = st.text_input(t["password"], type="password", key="signup_pass")
            confirm_pass = st.text_input(t["confirm_password"], type="password", key="signup_confirm_pass")
            
            if st.button(t["signup_btn"], use_container_width=True):
                if new_email in st.session_state.users_db:
                    st.error("البريد الإلكتروني مسجل بالفعل.")
                elif new_pass != confirm_pass:
                    st.error("كلمتا المرور غير متطابقتين.")
                elif new_name and new_email and new_pass:
                    st.session_state.users_db[new_email] = {
                        "name": new_name,
                        "password": VaultSecurity.hash_password(new_pass),
                        "credits": 5,
                        "plan_status": "Free Trial (5 Credits)"
                    }
                    st.success("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")

# =====================================================================
# 11. MAIN APPLICATION ENTRY
# =====================================================================
def main():
    st.set_page_config(page_title="PHOENIX PRO ENTERPRISE", page_icon="🧠", layout="wide")
    init_session()
    inject_custom_css()

    if not st.session_state.authenticated:
        render_auth_page()
        return

    t = TRANSLATIONS[st.session_state.lang]
    user = st.session_state.current_user

    # ----------------- SIDEBAR COMMAND -----------------
    with st.sidebar:
        st.markdown("<h3 style='text-align:center;'>⚙️ PHOENIX COMMAND</h3>", unsafe_allow_html=True)

        c_lang, c_theme = st.columns(2)
        with c_lang:
            if st.button("🌐 " + ("English" if st.session_state.lang == "ar" else "العربية"), use_container_width=True):
                st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
                st.rerun()
        with c_theme:
            if st.button("☀️/🌙", use_container_width=True):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                st.rerun()

        st.divider()
        st.caption(f"👤 {t['user']}: {user.get('name')}")
        st.caption(f"📧 {t['email']}: {user.get('email')}")
        st.markdown(f"**{t['credits']}:** `{user.get('credits', 0)}`")
        st.caption(f"{t['plan']}: {user.get('plan_status')}")

        if st.button(t["logout"], use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

        st.divider()
        api_key = st.text_input(t["gemini_key"], type="password", value=os.getenv("GEMINI_API_KEY", ""))

        st.divider()
        st.subheader(t["tg_title"])
        tg_bot_token = st.text_input("Bot Token", type="password", value=os.getenv("TELEGRAM_BOT_TOKEN", ""))
        tg_chat_id = st.text_input("Chat ID", value=os.getenv("TELEGRAM_CHAT_ID", ""))

        st.divider()
        st.subheader(t["email_title"])
        smtp_user = st.text_input("SMTP User", value=os.getenv("SMTP_USER", ""))
        smtp_pass = st.text_input("SMTP Pass", type="password", value=os.getenv("SMTP_PASS", ""))

        st.divider()
        st.subheader(t["sub_title"])
        pay_email = st.text_input(t["email"], value=user.get('email'), key="billing_email")
        
        col_m, col_y = st.columns(2)
        with col_m:
            st.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email, "monthly")}" target="_blank" class="pay-btn">{t["monthly"]}</a>', unsafe_allow_html=True)
        with col_y:
            st.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email, "yearly")}" target="_blank" class="pay-btn">{t["yearly"]}</a>', unsafe_allow_html=True)

        act_code = st.text_input(t["activate_code"], type="password")
        if st.button(t["activate_btn"], use_container_width=True):
            if act_code in ["PRO2026", "PHOENIX"]:
                user["credits"] = 9999
                user["plan_status"] = "Unlimited Developer"
                st.success("تم تفعيل الاشتراك الخارق بنجاح!")
                st.rerun()
            elif act_code in ["MONTHLY2026", "MONTHLY"]:
                user["credits"] += 30
                user["plan_status"] = "Monthly Pro"
                st.success("تم تفعيل الاشتراك الشهري (+30 محاولة)!")
                st.rerun()
            else:
                st.error("رمز غير صالح.")

    # ----------------- MAIN DASHBOARD -----------------
    st.markdown(f'<div class="hero-header">{t["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#94a3b8;'>{t['subtitle']}</p>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([t["tab_gen"], t["tab_analytics"], t["tab_dashboard"], t["tab_export"]])

    # 🚀 TAB 1: GENERATION & HITL EDITING
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            client = st.text_input(t["client"], value="مؤسسة التقنية العالية" if st.session_state.lang == "ar" else "HighTech Corp")
            budget = st.text_input(t["budget"], value="10000 - 15000 $")
        with c2:
            timeline = st.text_input(t["timeline"], value="8 أسابيع" if st.session_state.lang == "ar" else "8 Weeks")
            tech = st.text_input(t["tech"], value="Flutter, Node.js, PostgreSQL, Supabase")

        desc = st.text_area(t["scope"], value="تطوير تطبيق متكامل للخدمات اللوجستية وتتبع الشحنات مع إشعارات فورية ولوحة تحليلات سحابية.", height=120)

        if st.button(t["generate_btn"], type="primary", use_container_width=True):
            if not api_key:
                st.error("يرجى إدخال مفتاح Gemini API في القائمة الجانبية.")
            elif user.get("credits", 0) <= 0:
                st.error("رصيدك غير كافٍ. يرجى الترقية.")
            else:
                with st.spinner("جاري التحليل الهندسي والتوقيع المشفر..."):
                    try:
                        req_payload = {"client": client, "budget": budget, "timeline": timeline, "tech": tech, "desc": desc}
                        plan = PhoenixAI.generate_architecture(api_key, req_payload, lang=st.session_state.lang)

                        DatabaseManager.save_project(user.get("email"), plan)
                        st.session_state.selected_plan = plan
                        user["credits"] -= 1

                        if tg_bot_token and tg_chat_id: CommercialEngine.send_telegram(plan, tg_bot_token, tg_chat_id)
                        if smtp_user and smtp_pass: CommercialEngine.send_email(plan, user.get("email"), smtp_user, smtp_pass)

                        st.success(f"✅ تم إنشاء وتوقيع الخطة الرقمية بنجاح! المتبقي: {user['credits']}")
                        st.rerun()
                    except Exception as err:
                        st.error(str(err))

        if st.session_state.selected_plan:
            plan = st.session_state.selected_plan
            st.divider()
            
            st.markdown(f"""
            <div class="plan-box">
                <h4>🏛️ {plan.get('client')}</h4>
                <p><b>📅 Date:</b> {plan.get('timestamp')}</p>
                <p><b>🔑 Digital Signature (HMAC):</b> <code>{plan.get('signature')}</code></p>
                <hr style="border-color:rgba(255, 255, 255, 0.15);">
                <h5>📝 Executive Summary:</h5>
                <p style="line-height:1.7;">{plan.get('executive_summary')}</p>
                <hr style="border-color:rgba(255, 255, 255, 0.15);">
                <h5>🛠️ Tech Stack:</h5>
                <p><code>{"  |  ".join(plan.get('tech_stack', []))}</code></p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br/>", unsafe_allow_html=True)

            render_hitl_task_editor(plan)

    # 📊 TAB 2: ADVANCED INTERACTIVE ANALYTICS
    with tab2:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            metrics = AnalyticsEngine.compute_metrics(p)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="lbl">{t['total_cost']}</div>
                    <div class="val">${metrics['total_cost']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="lbl">{t['total_days']}</div>
                    <div class="val">{metrics['total_days']} {('أيام' if st.session_state.lang == 'ar' else 'Days')}</div>
                </div>
                """, unsafe_allow_html=True)

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                risk_color = "#ef4444" if metrics['risk_score'] > 60 else "#f59e0b" if metrics['risk_score'] > 30 else "#10b981"
                fig_risk = AnalyticsEngine.create_semi_gauge(metrics['risk_score'], t['risk_score'], risk_color)
                st.plotly_chart(fig_risk, use_container_width=True)

            with col_g2:
                fig_conf = AnalyticsEngine.create_semi_gauge(metrics['confidence_score'], t['accuracy'], "#3b82f6")
                st.plotly_chart(fig_conf, use_container_width=True)

            st.divider()

            df_tasks = pd.DataFrame(p.get("tasks", []))
            if not df_tasks.empty:
                g_col1, g_col2 = st.columns(2)
                with g_col1:
                    fig_pie = px.pie(
                        df_tasks, 
                        names="priority", 
                        values="cost", 
                        title="<b>توزيع التكلفة حسب الأولوية</b>", 
                        hole=0.6,
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#0b0f19', width=2)))
                    fig_pie.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#f1f5f9", family="Cairo"),
                        showlegend=False,
                        height=280
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with g_col2:
                    fig_bar = px.bar(
                        df_tasks, 
                        x="days", 
                        y="title", 
                        color="priority", 
                        orientation='h', 
                        title="<b>المدد الزمنية للمهام</b>",
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
                    fig_bar.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#f1f5f9", family="Cairo"),
                        xaxis=dict(title="الأيام", showgrid=False),
                        yaxis=dict(title="", showgrid=False),
                        height=280
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("💡 يرجى توليد أو اختيار مشروع أولاً.")

    # 🗄️ TAB 3: PROJECTS DASHBOARD & ARCHIVE
    with tab3:
        st.subheader(t["tab_dashboard"])
        projects = DatabaseManager.fetch_user_projects(user.get("email"))
        if projects:
            st.dataframe(pd.DataFrame(projects), use_container_width=True)
        else:
            st.info("لا توجد مشاريع محفوظة حالياً.")

    # 📦 TAB 4: SECURE EXPORT
    with tab4:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            st.subheader(t["tab_export"])
            st.code(f"Digital HMAC Signature: {p.get('signature')}", language="json")

            ec1, ec2, ec3 = st.columns(3)
            ec1.download_button(t["export_json"], json.dumps(p, ensure_ascii=False, indent=2), "signed_plan.json", "application/json", use_container_width=True)
            ec2.download_button(t["export_excel"], ExportEngine.build_excel(p.get("tasks", [])), "plan_excel.xlsx", use_container_width=True)
            if REPORTLAB_AVAILABLE:
                ec3.download_button(t["export_pdf"], ExportEngine.build_pdf(p), "architecture_report.pdf", "application/pdf", use_container_width=True)
        else:
            st.info("لا توجد خطة نشطة للتصدير.")

if __name__ == "__main__":
    main()
