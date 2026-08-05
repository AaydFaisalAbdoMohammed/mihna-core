#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & MIHNA AGENT PRO ENTERPRISE - HYBRID ULTIMATE SaaS
النسخة المدمجة الشاملة: تجمع بين قاعدة بيانات Cloud SQL وتوليد Gemini AI 
مع التحليلات البصرية الـ 5D، دعم PDF العربي، وإدارة الاشتراكات المؤقنة.
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
# 3. AI GENERATION ENGINE (GEMINI INTEGRATION)
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        if not api_key:
            # Fallback Mock Generator if API key is missing
            return {
                "project_name": req['client'],
                "domain": req['tech'],
                "budget": req['budget'],
                "target_days": req['timeline'],
                "executive_summary": f"خطة هندسية معمارية لمشروع {req['client']} تغطي كافة الجوانب الفنية.",
                "risk_score": 25,
                "confidence_score": 90,
                "tasks": [
                    {"id": 1, "task": "تحليل المتطلبات وبناء المعمارية Architecture", "days": max(1, int(req['timeline']*0.2)), "cost": int(req['budget']*0.2), "priority": "High"},
                    {"id": 2, "task": "تطوير قواعد البيانات والـ Backend API", "days": max(1, int(req['timeline']*0.4)), "cost": int(req['budget']*0.4), "priority": "High"},
                    {"id": 3, "task": "بناء واجهات المستخدم Frontend & UI", "days": max(1, int(req['timeline']*0.25)), "cost": int(req['budget']*0.25), "priority": "Medium"},
                    {"id": 4, "task": "الاختبارات والتكامل السحابي QA & Deploy", "days": max(1, int(req['timeline']*0.15)), "cost": int(req['budget']*0.15), "priority": "Low"}
                ]
            }

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        lang_instruction = "اللغة العربية" if lang == "ar" else "English"

        prompt = f"""
        Analyze this project requirements and output STRICTLY a JSON object in {lang_instruction}:
        - Project/Client Name: {req['client']}
        - Description & Scope: {req['desc']}
        - Budget ($): {req['budget']}
        - Timeline (Days): {req['timeline']}
        - Tech Stack: {req['tech']}

        JSON Schema:
        {{
            "project_name": "{req['client']}",
            "domain": "{req['tech']}",
            "budget": {req['budget']},
            "target_days": {req['timeline']},
            "executive_summary": "Summary here...",
            "risk_score": 20,
            "confidence_score": 92,
            "tasks": [
                {{"id": 1, "task": "Task Name", "days": 5, "cost": 1000, "priority": "High"}}
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
# 4. EXPORT ENGINE (WITH ARABIC PDF FIXED)
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
        
        info_text = f"الميزانية: ${plan.get('budget')} | المدة: {plan.get('target_days')} يوم | HMAC: {plan.get('signature', '')[:20]}..."
        story.append(Paragraph(reshape(info_text), body_style))
        story.append(Spacer(1, 15))

        table_data = [[reshape("الأولوية"), reshape("التكلفة ($)"), reshape("المدة (يوم)"), reshape("اسم المهمة")]]
        for t in plan.get("tasks", []):
            table_data.append([reshape(t.get('priority', '')), str(t.get('cost', 0)), str(t.get('days', 0)), reshape(t.get('task', ''))])

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
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 6. MAIN APPLICATION
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

    # --- MAIN DASHBOARD ---
    user = st.session_state.current_user

    with st.sidebar:
        st.title("🛡️ PHOENIX COMMAND")
        st.caption(f"👤 {user.get('name')}")
        st.caption(f"💳 الرصيد: {user.get('credits')} نقاط")
        st.markdown(f"<span class='badge-purple'>{user.get('plan_status')}</span>", unsafe_allow_html=True)
        st.divider()
        
        api_key = st.text_input("🔑 Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    st.title("🚀 وكيل مهنة PRO | PHOENIX Enterprise")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏗️ بناء خطة مشروع", "📊 التحليلات الـ 5D", "✏️ محرر المهام", "💳 الحساب والترقية"])

    # --- TAB 1: BUILD PLAN ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("اسم المشروع", value="متجر لوجستي متكامل")
            budget = st.number_input("الميزانية المقدرة ($)", value=5000)
        with col2:
            tech = st.text_input("المجال والتقنيات", value="Flutter, Node.js, PostgreSQL")
            days = st.number_input("المدة (أيام)", value=30)
            
        scope = st.text_area("نطاق العمل (Scope of Work)", value="تطوير نظام تتبع شحنات ومتاجر مع لوحة تحكم سحابية.")

        if st.button("🚀 توليد وتوقيع الخطة الهندسية", type="primary", use_container_width=True):
            if user.get("credits", 0) <= 0:
                st.error("رصيدك غير كافٍ. يرجى الترقية.")
            else:
                with st.spinner("جاري التوليد والتوقيع الرقمي..."):
                    req = {"client": p_name, "budget": budget, "timeline": days, "tech": tech, "desc": scope}
                    plan = PhoenixAI.generate_architecture(api_key, req, lang=st.session_state.lang)
                    
                    st.session_state.current_plan = plan
                    user["credits"] -= 1
                    CloudSQLUtils.update_user_credits(user.get("email"), user["credits"])
                    st.success("✅ تم توليد وتوقيع الخطة بنجاح!")
                    st.rerun()

        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            st.divider()
            st.info(f"🔑 HMAC-SHA512 Signature: `{plan.get('signature')}`")
            st.dataframe(pd.DataFrame(plan.get("tasks", [])), use_container_width=True)

    # --- TAB 2: 5D VISUAL ANALYTICS ---
    with tab2:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            df = pd.DataFrame(plan.get("tasks", []))
            
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.markdown("### 🕸️ تقييم أبعاد المشروع (5D Radar Risk)")
                radar_categories = ['تعقيد النطاق', 'الأمان الرقمي', 'التحكم بالجدول', 'استقرار التكلفة', 'المرونة التقنية']
                fig_radar = go.Figure(go.Scatterpolar(
                    r=[80, 90, 85, 75, plan.get('risk_score', 20)],
                    theta=radar_categories, fill='toself', line=dict(color='#8B5CF6')
                ))
                fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"), height=300)
                st.plotly_chart(fig_radar, use_container_width=True)

            with c_r2:
                st.markdown("### 🎯 مؤشر السلامة والاعتمادية")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=plan.get('confidence_score', 90),
                    title={'text': "نسبة الاعتمادية %"},
                    gauge={'bar': {'color': "#3b82f6"}}
                ))
                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"), height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("قم بتوليد خطة من التبويب الأول أولاً.")

    # --- TAB 3: TASK EDITOR & EXPORT ---
    with tab3:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            edited_df = st.data_editor(pd.DataFrame(plan.get("tasks", [])), num_rows="dynamic", use_container_width=True)
            
            if st.button("💾 حفظ التعديلات وإعادة التوقيع الرقمي", use_container_width=True):
                plan["tasks"] = edited_df.to_dict(orient='records')
                plan["signature"] = VaultSecurity.sign_payload(plan)
                st.session_state.current_plan = plan
                st.success("✅ تم تحديث التوقيع الرقمي بنجاح!")
                st.rerun()

            st.divider()
            col_ex1, col_ex2 = st.columns(2)
            col_ex1.download_button("📊 تصدير Excel", ExportEngine.build_excel(plan.get("tasks", [])), "plan.xlsx", use_container_width=True)
            col_ex2.download_button("📄 تصدير PDF عربي موثق", ExportEngine.build_pdf(plan), "plan.pdf", use_container_width=True)
        else:
            st.info("لا توجد خطة حالية.")

    # --- TAB 4: ACCOUNT & UPGRADE ---
    with tab4:
        st.subheader("💳 ترقية الاشتراك")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" style="display:block;text-align:center;background:#2563eb;color:white;padding:12px;border-radius:8px;font-weight:bold;text-decoration:none;">🚀 الاشتراك الشهري ($29)</a>', unsafe_allow_html=True)
        with col_p2:
            st.markdown(f'<a href="{PAYMENT_LINK_YEARLY}" target="_blank" style="display:block;text-align:center;background:#7c3aed;color:white;padding:12px;border-radius:8px;font-weight:bold;text-decoration:none;">🏆 الاشتراك السنوي ($279)</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
