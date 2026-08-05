#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & MIHNA AGENT PRO ENTERPRISE - HYBRID ULTIMATE SaaS
النسخة المدمجة الكاملة والقصوى: تجمع بين قوة Cloud SQL وGemini 2.5 AI والتشفير،
مع واجهة التحليلات البصرية 5D، معالجة PDF العربية، ومحاكاة وكيل الدفع.
===============================================================================
"""

import os
import re
import io
import json
import uuid
import hashlib
import hmac
import time
import secrets
import logging
import urllib.parse
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import requests

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
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import arabic_reshaper
    from bidi.algorithm import get_display
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =====================================================================
# 1. CONFIGURATION & CONSTANTS
# =====================================================================
APP_TITLE = "PHOENIX & MIHNA AGENT PRO - ENTERPRISE"
PAYMENT_LINK_MONTHLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly"
PAYMENT_LINK_YEARLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly"

st.set_page_config(
    page_title="وكيل مهنة PRO | PHOENIX Enterprise",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# 2. SECURITY & CLOUD DATABASE ENGINE (FROM CODE 1)
# =====================================================================
class VaultSecurity:
    HMAC_KEY = os.getenv("HMAC_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_DEFAULT")

    @classmethod
    def sign_payload(cls, payload: dict) -> str:
        clean_payload = {k: v for k, v in payload.items() if k not in ["signature", "timestamp"]}
        payload_str = json.dumps(clean_payload, sort_keys=True, ensure_ascii=False)
        return hmac.new(cls.HMAC_KEY.encode(), payload_str.encode(), hashlib.sha512).hexdigest()

    @classmethod
    def verify_signature(cls, payload: dict, signature: str) -> bool:
        if not signature: return False
        expected = cls.sign_payload(payload)
        return hmac.compare_digest(expected, signature)

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

class CloudSQLUtils:
    @staticmethod
    def get_db_connection():
        if not PYMYSQL_AVAILABLE: return None
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
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
        except Exception as e:
            logging.error(f"Database connection error: {e}")
        return None

    @classmethod
    def get_user_by_email(cls, email: str) -> dict:
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                    user = cursor.fetchone()
                conn.close()
                return user
            except Exception as e:
                logging.error(f"CloudSQL Get User Error: {e}")
        return st.session_state.get("users_db", {}).get(email)

    @classmethod
    def register_user(cls, name: str, email: str, hashed_pass: str, credits: int = 5, plan_status: str = "Free Trial") -> bool:
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO users (name, email, password, credits, plan_status, created_at)
                           VALUES (%s, %s, %s, %s, %s, NOW())""",
                        (name, email, hashed_pass, credits, plan_status)
                    )
                conn.close()
                return True
            except Exception as e:
                logging.error(f"CloudSQL Register Error: {e}")
        
        if "users_db" not in st.session_state: st.session_state.users_db = {}
        st.session_state.users_db[email] = {
            "name": name, "password": hashed_pass, "credits": credits, "plan_status": plan_status
        }
        return True

    @classmethod
    def update_user_credits(cls, email: str, new_credits: int, new_status: str = None) -> bool:
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    if new_status:
                        cursor.execute("UPDATE users SET credits = %s, plan_status = %s WHERE email = %s", (new_credits, new_status, email))
                    else:
                        cursor.execute("UPDATE users SET credits = %s WHERE email = %s", (new_credits, email))
                conn.close()
                return True
            except Exception as e:
                logging.error(f"CloudSQL Update Error: {e}")
        
        if email in st.session_state.get("users_db", {}):
            st.session_state.users_db[email]["credits"] = new_credits
            if new_status: st.session_state.users_db[email]["plan_status"] = new_status
        return True

# =====================================================================
# 3. REAL AI GENERATION ENGINE (GEMINI INTEGRATION)
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        if not api_key:
            # Fallback Dynamic Generator if Key is Missing
            b = req['budget']
            t = req['timeline']
            return {
                "project_name": req['client'],
                "domain": req['tech'],
                "budget": b,
                "target_days": t,
                "executive_summary": f"خطة هندسية معمارية شاملة لمشروع {req['client']} تعتمد تقنيات {req['tech']}.",
                "risk_score": 22,
                "confidence_score": 94,
                "tasks": [
                    {"id": 1, "task": "تحليل المتطلبات وهندسة معمارية للنظام", "days": max(1, int(t*0.15)), "cost": int(b*0.15), "priority": "High", "phase": "Planning"},
                    {"id": 2, "task": "تصميم قواعد البيانات والـ Schemas", "days": max(1, int(t*0.20)), "cost": int(b*0.20), "priority": "High", "phase": "Backend"},
                    {"id": 3, "task": "تطوير الواجهات وتكامل APIs", "days": max(1, int(t*0.35)), "cost": int(b*0.35), "priority": "Medium", "phase": "Frontend"},
                    {"id": 4, "task": "اختبار الأمان والأداء والانتشار Deploy", "days": max(1, int(t*0.30)), "cost": int(b*0.30), "priority": "Low", "phase": "DevOps"}
                ]
            }

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        lang_instruction = "اللغة العربية" if lang == "ar" else "English"

        prompt = f"""
        Analyze the following IT project architecture requirements and generate a structured JSON object in {lang_instruction}:
        - Client/Project Name: {req['client']}
        - Description: {req['desc']}
        - Budget ($): {req['budget']}
        - Timeline (Days): {req['timeline']}
        - Technology Stack: {req['tech']}

        Requirements for Output JSON ONLY (No markdown extra text):
        {{
            "project_name": "{req['client']}",
            "domain": "{req['tech']}",
            "budget": {req['budget']},
            "target_days": {req['timeline']},
            "executive_summary": "Detailed strategic architectural plan summary...",
            "risk_score": 25,
            "confidence_score": 92,
            "tasks": [
                {{"id": 1, "task": "Task name", "days": 5, "cost": 1000, "priority": "High", "phase": "Planning"}},
                {{"id": 2, "task": "Task name 2", "days": 10, "cost": 2500, "priority": "High", "phase": "Core"}}
            ]
        }}
        """
        response = model.generate_content(prompt)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        data = json.loads(match.group() if match else response.text)
        data["signature"] = VaultSecurity.sign_payload(data)
        data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return data

# =====================================================================
# 4. EXPORT ENGINE (EXCEL & ARABIC PDF FIXED)
# =====================================================================
class ExportEngine:
    @staticmethod
    def build_excel(tasks: list) -> bytes:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Architecture_Tasks")
        return buffer.getvalue()

    @staticmethod
    def build_pdf(plan: dict) -> bytes:
        if not REPORTLAB_AVAILABLE: return b""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        def reshape(text):
            try:
                return get_display(arabic_reshaper.reshape(str(text)))
            except Exception:
                return str(text)

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, alignment=2)

        story.append(Paragraph(reshape(f"خطة مشروع: {plan.get('project_name')}"), title_style))
        story.append(Spacer(1, 15))
        
        info_text = f"الميزانية: ${plan.get('budget')} | المدة: {plan.get('target_days')} يوم | T-Signature: {plan.get('signature', '')[:20]}..."
        story.append(Paragraph(reshape(info_text), body_style))
        story.append(Spacer(1, 15))

        table_data = [[reshape("المرحلة"), reshape("الأولوية"), reshape("التكلفة ($)"), reshape("المدة (يوم)"), reshape("اسم المهمة")]]
        for t in plan.get("tasks", []):
            table_data.append([
                reshape(t.get('phase', 'Core')),
                reshape(t.get('priority', '')),
                str(t.get('cost', 0)),
                str(t.get('days', 0)),
                reshape(t.get('task', ''))
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
        ]))
        story.append(table)
        doc.build(story)
        return buffer.getvalue()

# =====================================================================
# 5. INITIALIZATION & STYLING
# =====================================================================
def init_session():
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "eng.alhiadri2020@gmail.com": {
                "name": "AYAD FAISAL ABDO MOHAMMED",
                "password": VaultSecurity.hash_password("123456"),
                "credits": 9999,
                "plan_status": "Enterprise Pro"
            }
        }
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if "current_user" not in st.session_state: st.session_state.current_user = None
    if "current_plan" not in st.session_state: st.session_state.current_plan = None
    if "lang" not in st.session_state: st.session_state.lang = "ar"
    if "theme" not in st.session_state: st.session_state.theme = "dark"
    if "notify_whatsapp" not in st.session_state: st.session_state.notify_whatsapp = "+967700000000"
    if "notify_telegram" not in st.session_state: st.session_state.notify_telegram = "@Ayad_Developer"
    if "payment_logs" not in st.session_state: st.session_state.payment_logs = []

def inject_custom_css():
    bg_main = "#0b0f19" if st.session_state.theme == "dark" else "#f8fafc"
    text_color = "#f8fafc" if st.session_state.theme == "dark" else "#0f172a"
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Cairo', sans-serif !important;
            background-color: {bg_main} !important;
            color: {text_color} !important;
        }}
        div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {{
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
        }}
        .badge-purple {{ background-color: #8B5CF6; color: white; padding: 4px 12px; border-radius: 10px; font-weight: bold; font-size: 12px; }}
        .badge-green {{ background-color: #10B981; color: white; padding: 4px 12px; border-radius: 10px; font-weight: bold; font-size: 12px; }}
        .metric-card {{
            background-color: #1e293b;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #3b82f6;
            margin-bottom: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 6. APPLICATION CONTROLLER
# =====================================================================
def main():
    init_session()
    inject_custom_css()

    # --- AUTHENTICATION SCREEN ---
    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔐 منصة PHOENIX & MIHNA ENTERPRISE</h1>", unsafe_allow_html=True)
        t_login, t_signup = st.tabs(["🔑 تسجيل الدخول", "📝 حساب جديد"])
        
        with t_login:
            email = st.text_input("البريد الإلكتروني", key="l_email")
            password = st.text_input("كلمة المرور", type="password", key="l_pass")
            if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                user = CloudSQLUtils.get_user_by_email(email)
                if user and VaultSecurity.verify_password(password, user["password"]):
                    st.session_state.authenticated = True
                    st.session_state.current_user = user
                    st.session_state.current_user["email"] = email
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")

        with t_signup:
            s_name = st.text_input("الاسم الكامل", key="s_name")
            s_email = st.text_input("البريد الإلكتروني", key="s_email")
            s_pass = st.text_input("كلمة المرور", type="password", key="s_pass")
            if st.button("إنشاء حساب (5 نقاط مجانية)", use_container_width=True):
                if s_name and s_email and s_pass:
                    hashed = VaultSecurity.hash_password(s_pass)
                    CloudSQLUtils.register_user(s_name, s_email, hashed, credits=5, plan_status="Free Trial")
                    st.success("تم إنشاء الحساب بنجاح! قم بتسجيل الدخول الان.")
        return

    # --- MAIN DASHBOARD (AUTHENTICATED) ---
    user = st.session_state.current_user

    with st.sidebar:
        st.title("🛡️ PHOENIX COMMAND")
        st.caption(f"👤 {user.get('name')}")
        st.caption(f"💳 الرصيد: {user.get('credits')} نقاط")
        st.markdown(f"<span class='badge-purple'>{user.get('plan_status')}</span>", unsafe_allow_html=True)
        st.divider()
        
        api_key = st.text_input("🔑 Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        
        st.divider()
        st.subheader("⚙️ التنبيهات والإعدادات")
        st.session_state.notify_whatsapp = st.text_input("📱 واتساب التنبيهات", value=st.session_state.notify_whatsapp)
        st.session_state.notify_telegram = st.text_input("✈️ تليجرام التنبيهات", value=st.session_state.notify_telegram)
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    st.title("🚀 وكيل مهنة PRO | PHOENIX Enterprise v8.5")
    
    # NAVIGATION TABS (FULL CODE 2 STRUCTURE)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏗️ بناء خطة مشروع", 
        "📊 التحليلات الـ 5D المتقدمة", 
        "✏️ محرر المهام المتقدم", 
        "🤖 وكيل الدفع الذكي (Payment Agent)", 
        "💳 الحساب والاشتراك"
    ])

    # -----------------------------------------------------------------
    # TAB 1: BUILD ARCHITECTURE PLAN (WITH QUICK TEMPLATES)
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("⚡ قوالب مشاريع سريعة (Quick Templates)")
        col_t1, col_t2, col_t3 = st.columns(3)
        
        selected_template = None
        if col_t1.button("🛒 متجر إلكتروني متكامل", use_container_width=True):
            selected_template = {"name": "منصة تجارة إلكترونية", "budget": 8000, "days": 45, "tech": "React, Node.js, PostgreSQL", "desc": "متجر تجارة إلكترونية متعدد التجار مع بوابة دفع وتتبع طلبات."}
        if col_t2.button("🎓 منصة تعليمية وتدريب", use_container_width=True):
            selected_template = {"name": "نظام إدارة التعلم (LMS)", "budget": 6000, "days": 35, "tech": "Flutter, Supabase, WebRTC", "desc": "منصة كورسات تفاعلية وبث مباشر مع شهادات تلقائية."}
        if col_t3.button("🛵 تطبيق توصيل وشحن", use_container_width=True):
            selected_template = {"name": "منصة توصيل وشحن لوجستي", "budget": 12000, "days": 60, "tech": "Flutter, Go, Redis, Cloud SQL", "desc": "تطبيق شحن وتوصيل فوري مع تتبع مباشر عبر الخرائط GPS."}

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("اسم المشروع", value=selected_template['name'] if selected_template else "منصة إدارة المقاولات")
            budget = st.number_input("الميزانية المقدرة ($)", value=selected_template['budget'] if selected_template else 5000)
        with col2:
            tech = st.text_input("المجال والتقنيات", value=selected_template['tech'] if selected_template else "Flutter, Node.js, Cloud SQL")
            days = st.number_input("المدة الزمانية (أيام)", value=selected_template['days'] if selected_template else 30)
            
        scope = st.text_area("نطاق العمل تفصيلياً (Scope of Work)", value=selected_template['desc'] if selected_template else "بناء تطبيق للهواتف مع لوحة تحكم سحابية لإدارة المشاريع والتوقيع الرقمي.")

        if st.button("🚀 توليد وتوقيع الخطة الهندسية عبر AI", type="primary", use_container_width=True):
            if user.get("credits", 0) <= 0:
                st.error("رصيدك غير كافٍ. يرجى الترقية لتوليد خطط جديدة.")
            else:
                with st.spinner("جاري التواصل مع محرك AI وتوقيع الخطة رقمياً..."):
                    req = {"client": p_name, "budget": budget, "timeline": days, "tech": tech, "desc": scope}
                    plan = PhoenixAI.generate_architecture(api_key, req, lang=st.session_state.lang)
                    
                    st.session_state.current_plan = plan
                    user["credits"] -= 1
                    CloudSQLUtils.update_user_credits(user.get("email"), user["credits"])
                    st.success("✅ تم توليد وتوقيع الخطة المعمارية بنجاح!")
                    st.rerun()

        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            st.divider()
            st.markdown(f"### 📄 ملخص الخطة المعمارية: {plan.get('project_name')}")
            st.info(f"🔒 **التوقيع الرقمي HMAC-SHA512:** `{plan.get('signature')}`")
            st.write(f"**الملخص التنفيذي:** {plan.get('executive_summary')}")
            st.dataframe(pd.DataFrame(plan.get("tasks", [])), use_container_width=True)

    # -----------------------------------------------------------------
    # TAB 2: ADVANCED 5D VISUAL ANALYTICS (FULL CODE 2 VISUALS)
    # -----------------------------------------------------------------
    with tab2:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            tasks = plan.get("tasks", [])
            df = pd.DataFrame(tasks)

            # TOP METRIC CARDS
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<div class='metric-card'>💵 <b>إجمالي التكلفة:</b><br>${df['cost'].sum():,}</div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-card'>⏱️ <b>إجمالي الأيام:</b><br>{df['days'].sum()} يوم</div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-card'>🛡️ <b>مؤشر المخاطر:</b><br>{plan.get('risk_score')}%</div>", unsafe_allow_html=True)
            m4.markdown(f"<div class='metric-card'>🎯 <b>نسبة الاعتمادية:</b><br>{plan.get('confidence_score')}%</div>", unsafe_allow_html=True)

            st.divider()
            c_r1, c_r2 = st.columns(2)
            
            with c_r1:
                st.markdown("### 🕸️ تقييم أبعاد المشروع (5D Radar Risk)")
                radar_categories = ['تعقيد النطاق', 'الأمان الرقمي', 'التحكم بالجدول', 'استقرار التكلفة', 'المرونة التقنية']
                fig_radar = go.Figure(go.Scatterpolar(
                    r=[80, 90, 85, 75, plan.get('risk_score', 20)],
                    theta=radar_categories, fill='toself', line=dict(color='#8B5CF6')
                ))
                fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"), height=320)
                st.plotly_chart(fig_radar, use_container_width=True)

            with c_r2:
                st.markdown("### 🎯 مؤشر جدوى المشروع (Feasibility Gauge)")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=plan.get('confidence_score', 90),
                    gauge={'bar': {'color': "#10B981"}, 'axis': {'range': [0, 100]}}
                ))
                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"), height=320)
                st.plotly_chart(fig_gauge, use_container_width=True)

            c_r3, c_r4 = st.columns(2)
            
            with c_r3:
                st.markdown("### ☀️ الهيكلية الموزعة للمهام (Sunburst Hierarchy)")
                fig_sun = px.sunburst(df, path=['priority', 'task'], values='cost', color='cost', color_continuous_scale='Purples')
                fig_sun.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"), height=350)
                st.plotly_chart(fig_sun, use_container_width=True)

            with c_r4:
                st.markdown("### 💧 تدفق تكاليف المراحل (Waterfall Cost Flow)")
                fig_water = go.Figure(go.Waterfall(
                    name="Cost Flow", orientation="v",
                    measure=["relative"] * len(df),
                    x=df['task'], textposition="outside",
                    y=df['cost'], connector={"line": {"color": "rgb(63, 63, 63)"}}
                ))
                fig_water.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"), height=350)
                st.plotly_chart(fig_water, use_container_width=True)
        else:
            st.info("قم بتوليد خطة هندسية أولاً لعرض التحليلات الـ 5D.")

    # -----------------------------------------------------------------
    # TAB 3: TASK EDITOR & DUAL EXPORT (EXCEL / PDF)
    # -----------------------------------------------------------------
    with tab3:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            st.subheader("✏️ تعديل وتحديث مهام الخطة")
            
            edited_df = st.data_editor(
                pd.DataFrame(plan.get("tasks", [])),
                num_rows="dynamic",
                use_container_width=True
            )
            
            if st.button("💾 حفظ التعديلات وإعادة التوقيع الرقمي HMAC", use_container_width=True):
                plan["tasks"] = edited_df.to_dict(orient='records')
                plan["signature"] = VaultSecurity.sign_payload(plan)
                st.session_state.current_plan = plan
                st.success("✅ تم تحديث التوقيع الرقمي وتوثيق التعديلات بنجاح!")
                st.rerun()

            st.divider()
            st.subheader("📥 تصدير التقارير الهندسية")
            col_ex1, col_ex2 = st.columns(2)
            col_ex1.download_button(
                "📊 تصدير Excel مفصل",
                ExportEngine.build_excel(plan.get("tasks", [])),
                "Phoenix_Architecture_Tasks.xlsx",
                use_container_width=True
            )
            col_ex2.download_button(
                "📄 تصدير PDF عربي موثق",
                ExportEngine.build_pdf(plan),
                "Phoenix_Architecture_Report.pdf",
                use_container_width=True
            )
        else:
            st.info("لا توجد خطة معروضة للتعديل.")

    # -----------------------------------------------------------------
    # TAB 4: AI PAYMENT AGENT SIMULATOR (FROM CODE 2)
    # -----------------------------------------------------------------
    with tab4:
        st.subheader("🤖 وكيل معالجة الدفع والاشتراكات الآلي (AI Payment Agent)")
        st.caption("محاكاة واستقبال webhook الاشتراكات وتأكيد معاملات Lemon Squeezy تلقائياً.")
        
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            pay_email = st.text_input("بريد المشترك للتفعيل", value=user.get("email"))
            pay_plan = st.selectbox("باقة الترقية", ["Enterprise Monthly ($29)", "Enterprise Yearly ($279)"])
            tx_id = st.text_input("معرف المعاملة (TxID)", value=f"TX-{secrets.token_hex(4).upper()}")
            
            if st.button("⚡ محاكاة استلام Webhook الدفع", use_container_width=True):
                added_credits = 100 if "Monthly" in pay_plan else 1500
                CloudSQLUtils.update_user_credits(pay_email, user.get("credits") + added_credits, new_status="Enterprise Pro")
                
                log_entry = {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "tx_id": tx_id,
                    "email": pay_email,
                    "plan": pay_plan,
                    "status": "SUCCESS"
                }
                st.session_state.payment_logs.append(log_entry)
                st.success(f"✅ تم تفعيل الاشتراك بنجاح للبريد {pay_email}! تمت إضافة {added_credits} نقطة.")
                st.rerun()

        with col_pay2:
            st.markdown("### 📬 سجل معالجات الدفع الفورية (Payment Logs)")
            if st.session_state.payment_logs:
                st.dataframe(pd.DataFrame(st.session_state.payment_logs), use_container_width=True)
            else:
                st.info("لا توجد عمليات دفع مسجلة في الجلسة الحالية.")

    # -----------------------------------------------------------------
    # TAB 5: ACCOUNT & UPGRADE (CHECKOUT LINKS)
    # -----------------------------------------------------------------
    with tab5:
        st.subheader("💳 ترقية الاشتراك والرصيد")
        st.write("اختر الخطة المناسبة للانتقال مباشرة إلى بوابة الدفع المعتمدة:")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f'''
            <div style="background-color:#1e293b; padding:20px; border-radius:10px; border:1px solid #3b82f6; text-align:center;">
                <h3>🚀 الاشتراك الشهري</h3>
                <h2>$29 <small>/ شهرياً</small></h2>
                <p>100 نقطة توليد معمارية شهرياً + دعم كامل</p>
                <a href="{PAYMENT_LINK_MONTHLY}" target="_blank" style="display:block; background:#2563eb; color:white; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none;">ادفع الآن عبر Lemon Squeezy</a>
            </div>
            ''', unsafe_allow_html=True)
            
        with col_p2:
            st.markdown(f'''
            <div style="background-color:#1e293b; padding:20px; border-radius:10px; border:1px solid #8b5cf6; text-align:center;">
                <h3>🏆 الاشتراك السنوي</h3>
                <h2>$279 <small>/ سنوياً</small></h2>
                <p>1500 نقطة توليد معمارية + أولوية الدعم والسيرفرات</p>
                <a href="{PAYMENT_LINK_YEARLY}" target="_blank" style="display:block; background:#7c3aed; color:white; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none;">ادفع الآن عبر Lemon Squeezy</a>
            </div>
            ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
