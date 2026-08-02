#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX PRO HYBRID EDITION (MERGED & FIXED) - ULTIMATE WINNING ARCHITECTURE
دمج بين هيكلية PHOENIX PRO v8.5 وميزات وكيل مهنة PRO v5.0 مع إصلاح شامل للاعتماديات
الميزات:
- قاعدة بيانات مدمجة (بدون need for cloudsql_utils)
- RAG (استرجاع مشاريع مشابهة)
- تحليلات متقدمة مع جدول وتوصيات ذكية
- HITL متطور
- تصدير (PDF, Excel, JSON, TXT)
- واجهة فاخرة (داكنة/فاتحة، عربي/إنجليزي)
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
from plotly.subplots import make_subplots
import google.generativeai as genai

# ----------------- Optional Heavy Dependencies -----------------
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
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
        "export_txt": "📝 تصدير نصي (TXT)",
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
        "export_txt": "📝 Export Text (TXT)",
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
    JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))

    @classmethod
    def generate_fingerprint(cls) -> str:
        seed = f"{os.getenv('HOSTNAME', 'unknown')}-{datetime.datetime.now().isoformat()}-{uuid.uuid4()}-{os.getpid()}"
        return hashlib.sha256((seed + cls.HMAC_KEY[:16]).encode()).hexdigest()[:24]

    @classmethod
    def sign_payload(cls, payload: dict) -> str:
        clean_payload = {k: v for k, v in payload.items() if k not in ["signature", "timestamp"]}
        payload_str = json.dumps(clean_payload, sort_keys=True)
        return hmac.new(cls.HMAC_KEY.encode(), payload_str.encode(), hashlib.sha512).hexdigest()[:32]

    @classmethod
    def generate_digital_signature(cls, data: str) -> str:
        timestamp = str(int(time.time()))
        message = f"{data}:{timestamp}:{cls.generate_fingerprint()}"
        sig = hmac.new(cls.HMAC_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()[:16]
        return f"SIG-{timestamp[:8]}-{sig}"

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
# 3. DATABASE ENGINE (FIXED - NO external cloudsql_utils needed)
# =====================================================================
class DatabaseEngine:
    @staticmethod
    def get_db_connection():
        if not PYMYSQL_AVAILABLE:
            return None
        try:
            cloud_sql_instance = os.getenv("CLOUD_SQL_CONNECTION_NAME")
            db_user = os.getenv("DB_USER", "root")
            db_pass = os.getenv("DB_PASSWORD", "")
            db_name = os.getenv("DB_NAME", "mihna_agent")
            db_host = os.getenv("DB_HOST", "127.0.0.1")
            db_port = int(os.getenv("DB_PORT", 3306))
            db_ssl = os.getenv("DB_SSL_ENABLED", "false").lower() == "true"

            conn_args = {
                "user": db_user,
                "password": db_pass,
                "database": db_name,
                "charset": "utf8mb4",
                "cursorclass": pymysql.cursors.DictCursor,
                "connect_timeout": 10
            }

            if cloud_sql_instance and os.path.exists(f"/cloudsql/{cloud_sql_instance}"):
                conn_args["unix_socket"] = f"/cloudsql/{cloud_sql_instance}"
            else:
                conn_args["host"] = db_host
                conn_args["port"] = db_port
                if db_ssl:
                    conn_args["ssl"] = {"ca": "/etc/ssl/certs/ca-certificates.crt"}

            return pymysql.connect(**conn_args)
        except Exception as e:
            logging.error(f"DB Connection Error: {e}")
            return None

    @staticmethod
    def init_db():
        conn = DatabaseEngine.get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100), email VARCHAR(100) UNIQUE, password VARCHAR(255),
                        credits INT DEFAULT 5, plan_status VARCHAR(50) DEFAULT 'Free',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(100), client_name VARCHAR(100), summary TEXT,
                        budget_range VARCHAR(50), tech_stack JSON, payload JSON,
                        signature VARCHAR(64), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        project_id INT, title VARCHAR(200), description TEXT,
                        estimated_days INT, priority VARCHAR(20)
                    )
                """)
                conn.commit()
        except Exception as e:
            logging.error(f"Init DB Error: {e}")
        finally:
            conn.close()

    @staticmethod
    def get_user_by_email(email):
        conn = DatabaseEngine.get_db_connection()
        if not conn: return None
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM users WHERE email = %s", (email,))
                return c.fetchone()
        except: return None
        finally: conn.close()

    @staticmethod
    def register_user(name, email, hashed_pass, credits=5, plan_status="Free"):
        conn = DatabaseEngine.get_db_connection()
        if not conn: return False
        try:
            with conn.cursor() as c:
                c.execute("INSERT INTO users (name, email, password, credits, plan_status) VALUES (%s,%s,%s,%s,%s)",
                          (name, email, hashed_pass, credits, plan_status))
            conn.commit()
            return True
        except: return False
        finally: conn.close()

    @staticmethod
    def update_user_credits(email, credits, status=None):
        conn = DatabaseEngine.get_db_connection()
        if not conn: return False
        try:
            with conn.cursor() as c:
                if status:
                    c.execute("UPDATE users SET credits=%s, plan_status=%s WHERE email=%s", (credits, status, email))
                else:
                    c.execute("UPDATE users SET credits=%s WHERE email=%s", (credits, email))
            conn.commit()
            return True
        except: return False
        finally: conn.close()

    @staticmethod
    def save_project(email, plan_json):
        conn = DatabaseEngine.get_db_connection()
        if not conn: return False
        try:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO projects (user_id, client_name, summary, budget_range, tech_stack, payload, signature)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    email,
                    plan_json.get('client'),
                    plan_json.get('executive_summary'),
                    plan_json.get('budget_str'),
                    json.dumps(plan_json.get('tech_stack', [])),
                    json.dumps(plan_json, ensure_ascii=False),
                    plan_json.get('signature')
                ))
                project_id = c.lastrowid
                for task in plan_json.get('tasks', []):
                    c.execute("""
                        INSERT INTO tasks (project_id, title, description, estimated_days, priority)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (project_id, task.get('title'), task.get('description'), task.get('days'), task.get('priority')))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Save project error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_projects(email):
        conn = DatabaseEngine.get_db_connection()
        if not conn: return []
        try:
            with conn.cursor() as c:
                c.execute("SELECT id, client_name, summary, budget_range, created_at, signature FROM projects WHERE user_id = %s ORDER BY created_at DESC", (email,))
                return c.fetchall()
        except: return []
        finally: conn.close()


# =====================================================================
# 4. RAG ENGINE (Retrieval Augmented Generation) - من الكود الثاني
# =====================================================================
class RAGEngine:
    @staticmethod
    def get_similar_projects(keyword: str, top_k: int = 2) -> list:
        conn = DatabaseEngine.get_db_connection()
        if not conn: return []
        try:
            keywords = [w for w in re.findall(r'\w+', keyword) if len(w) > 3]
            if not keywords: return []
            conditions = " OR ".join([
                "(summary LIKE %s OR client_name LIKE %s OR tech_stack LIKE %s)"
                for _ in keywords[:5]
            ])
            params = []
            for kw in keywords[:5]:
                pattern = f"%{kw}%"
                params.extend([pattern, pattern, pattern])
            sql = f"SELECT * FROM projects WHERE {conditions} LIMIT {top_k}"
            with conn.cursor() as c:
                c.execute(sql, params)
                return c.fetchall()
        except Exception as e:
            return []
        finally:
            conn.close()


# =====================================================================
# 5. AI GENERATION ENGINE
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # RAG Context (من الكود الثاني)
        similar = RAGEngine.get_similar_projects(req.get("desc", ""), top_k=2)
        context = ""
        if similar:
            context = "\n\n**📚 مشاريع سابقة مشابهة (RAG):**\n"
            for p in similar:
                context += f"- {p.get('summary', '')[:150]}...\n"

        lang_instruction = "اللغة العربية" if lang == "ar" else "English"
        prompt = f"""
        أنت مهندس معماري في PHOENIX PRO. حلل هذا الطلب:
        - العميل: {req['client']}
        - النطاق: {req['desc']}
        - الميزانية: {req['budget']}
        - الجدول: {req['timeline']}
        - التقنيات: {req['tech']}
        {context}

        أخرج JSON فقط بهذا الهيكل:
        {{
            "client": "{req['client']}",
            "executive_summary": "ملخص شامل في {lang_instruction}",
            "tech_stack": ["تقنية 1", "تقنية 2"],
            "budget_str": "{req['budget']}",
            "timeline": "{req['timeline']}",
            "risk_score": 20,
            "confidence_score": 85,
            "tasks": [
                {{"title": "مهمة 1", "description": "وصف", "days": 5, "cost": 1200, "priority": "High"}},
                {{"title": "مهمة 2", "description": "وصف", "days": 10, "cost": 2400, "priority": "Medium"}}
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
            raise ValueError(f"فشل التوليد: {e}")


# =====================================================================
# 6. ANALYTICS ENGINE (المدمجة مع جدول وتوصيات من الكود الثاني)
# =====================================================================
class AnalyticsEngine:
    @staticmethod
    def compute_metrics(plan: dict) -> dict:
        tasks = plan.get("tasks", [])
        total_days = sum(t.get('days', 0) for t in tasks)
        total_tasks = len(tasks)
        high = sum(1 for t in tasks if str(t.get('priority', '')).lower() in ['high', 'عالية'])
        med = sum(1 for t in tasks if str(t.get('priority', '')).lower() in ['medium', 'متوسطة'])
        low = sum(1 for t in tasks if str(t.get('priority', '')).lower() in ['low', 'منخفضة'])
        
        base_cost = total_days * 150
        overhead = base_cost * 0.2
        total_cost = base_cost + overhead
        
        high_ratio = high / total_tasks if total_tasks else 0
        long_tasks = sum(1 for t in tasks if t.get('days', 0) > 5)
        long_ratio = long_tasks / total_tasks if total_tasks else 0
        
        risk_score = min(100, int((high_ratio * 0.6 + long_ratio * 0.4) * 100))
        confidence_score = plan.get('confidence_score', 85)
        
        return {
            'total_days': total_days,
            'total_tasks': total_tasks,
            'high': high, 'med': med, 'low': low,
            'total_cost': total_cost,
            'risk_score': risk_score,
            'confidence_score': confidence_score,
            'avg_days': total_days / total_tasks if total_tasks else 0,
            'long_tasks': long_tasks
        }

    @staticmethod
    def render_advanced_analytics(plan: dict):
        m = AnalyticsEngine.compute_metrics(plan)
        tasks = plan.get("tasks", [])
        
        st.markdown("## 📊 تحليل الخطة الذكي")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 إجمالي الأيام", m['total_days'])
        c2.metric("💰 التكلفة", f"${m['total_cost']:,.0f}")
        c3.metric("⚠️ المخاطرة", f"{m['risk_score']}%")
        c4.metric("📊 الثقة", f"{m['confidence_score']}%")
        st.divider()

        # رسوم بيانية (مفاتيح فريدة)
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Pie(labels=['عالية','متوسطة','منخفضة'], values=[m['high'],m['med'],m['low']], hole=0.3)])
            fig.update_layout(title="توزيع المهام حسب الأولوية")
            st.plotly_chart(fig, use_container_width=True, key="analytics_pie")
        with col2:
            if tasks:
                df = pd.DataFrame(tasks)
                fig = px.bar(df, x='title', y='days', color='priority', title="أيام العمل لكل مهمة")
                st.plotly_chart(fig, use_container_width=True, key="analytics_bar")

        # 📋 الجدول التفصيلي + التوصيات (مأخوذ من الكود الثاني)
        st.markdown("### 📋 جدول التحليل التفصيلي")
        df_analytics = pd.DataFrame({
            'المقياس': ['إجمالي الأيام', 'عدد المهام', 'عالية الأولوية', 'متوسطة الأولوية', 'منخفضة الأولوية',
                       'التكلفة الإجمالية', 'درجة المخاطرة', 'درجة الثقة', 'متوسط الأيام لكل مهمة', 'مهام طويلة (>5 أيام)'],
            'القيمة': [
                m['total_days'], m['total_tasks'], m['high'], m['med'], m['low'],
                f"${m['total_cost']:,.0f}", f"{m['risk_score']}%", f"{m['confidence_score']}%",
                f"{m['avg_days']:.1f} أيام", m['long_tasks']
            ]
        })
        st.dataframe(df_analytics, use_container_width=True, hide_index=True)

        st.markdown("### 💡 توصيات ذكية")
        recs = []
        if m['risk_score'] > 70: recs.append("⚠️ **مخاطرة عالية**: يُوصى بتقسيم المهام عالية الأولوية إلى مهام أصغر.")
        if m['confidence_score'] < 50: recs.append("📝 **تفاصيل غير كافية**: يُوصى بإضافة تفاصيل أكثر للمهام.")
        if m['total_days'] > 30: recs.append("⏳ **جدول طويل**: قسّم المشروع إلى مراحل.")
        if m['high'] / max(m['total_tasks'], 1) > 0.5: recs.append("🔥 **كثافة عالية**: أعد تقييم الأولويات.")
        if not recs: recs.append("✅ **خطة متوازنة**: استمر في التنفيذ.")
        for rec in recs: st.info(rec)


# =====================================================================
# 7. EXPORT ENGINE (مع إضافة TXT من الكود الثاني)
# =====================================================================
class ExportEngine:
    @staticmethod
    def build_pdf(data: dict) -> bytes:
        if not REPORTLAB_AVAILABLE: return b""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>Enterprise Architecture: {data.get('client')}</b>", styles['Title']), Spacer(1, 12)]
        table_data = [["Task", "Days", "Cost ($)", "Priority"]]
        for t in data.get("tasks", []):
            table_data.append([t.get('title'), str(t.get('days')), f"${t.get('cost')}", t.get('priority')])
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
        ]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()

    @staticmethod
    def build_excel(tasks: list) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Tasks")
        return buffer.getvalue()

    @staticmethod
    def build_txt(plan: dict) -> bytes:
        txt = f"=== خطة مشروع {plan.get('client')} ===\n\n"
        txt += f"الملخص: {plan.get('executive_summary')}\n"
        txt += f"الميزانية: {plan.get('budget_str')}\n"
        txt += f"التوقيع: {plan.get('signature')}\n\n"
        txt += "=== المهام ===\n"
        for i, t in enumerate(plan.get("tasks", []), 1):
            txt += f"{i}. {t.get('title')} ({t.get('priority')}) - {t.get('days')} أيام\n"
            txt += f"   {t.get('description')}\n\n"
        return txt.encode('utf-8')


# =====================================================================
# 8. SESSION & UI (Glassmorphism CSS - من الكود الأول)
# =====================================================================
def init_session():
    if "users_db" not in st.session_state:
        st.session_state.users_db = {}
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
        text_color = "#f8fafc"; label_color = "#38bdf8"; input_bg = "#1e293b"; input_text = "#ffffff"; input_border = "#3b82f6"
    else:
        bg_main, bg_sidebar = "#f8fafc", "#ffffff"
        text_color = "#0f172a"; label_color = "#1e293b"; input_bg = "#ffffff"; input_text = "#0f172a"; input_border = "#2563eb"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Cairo', sans-serif !important;
            direction: {direction}; text-align: {align_text};
            background-color: {bg_main} !important; color: {text_color} !important;
        }}
        section[data-testid="stSidebar"] {{ background-color: {bg_sidebar} !important; }}
        .stTextInput label, .stSelectbox label, .stTextArea label {{
            color: {label_color} !important; font-weight: 800 !important;
        }}
        div[data-baseweb="input"], input, textarea {{
            background-color: {input_bg} !important;
            border: 2px solid {input_border} !important;
            color: {input_text} !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
        }}
        .hero-header {{
            font-size: 2.2rem; font-weight: 800;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-align: center; padding: 10px 0;
        }}
        .pay-btn {{
            display: block; background: linear-gradient(90deg, #2563eb, #4f46e5);
            color: white !important; text-align: center; padding: 10px;
            border-radius: 10px; text-decoration: none; font-weight: bold;
        }}
        .stat-card {{
            background: rgba(30, 41, 59, 0.8); border-radius: 14px; padding: 16px;
            border: 1px solid rgba(255,255,255,0.1); text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 9. AUTHENTICATION
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
                user = DatabaseEngine.get_user_by_email(email)
                if user and VaultSecurity.verify_password(password, user["password"]):
                    st.session_state.authenticated = True
                    st.session_state.current_user = user
                    st.rerun()
                else: st.error("بيانات الدخول غير صحيحة.")
        with tab_signup:
            name = st.text_input(t["full_name"], key="signup_name")
            email = st.text_input(t["email"], key="signup_email")
            p1 = st.text_input(t["password"], type="password", key="signup_pass")
            p2 = st.text_input(t["confirm_password"], type="password", key="signup_confirm")
            if st.button(t["signup_btn"], use_container_width=True):
                if DatabaseEngine.get_user_by_email(email): st.error("مسجل مسبقاً.")
                elif p1 != p2: st.error("كلمات المرور غير متطابقة.")
                else:
                    hashed = VaultSecurity.hash_password(p1)
                    if DatabaseEngine.register_user(name, email, hashed, 5, "Free Trial"):
                        st.success("تم إنشاء الحساب! سجل دخولك الآن.")


# =====================================================================
# 10. MAIN APPLICATION
# =====================================================================
def main():
    st.set_page_config(page_title="PHOENIX PRO", page_icon="🧠", layout="wide")
    init_session()
    DatabaseEngine.init_db()
    
    if not st.session_state.authenticated:
        render_auth_page()
        return

    t = TRANSLATIONS[st.session_state.lang]
    user = st.session_state.current_user

    # Sidebar
    with st.sidebar:
        st.markdown("<h3 style='text-align:center;'>⚙️ PHOENIX</h3>", unsafe_allow_html=True)
        c_l, c_t = st.columns(2)
        with c_l:
            if st.button("🌐 EN" if st.session_state.lang == "ar" else "🌐 AR", use_container_width=True):
                st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
                st.rerun()
        with c_t:
            if st.button("☀️" if st.session_state.theme == "dark" else "🌙", use_container_width=True):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                st.rerun()
        st.divider()
        st.caption(f"👤 {user.get('name')}")
        st.caption(f"📧 {user.get('email')}")
        st.markdown(f"**{t['credits']}:** `{user.get('credits', 0)}`")
        st.caption(f"{t['plan']}: {user.get('plan_status')}")
        if st.button(t["logout"], use_container_width=True):
            st.session_state.authenticated = False; st.rerun()
        st.divider()
        api_key = st.text_input(t["gemini_key"], type="password", value=os.getenv("GEMINI_API_KEY", ""))
        st.divider()
        st.subheader(t["tg_title"])
        tg_bot = st.text_input("Token", type="password", value=os.getenv("TELEGRAM_BOT_TOKEN", ""))
        tg_chat = st.text_input("ID", value=os.getenv("TELEGRAM_CHAT_ID", ""))
        st.divider()
        st.subheader(t["sub_title"])
        pay_email = st.text_input(t["email"], value=user.get('email'))
        col_m, col_y = st.columns(2)
        store_slug = os.getenv("LEMONSQUEEZY_STORE_SLUG", "mihna")
        col_m.markdown(f'<a href="https://{store_slug}.lemonsqueezy.com/buy?checkout[email]={pay_email}&plan=monthly" target="_blank" class="pay-btn">{t["monthly"]}</a>', unsafe_allow_html=True)
        col_y.markdown(f'<a href="https://{store_slug}.lemonsqueezy.com/buy?checkout[email]={pay_email}&plan=yearly" target="_blank" class="pay-btn">{t["yearly"]}</a>', unsafe_allow_html=True)
        act_code = st.text_input(t["activate_code"], type="password")
        if st.button(t["activate_btn"], use_container_width=True):
            if act_code in ["PRO2026", "PHOENIX"]:
                DatabaseEngine.update_user_credits(user.get("email"), 9999, "Unlimited")
                user["credits"] = 9999; user["plan_status"] = "Unlimited"; st.success("تم التفعيل!"); st.rerun()

    # Main Area
    inject_custom_css()
    st.markdown(f'<div class="hero-header">{t["title"]}</div>', unsafe_allow_html=True)
    tab_gen, tab_an, tab_dash, tab_exp = st.tabs([t["tab_gen"], t["tab_analytics"], t["tab_dashboard"], t["tab_export"]])

    # Tab 1: Generation
    with tab_gen:
        c1, c2 = st.columns(2)
        with c1:
            client = st.text_input(t["client"], value="مؤسسة أفق")
            budget = st.text_input(t["budget"], value="8000 - 12000")
        with c2:
            timeline = st.text_input(t["timeline"], value="8 أسابيع")
            tech = st.text_input(t["tech"], value="Flutter, Node.js, Supabase")
        desc = st.text_area(t["scope"], value="منصة تعليمية تفاعلية للطلاب...", height=120)
        if st.button(t["generate_btn"], type="primary", use_container_width=True):
            if not api_key: st.error("أدخل مفتاح Gemini API.")
            elif user.get("credits", 0) <= 0: st.error("انتهى الرصيد.")
            else:
                with st.spinner("جاري التوليد..."):
                    try:
                        req = {"client": client, "desc": desc, "budget": budget, "timeline": timeline, "tech": tech}
                        plan = PhoenixAI.generate_architecture(api_key, req, lang=st.session_state.lang)
                        # Save & Update credits
                        DatabaseEngine.save_project(user.get("email"), plan)
                        user["credits"] -= 1
                        DatabaseEngine.update_user_credits(user.get("email"), user["credits"])
                        st.session_state.selected_plan = plan
                        # Telegram alert
                        if tg_bot and tg_chat:
                            try:
                                requests.post(f"https://api.telegram.org/bot{tg_bot}/sendMessage", json={"chat_id": tg_chat, "text": f"🚀 New Plan: {plan.get('client')}", "parse_mode": "Markdown"}, timeout=5)
                            except: pass
                        st.success(f"✅ تم التوليد! المتبقي: {user['credits']}")
                        st.rerun()
                    except Exception as e: st.error(str(e))

        if st.session_state.selected_plan:
            plan = st.session_state.selected_plan
            st.divider()
            st.markdown(f"**Client:** {plan.get('client')} | **Signature:** `{plan.get('signature')}`")
            st.caption(plan.get('executive_summary'))
            # HITL (Interactive edit)
            tasks = plan.get("tasks", [])
            updated_tasks = []
            st.markdown("### ✏️ HITL - تعديل المهام")
            for idx, task in enumerate(tasks):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3,1,1,1])
                    with col1: title = st.text_input(f"المهمة {idx+1}", value=task.get('title',''), key=f"t_{idx}")
                    with col2: days = st.number_input("أيام", min_value=1, value=task.get('days',1), key=f"d_{idx}")
                    with col3: cost = st.number_input("$", min_value=0, value=task.get('cost',100), step=50, key=f"c_{idx}")
                    with col4: priority = st.selectbox("الأولوية", ['High','Medium','Low'], index=['High','Medium','Low'].index(task.get('priority','Medium')), key=f"p_{idx}")
                    updated_tasks.append({"title": title, "days": days, "cost": cost, "priority": priority, "description": task.get("description", "")})
            if st.button("🔄 تحديث الخطة والتوقيع", use_container_width=True):
                plan["tasks"] = updated_tasks
                plan["signature"] = VaultSecurity.sign_payload(plan)
                st.session_state.selected_plan = plan
                st.success("تم تحديث التوقيع!"); st.rerun()

    # Tab 2: Analytics (المدمجة مع جدول وتوصيات)
    with tab_an:
        if st.session_state.selected_plan:
            AnalyticsEngine.render_advanced_analytics(st.session_state.selected_plan)
        else:
            st.info("قم بتوليد خطة أولاً.")

    # Tab 3: Dashboard
    with tab_dash:
        projects = DatabaseEngine.get_projects(user.get("email"))
        if projects:
            st.dataframe(pd.DataFrame(projects), use_container_width=True)
        else:
            st.info("لا توجد مشاريع.")

    # Tab 4: Export (مع إضافة TXT)
    with tab_exp:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            st.code(f"Signature: {p.get('signature')}", language="json")
            c1, c2, c3, c4 = st.columns(4)
            c1.download_button(t["export_json"], json.dumps(p, ensure_ascii=False, indent=2), "plan.json", "application/json", use_container_width=True)
            c2.download_button(t["export_excel"], ExportEngine.build_excel(p.get("tasks", [])), "plan.xlsx", use_container_width=True)
            if REPORTLAB_AVAILABLE:
                c3.download_button(t["export_pdf"], ExportEngine.build_pdf(p), "plan.pdf", "application/pdf", use_container_width=True)
            c4.download_button(t["export_txt"], ExportEngine.build_txt(p), "plan.txt", "text/plain", use_container_width=True)
        else:
            st.info("لا توجد خطة نشطة.")

if __name__ == "__main__":
    main()
