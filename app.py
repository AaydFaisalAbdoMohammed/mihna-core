#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX PRO ULTIMATE – النسخة النهائية الفائزة (Merged Edition)
دمج أفضل ميزات PHOENIX PRO v8.5 مع محرك قاعدة البيانات الذكي والـ RAG
مع واجهة Glassmorphism الفاخرة، وتحليلات متقدمة، وتصدير متعدد الصيغ
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
from functools import wraps

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# ----------------- Optional Dependencies -----------------
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
# 1. TRANSLATION DICTIONARY (دمج الكودين)
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
# 2. SECURITY & INTEGRITY ENGINE (من الكود الثاني مع تحسينات)
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
# 3. DATABASE ENGINE (ذكي مع إعادة محاولة و RAG حقيقي)
# =====================================================================
class DatabaseEngine:
    _connection_status = None
    _max_retries = 3
    _retry_delay = 1

    @classmethod
    def _retry_operation(cls, func, *args, **kwargs):
        for attempt in range(cls._max_retries):
            try:
                result = func(*args, **kwargs)
                cls._connection_status = True
                return result
            except Exception as e:
                logging.warning(f"DB operation failed (attempt {attempt+1}): {e}")
                if attempt < cls._max_retries - 1:
                    time.sleep(cls._retry_delay * (attempt + 1))
                else:
                    cls._connection_status = False
                    raise e

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

            conn = pymysql.connect(**conn_args)
            DatabaseEngine._connection_status = True
            return conn
        except Exception as e:
            DatabaseEngine._connection_status = False
            logging.error(f"DB Connection Error: {e}")
            return None

    @classmethod
    def is_connected(cls):
        if cls._connection_status is None:
            conn = cls.get_db_connection()
            if conn:
                conn.close()
                cls._connection_status = True
            else:
                cls._connection_status = False
        return cls._connection_status

    @classmethod
    def refresh_status(cls):
        cls._connection_status = None
        return cls.is_connected()

    @staticmethod
    def _get_fallback_store():
        if "_fallback_db" not in st.session_state:
            st.session_state._fallback_db = {
                "users": {},
                "projects": {},
                "next_user_id": 1,
                "next_project_id": 1
            }
        return st.session_state._fallback_db

    @classmethod
    def init_db(cls):
        conn = cls.get_db_connection()
        if not conn:
            st.warning("⚠️ قاعدة البيانات غير متصلة. سيتم استخدام التخزين المؤقت في الجلسة.")
            return
        try:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100), email VARCHAR(100) UNIQUE, password VARCHAR(255),
                        credits INT DEFAULT 5, plan_status VARCHAR(50) DEFAULT 'Free',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_email (email)
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(100), client_name VARCHAR(100), summary TEXT,
                        budget_range VARCHAR(50), tech_stack JSON, payload JSON,
                        signature VARCHAR(64), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_user (user_id),
                        FULLTEXT INDEX ft_summary (summary)
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        project_id INT, title VARCHAR(200), description TEXT,
                        estimated_days INT, priority VARCHAR(20),
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    )
                """)
                conn.commit()
                st.success("✅ قاعدة البيانات متصلة وجاهزة للعمل.")
        except Exception as e:
            logging.error(f"Init DB Error: {e}")
            st.warning(f"⚠️ فشل تهيئة قاعدة البيانات: {e}. سيتم استخدام التخزين المؤقت.")
        finally:
            conn.close()

    # ---- CRUD مع إعادة المحاولة ----
    @classmethod
    def get_user_by_email(cls, email):
        try:
            return cls._retry_operation(cls._get_user_by_email_impl, email)
        except Exception:
            return cls._get_fallback_store()["users"].get(email)

    @classmethod
    def _get_user_by_email_impl(cls, email):
        conn = cls.get_db_connection()
        if not conn:
            raise Exception("No database connection")
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM users WHERE email = %s", (email,))
                return c.fetchone()
        finally:
            conn.close()

    @classmethod
    def register_user(cls, name, email, hashed_pass, credits=5, plan_status="Free"):
        try:
            return cls._retry_operation(cls._register_user_impl, name, email, hashed_pass, credits, plan_status)
        except Exception:
            fallback = cls._get_fallback_store()
            if email in fallback["users"]:
                return False
            fallback["users"][email] = {
                "id": fallback["next_user_id"],
                "name": name,
                "email": email,
                "password": hashed_pass,
                "credits": credits,
                "plan_status": plan_status
            }
            fallback["next_user_id"] += 1
            return True

    @classmethod
    def _register_user_impl(cls, name, email, hashed_pass, credits, plan_status):
        conn = cls.get_db_connection()
        if not conn:
            raise Exception("No database connection")
        try:
            with conn.cursor() as c:
                c.execute("SELECT id FROM users WHERE email = %s", (email,))
                if c.fetchone():
                    return False
                c.execute("INSERT INTO users (name, email, password, credits, plan_status) VALUES (%s,%s,%s,%s,%s)",
                          (name, email, hashed_pass, credits, plan_status))
            conn.commit()
            return True
        finally:
            conn.close()

    @classmethod
    def update_user_credits(cls, email, credits, status=None):
        try:
            return cls._retry_operation(cls._update_credits_impl, email, credits, status)
        except Exception:
            fallback = cls._get_fallback_store()
            if email in fallback["users"]:
                fallback["users"][email]["credits"] = credits
                if status:
                    fallback["users"][email]["plan_status"] = status
                return True
            return False

    @classmethod
    def _update_credits_impl(cls, email, credits, status):
        conn = cls.get_db_connection()
        if not conn:
            raise Exception("No database connection")
        try:
            with conn.cursor() as c:
                if status:
                    c.execute("UPDATE users SET credits=%s, plan_status=%s WHERE email=%s", (credits, status, email))
                else:
                    c.execute("UPDATE users SET credits=%s WHERE email=%s", (credits, email))
                affected = c.rowcount
            conn.commit()
            return affected > 0
        finally:
            conn.close()

    @classmethod
    def save_project(cls, email, plan_json):
        try:
            return cls._retry_operation(cls._save_project_impl, email, plan_json)
        except Exception:
            fallback = cls._get_fallback_store()
            if email not in fallback["users"]:
                return False
            project = {
                "id": fallback["next_project_id"],
                "client_name": plan_json.get('client'),
                "summary": plan_json.get('executive_summary'),
                "budget_range": plan_json.get('budget_str'),
                "signature": plan_json.get('signature'),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": email
            }
            fallback["projects"][fallback["next_project_id"]] = project
            fallback["next_project_id"] += 1
            return True

    @classmethod
    def _save_project_impl(cls, email, plan_json):
        conn = cls.get_db_connection()
        if not conn:
            raise Exception("No database connection")
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
        finally:
            conn.close()

    @classmethod
    def get_projects(cls, email):
        try:
            return cls._retry_operation(cls._get_projects_impl, email)
        except Exception:
            fallback = cls._get_fallback_store()
            result = []
            for pid, proj in fallback["projects"].items():
                if proj.get("user_id") == email:
                    result.append({
                        "id": pid,
                        "client_name": proj.get("client_name"),
                        "summary": proj.get("summary"),
                        "budget_range": proj.get("budget_range"),
                        "created_at": proj.get("created_at"),
                        "signature": proj.get("signature")
                    })
            return sorted(result, key=lambda x: x["created_at"], reverse=True)

    @classmethod
    def _get_projects_impl(cls, email):
        conn = cls.get_db_connection()
        if not conn:
            raise Exception("No database connection")
        try:
            with conn.cursor() as c:
                c.execute("SELECT id, client_name, summary, budget_range, created_at, signature FROM projects WHERE user_id = %s ORDER BY created_at DESC", (email,))
                return c.fetchall()
        finally:
            conn.close()

    @classmethod
    def get_similar_projects(cls, keyword: str, top_k: int = 2) -> list:
        """استرجاع مشاريع مشابهة باستخدام البحث النصي."""
        try:
            return cls._retry_operation(cls._get_similar_projects_impl, keyword, top_k)
        except Exception:
            return []

    @classmethod
    def _get_similar_projects_impl(cls, keyword: str, top_k: int) -> list:
        conn = cls.get_db_connection()
        if not conn:
            raise Exception("No database connection")
        try:
            with conn.cursor() as c:
                keywords = [w for w in re.findall(r'\w+', keyword) if len(w) > 3]
                if not keywords:
                    return []
                conditions = " OR ".join([
                    "(summary LIKE %s OR client_name LIKE %s OR tech_stack LIKE %s)"
                    for _ in keywords[:5]
                ])
                params = []
                for kw in keywords[:5]:
                    pattern = f"%{kw}%"
                    params.extend([pattern, pattern, pattern])
                sql = f"SELECT summary, client_name FROM projects WHERE {conditions} LIMIT {top_k}"
                c.execute(sql, params)
                return c.fetchall()
        finally:
            conn.close()


# =====================================================================
# 4. AI GENERATION ENGINE (مع RAG حقيقي)
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        # استرجاع مشاريع مشابهة
        similar = DatabaseEngine.get_similar_projects(req.get("desc", ""), top_k=2)
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
# 5. ANALYTICS ENGINE (نسخة متقدمة مع جدول وتوصيات)
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
# 6. EXPORT ENGINE (PDF, Excel, JSON, TXT)
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
# 7. COMMERCE & NOTIFICATION ENGINE (Telegram, Email, Lemon Squeezy)
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
# 8. SESSION & UI (Glassmorphism من الكود الأول)
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
        text_color = "#f8fafc"
        label_color = "#38bdf8"
        input_bg = "#1e293b"
        input_text = "#ffffff"
        input_border = "#3b82f6"
        input_focus_border = "#60a5fa"
    else:
        bg_main, bg_sidebar = "#f8fafc", "#ffffff"
        text_color = "#0f172a"
        label_color = "#1e293b"
        input_bg = "#ffffff"
        input_text = "#0f172a"
        input_border = "#2563eb"
        input_focus_border = "#1d4ed8"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700&display=swap');

        section[data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
            z-index: 999999 !important;
            writing-mode: horizontal-tb !important;
            white-space: normal !important;
            overflow-x: hidden !important;
        }}
        section[data-testid="stSidebar"] * {{
            writing-mode: horizontal-tb !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
        }}

        html, body, [data-testid="stAppViewContainer"], .main {{
            font-family: 'Cairo', 'Inter', sans-serif !important;
            direction: {direction};
            text-align: {align_text};
            background-color: {bg_main} !important;
            color: {text_color} !important;
            overflow-x: hidden !important;
        }}

        .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {{
            color: {label_color} !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            margin-bottom: 8px !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }}

        div[data-baseweb="input"], 
        div[data-baseweb="select"], 
        div[data-baseweb="base-input"], 
        div[data-baseweb="textarea"],
        input[type="text"],
        textarea {{
            background-color: {input_bg} !important;
            background: {input_bg} !important;
            border: 2px solid {input_border} !important;
            border-radius: 12px !important;
            color: {input_text} !important;
            -webkit-text-fill-color: {input_text} !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        }}

        div[data-baseweb="input"]:focus-within, 
        div[data-baseweb="select"]:focus-within, 
        div[data-baseweb="textarea"]:focus-within {{
            border-color: {input_focus_border} !important;
            box-shadow: 0 0 18px rgba(96, 165, 250, 0.6) !important;
        }}

        input::placeholder, textarea::placeholder {{
            color: #cbd5e1 !important;
            -webkit-text-fill-color: #cbd5e1 !important;
            opacity: 0.85 !important;
        }}

        button[data-baseweb="tab"] {{
            background-color: rgba(30, 41, 59, 0.6) !important;
            border-radius: 8px 8px 0 0 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 10px 16px !important;
            margin-right: 4px !important;
        }}
        button[data-baseweb="tab"] p {{
            color: #cbd5e1 !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
        }}
        button[aria-selected="true"] {{
            background-color: #2563eb !important;
            border-bottom: 3px solid #60a5fa !important;
        }}
        button[aria-selected="true"] p {{
            color: #ffffff !important;
            font-weight: 800 !important;
        }}

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
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
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
            background: #1e293b;
            border: 1px solid #3b82f6;
            border-radius: 14px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
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

        @media (max-width: 768px) {{
            .hero-header {{
                font-size: 1.6rem !important;
            }}
            section[data-testid="stSidebar"] {{
                width: 85vw !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 9. HITL TASK EDITOR
# =====================================================================
def render_hitl_task_editor(plan: dict):
    st.markdown("### ✏️ تعديل ومراجعة المهام المباشرة (HITL Engine)")
    st.caption("يمكنك تعديل أي قيمة، وسيقوم المحرك بإعادة الحسابات والتوقيع الرقمي فوراً.")

    tasks = plan.get("tasks", [])
    updated_tasks = []

    p_opts = ["High", "Medium", "Low"]

    for idx, task in enumerate(tasks):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                t_title = st.text_input(f"عنوان المهمة #{idx+1}", value=task.get('title', ''), key=f"t_title_{idx}")
            with col2:
                t_days = st.number_input(f"الأيام", min_value=1, value=int(task.get('days', 1)), key=f"t_days_{idx}")
            with col3:
                t_cost = st.number_input(f"التكلفة ($)", min_value=0, value=int(task.get('cost', 100)), step=50, key=f"t_cost_{idx}")
            with col4:
                raw_priority = str(task.get('priority', 'Medium')).capitalize()
                selected_index = p_opts.index(raw_priority) if raw_priority in p_opts else 1
                t_priority = st.selectbox(f"الأولوية", p_opts, index=selected_index, key=f"t_prio_{idx}")

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
# 10. AUTHENTICATION PAGE
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
                else:
                    st.error("بيانات الدخول غير صحيحة.")

        with tab_signup:
            name = st.text_input(t["full_name"], key="signup_name")
            email = st.text_input(t["email"], key="signup_email")
            p1 = st.text_input(t["password"], type="password", key="signup_pass")
            p2 = st.text_input(t["confirm_password"], type="password", key="signup_confirm")
            if st.button(t["signup_btn"], use_container_width=True):
                if DatabaseEngine.get_user_by_email(email):
                    st.error("⚠️ البريد الإلكتروني مسجل مسبقاً.")
                elif p1 != p2:
                    st.error("⚠️ كلمات المرور غير متطابقة.")
                elif not name or not email or not p1:
                    st.error("⚠️ يرجى ملء جميع الحقول.")
                else:
                    hashed = VaultSecurity.hash_password(p1)
                    if DatabaseEngine.register_user(name, email, hashed, 5, "Free Trial"):
                        st.success("✅ تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
                    else:
                        st.error("❌ فشل إنشاء الحساب. يرجى المحاولة مرة أخرى.")


# =====================================================================
# 11. MAIN APPLICATION
# =====================================================================
def main():
    st.set_page_config(page_title="PHOENIX PRO ULTIMATE", page_icon="🧠", layout="wide")
    init_session()

    # تهيئة قاعدة البيانات
    DatabaseEngine.init_db()
    db_status = "🟢 متصلة" if DatabaseEngine.is_connected() else "🔴 غير متصلة"

    if not st.session_state.authenticated:
        render_auth_page()
        return

    t = TRANSLATIONS[st.session_state.lang]
    user = st.session_state.current_user

    # ----- SIDEBAR (مدمج من الكودين) -----
    with st.sidebar:
        st.markdown("<h3 style='text-align:center;'>⚙️ PHOENIX</h3>", unsafe_allow_html=True)

        # حالة قاعدة البيانات مع زر تحديث
        col_status, col_refresh = st.columns([3, 1])
        with col_status:
            st.caption(f"📡 قاعدة البيانات: **{db_status}**")
        with col_refresh:
            if st.button("🔄", help="التحقق من حالة قاعدة البيانات"):
                if DatabaseEngine.refresh_status():
                    st.success("✅ قاعدة البيانات متصلة!")
                else:
                    st.error("❌ فشل الاتصال بقاعدة البيانات.")
                st.rerun()

        # تبديل اللغة والثيم
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
            st.session_state.authenticated = False
            st.rerun()

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
        col_m.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email, "monthly")}" target="_blank" class="pay-btn">{t["monthly"]}</a>', unsafe_allow_html=True)
        col_y.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email, "yearly")}" target="_blank" class="pay-btn">{t["yearly"]}</a>', unsafe_allow_html=True)

        act_code = st.text_input(t["activate_code"], type="password")
        if st.button(t["activate_btn"], use_container_width=True):
            if act_code in ["PRO2026", "PHOENIX"]:
                DatabaseEngine.update_user_credits(user.get("email"), 9999, "Unlimited")
                user["credits"] = 9999
                user["plan_status"] = "Unlimited"
                st.success("تم التفعيل!")
                st.rerun()

    # ----- MAIN AREA -----
    inject_custom_css()
    st.markdown(f'<div class="hero-header">{t["title"]}</div>', unsafe_allow_html=True)

    # الأربع علامات تبويب
    tab_gen, tab_an, tab_dash, tab_exp = st.tabs([t["tab_gen"], t["tab_analytics"], t["tab_dashboard"], t["tab_export"]])

    # TAB 1: توليد الخطة مع HITL
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
            if not api_key:
                st.error("أدخل مفتاح Gemini API.")
            elif user.get("credits", 0) <= 0:
                st.error("انتهى الرصيد.")
            else:
                with st.spinner("جاري التوليد..."):
                    try:
                        req = {"client": client, "desc": desc, "budget": budget, "timeline": timeline, "tech": tech}
                        plan = PhoenixAI.generate_architecture(api_key, req, lang=st.session_state.lang)
                        # حفظ الخطة وتحديث الرصيد
                        if DatabaseEngine.save_project(user.get("email"), plan):
                            user["credits"] -= 1
                            DatabaseEngine.update_user_credits(user.get("email"), user["credits"])
                            st.session_state.selected_plan = plan
                            # إشعارات
                            if tg_bot and tg_chat:
                                try:
                                    requests.post(f"https://api.telegram.org/bot{tg_bot}/sendMessage", json={"chat_id": tg_chat, "text": f"🚀 New Plan: {plan.get('client')}", "parse_mode": "Markdown"}, timeout=5)
                                except: pass
                            st.success(f"✅ تم التوليد! المتبقي: {user['credits']}")
                            st.rerun()
                        else:
                            st.error("❌ فشل حفظ الخطة في قاعدة البيانات.")
                    except Exception as e:
                        st.error(str(e))

        if st.session_state.selected_plan:
            plan = st.session_state.selected_plan
            st.divider()
            st.markdown(f"""
            <div class="plan-box">
                <h4>🏛️ {plan.get('client')}</h4>
                <p><b>📅 Date:</b> {plan.get('timestamp')}</p>
                <p><b>🔑 Digital Signature:</b> <code>{plan.get('signature')}</code></p>
                <hr style="border-color:rgba(255,255,255,0.15);">
                <h5>📝 Executive Summary:</h5>
                <p style="line-height:1.7;">{plan.get('executive_summary')}</p>
                <hr style="border-color:rgba(255,255,255,0.15);">
                <h5>🛠️ Tech Stack:</h5>
                <p><code>{"  |  ".join(plan.get('tech_stack', []))}</code></p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br/>", unsafe_allow_html=True)
            render_hitl_task_editor(plan)

    # TAB 2: تحليلات متقدمة (من الكود الثاني)
    with tab_an:
        if st.session_state.selected_plan:
            AnalyticsEngine.render_advanced_analytics(st.session_state.selected_plan)
        else:
            st.info("قم بتوليد خطة أولاً.")

    # TAB 3: لوحة تحكم المشاريع
    with tab_dash:
        projects = DatabaseEngine.get_projects(user.get("email"))
        if projects:
            st.dataframe(pd.DataFrame(projects), use_container_width=True)
        else:
            st.info("لا توجد مشاريع.")

    # TAB 4: تصدير
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
