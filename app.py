#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & MIHNA AGENT PRO - النسخة النهائية المدمجة (Enterprise Grade)
تطبيق شامل يجمع بين إدارة المشاريع الذكية، الهندسة المعمارية للنظم المشفرة،
نظام المصادقة والتفعيل، تحليلات تفاعلية، والتحكم بالمهام (HITL).
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

# ----------------- Optional Dependencies Handling -----------------
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
# 1. TRANSLATION & DICTIONARY ENGINE
# =====================================================================
TRANSLATIONS = {
    "ar": {
        "title": "🧠 وكيل مهنة & PHOENIX PRO",
        "subtitle": "منصة إدارة المشاريع والهندسة المعمارية الذكية والمشفرة",
        "login_tab": "🔑 تسجيل الدخول",
        "signup_tab": "📝 حساب جديد",
        "email": "البريد الإلكتروني / اسم المستخدم",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "full_name": "الاسم الكامل / اسم المنظمة",
        "login_btn": "تسجيل الدخول",
        "signup_btn": "إنشاء حساب",
        "logout": "🚪 تسجيل الخروج",
        "user": "المستخدم",
        "credits": "⚡ المحاولات المتبقية",
        "plan": "نوع الاشتراك",
        "gemini_key": "🔑 مفتاح Gemini API",
        "tg_title": "📲 إشعارات Telegram",
        "email_title": "📧 إشعارات البريد (SMTP)",
        "sub_title": "💳 الترقية والاشتراكات",
        "tab_gen": "🚀 إنشاء خطة وهندسة جديدة",
        "tab_analytics": "📊 التحليلات التفاعلية",
        "tab_dashboard": "🗄️ أرشيف مشاريعك",
        "tab_export": "📦 التصدير والتوثيق",
        "client": "🏢 اسم العميل / الشركة",
        "budget": "💰 الميزانية المقدرة",
        "timeline": "⏱️ الجدول الزمني",
        "tech": "🛠️ التقنيات المفضلة",
        "scope": "💡 صف رؤية أو فكرة مشروعك بالتفصيل",
        "generate_btn": "🚀 توليد الخطة والتوقيع المشفر",
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
        "monthly": "🗓️ شهري ($9.99)",
        "yearly": "⭐ سنوي ($99.99)"
    },
    "en": {
        "title": "🧠 MIHNA & PHOENIX PRO ENTERPRISE",
        "subtitle": "AI-Powered Architecture & Project Engineering Management",
        "login_tab": "🔑 Login",
        "signup_tab": "📝 Sign Up",
        "email": "Email / Username",
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
        "sub_title": "💳 Subscriptions & Upgrades",
        "tab_gen": "🚀 Generate Architecture Plan",
        "tab_analytics": "📊 Interactive Analytics",
        "tab_dashboard": "🗄️ Projects Archive",
        "tab_export": "📦 Secure Export",
        "client": "🏢 Client / Company Name",
        "budget": "💰 Estimated Budget",
        "timeline": "⏱️ Target Timeline",
        "tech": "🛠️ Preferred Tech Stack",
        "scope": "💡 Project Vision / Detailed Scope",
        "generate_btn": "🚀 Generate Architecture & Sign",
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
        "monthly": "🗓️ Monthly ($9.99)",
        "yearly": "⭐ Yearly ($99.99)"
    }
}


# =====================================================================
# 2. SECURITY & INTEGRITY ENGINE
# =====================================================================
class VaultSecurity:
    HMAC_KEY = os.getenv("HMAC_KEY", secrets.token_hex(32))

    @classmethod
    def generate_fingerprint(cls) -> str:
        seed = f"{os.getenv('HOSTNAME', 'localhost')}-{datetime.datetime.now().isoformat()}-{uuid.uuid4()}"
        return hashlib.sha256((seed + cls.HMAC_KEY[:16]).encode()).hexdigest()[:24]

    @classmethod
    def sign_payload(cls, payload: dict) -> str:
        clean_payload = {k: v for k, v in payload.items() if k not in ["signature", "timestamp"]}
        payload_str = json.dumps(clean_payload, sort_keys=True, ensure_ascii=False)
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
# 3. DATABASE ENGINE (WITH HYBRID FALLBACK & RAG SUPPORT)
# =====================================================================
class DatabaseEngine:
    _connection_status = None

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

            conn_args = {
                "user": db_user,
                "password": db_pass,
                "database": db_name,
                "charset": "utf8mb4",
                "cursorclass": pymysql.cursors.DictCursor,
                "connect_timeout": 5
            }

            if cloud_sql_instance and os.path.exists(f"/cloudsql/{cloud_sql_instance}"):
                conn_args["unix_socket"] = f"/cloudsql/{cloud_sql_instance}"
            else:
                conn_args["host"] = db_host
                conn_args["port"] = db_port

            conn = pymysql.connect(**conn_args)
            DatabaseEngine._connection_status = True
            return conn
        except Exception as e:
            DatabaseEngine._connection_status = False
            logging.error(f"DB Connection Failed: {e}")
            return None

    @classmethod
    def is_connected(cls):
        conn = cls.get_db_connection()
        if conn:
            conn.close()
            return True
        return False

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
            return
        try:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) UNIQUE,
                        email VARCHAR(100) UNIQUE,
                        password VARCHAR(255),
                        credits INT DEFAULT 5,
                        plan_status VARCHAR(50) DEFAULT 'Free Trial',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(100),
                        client_name VARCHAR(100),
                        summary TEXT,
                        budget_range VARCHAR(50),
                        tech_stack JSON,
                        payload JSON,
                        signature VARCHAR(64),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        project_id INT,
                        title VARCHAR(200),
                        description TEXT,
                        estimated_days INT,
                        priority VARCHAR(20),
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    )
                """)
                conn.commit()
        except Exception as e:
            logging.error(f"Init DB Schema Error: {e}")
        finally:
            conn.close()

    @classmethod
    def get_user(cls, identifier: str):
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as c:
                    c.execute("SELECT * FROM users WHERE email = %s OR username = %s", (identifier, identifier))
                    return c.fetchone()
            finally:
                conn.close()
        # Fallback Storage
        fallback = cls._get_fallback_store()["users"]
        return fallback.get(identifier)

    @classmethod
    def register_user(cls, username: str, email: str, hashed_pass: str, credits=5, plan_status="Free Trial"):
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as c:
                    c.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
                    if c.fetchone():
                        return False
                    c.execute("INSERT INTO users (username, email, password, credits, plan_status) VALUES (%s, %s, %s, %s, %s)",
                              (username, email, hashed_pass, credits, plan_status))
                conn.commit()
                return True
            except Exception:
                return False
            finally:
                conn.close()

        # Fallback Local DB
        fallback = cls._get_fallback_store()
        if email in fallback["users"] or username in fallback["users"]:
            return False
        user_data = {
            "id": fallback["next_user_id"],
            "username": username,
            "email": email,
            "password": hashed_pass,
            "credits": credits,
            "plan_status": plan_status
        }
        fallback["users"][email] = user_data
        fallback["users"][username] = user_data
        fallback["next_user_id"] += 1
        return True

    @classmethod
    def update_credits(cls, identifier: str, credits: int, status: str = None):
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as c:
                    if status:
                        c.execute("UPDATE users SET credits=%s, plan_status=%s WHERE email=%s OR username=%s", (credits, status, identifier, identifier))
                    else:
                        c.execute("UPDATE users SET credits=%s WHERE email=%s OR username=%s", (credits, identifier, identifier))
                conn.commit()
                return True
            finally:
                conn.close()

        fallback = cls._get_fallback_store()["users"]
        if identifier in fallback:
            fallback[identifier]["credits"] = credits
            if status:
                fallback[identifier]["plan_status"] = status
            return True
        return False

    @classmethod
    def save_project(cls, identifier: str, plan_json: dict):
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as c:
                    c.execute("""
                        INSERT INTO projects (user_id, client_name, summary, budget_range, tech_stack, payload, signature)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        identifier,
                        plan_json.get('client', 'غير محدد'),
                        plan_json.get('executive_summary', ''),
                        plan_json.get('budget_str', ''),
                        json.dumps(plan_json.get('tech_stack', [])),
                        json.dumps(plan_json, ensure_ascii=False),
                        plan_json.get('signature', '')
                    ))
                    project_id = c.lastrowid
                    for task in plan_json.get('tasks', []):
                        c.execute("""
                            INSERT INTO tasks (project_id, title, description, estimated_days, priority)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (project_id, task.get('title'), task.get('description'), task.get('days', 2), task.get('priority', 'Medium')))
                conn.commit()
                return True
            except Exception as e:
                logging.error(f"Save Project SQL Error: {e}")
                return False
            finally:
                conn.close()

        # Fallback Storage
        fallback = cls._get_fallback_store()
        pid = fallback["next_project_id"]
        project_record = {
            "id": pid,
            "user_id": identifier,
            "client_name": plan_json.get('client'),
            "summary": plan_json.get('executive_summary'),
            "budget_range": plan_json.get('budget_str'),
            "signature": plan_json.get('signature'),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        fallback["projects"][pid] = project_record
        fallback["next_project_id"] += 1
        return True

    @classmethod
    def get_projects(cls, identifier: str):
        conn = cls.get_db_connection()
        if conn:
            try:
                with conn.cursor() as c:
                    c.execute("SELECT id, client_name, summary, budget_range, created_at, signature FROM projects WHERE user_id = %s ORDER BY created_at DESC", (identifier,))
                    return c.fetchall()
            finally:
                conn.close()

        fallback = cls._get_fallback_store()["projects"]
        results = [p for p in fallback.values() if p.get("user_id") == identifier]
        return sorted(results, key=lambda x: x["created_at"], reverse=True)

    @classmethod
    def get_similar_projects(cls, keyword: str, top_k: int = 2) -> list:
        conn = cls.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as c:
                words = [w for w in re.findall(r'\w+', keyword) if len(w) > 3]
                if not words:
                    return []
                conditions = " OR ".join(["(summary LIKE %s OR client_name LIKE %s)" for _ in words[:3]])
                params = []
                for w in words[:3]:
                    pattern = f"%{w}%"
                    params.extend([pattern, pattern])
                c.execute(f"SELECT summary, client_name FROM projects WHERE {conditions} LIMIT {top_k}", params)
                return c.fetchall()
        except Exception:
            return []
        finally:
            conn.close()


# =====================================================================
# 4. AI CORE ENGINE (GEMINI + RAG)
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict, lang: str = "ar") -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        similar = DatabaseEngine.get_similar_projects(req.get("desc", ""), top_k=2)
        context = ""
        if similar:
            context = "\n\n**📚 مشاريع سابقة مشابهة (RAG Memory Context):**\n"
            for p in similar:
                context += f"- {p.get('summary', '')[:150]}...\n"

        lang_str = "اللغة العربية" if lang == "ar" else "English Language"
        prompt = f"""
أنت مهندس معمارية نظم وخبير إدارة مشاريع برمجية.
قم بتحليل متطلبات المشروع التالية لبناء خطة عمل وتنفيذ هيلكية كاملة:

📋 **البيانات والمدخلات:**
- العميل / المنظمة: {req['client']}
- النطاق والرؤية: {req['desc']}
- الميزانية المستهدفة: {req['budget']}
- الجدول الزمني: {req['timeline']}
- التقنيات التفضيلية: {req['tech']}
{context}

🎯 **المطلوب:**
قم بتوليد استجابة بصيغة JSON فقط (صريحة ونقية بدون أي نصوص قبلية أو بعدها) بالتنسيق التالي:
{{
  "client": "{req['client']}",
  "executive_summary": "ملخص تنفيذي هندسي شامل باللغة ({lang_str})",
  "tech_stack": ["تقنية 1", "تقنية 2", "تقنية 3"],
  "budget_str": "{req['budget']}",
  "timeline": "{req['timeline']}",
  "risk_score": 25,
  "confidence_score": 90,
  "tasks": [
    {{
      "title": "عنوان المهمة",
      "description": "وصف تفصيلي ودقيق للمهمة",
      "days": 4,
      "cost": 600,
      "priority": "High"
    }}
  ]
}}

📌 **شروط إضافية:**
- الأولوية تكون حصراً: High, Medium, Low.
- عدد المهام: بين 4 إلى 7 مهام أساسية.
- كتابة الشروح باللغة: {lang_str}.
"""
        try:
            response = model.generate_content(prompt)
            raw = response.text
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(raw.strip())

            data["signature"] = VaultSecurity.sign_payload(data)
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            return data
        except Exception as e:
            raise ValueError(f"فشل توليد الخطة عبر الذكاء الاصطناعي: {e}")


# =====================================================================
# 5. ADVANCED ANALYTICS ENGINE
# =====================================================================
class AnalyticsEngine:
    @staticmethod
    def compute_metrics(plan: dict) -> dict:
        tasks = plan.get("tasks", [])
        total_days = sum(int(t.get('days', 0)) for t in tasks)
        total_tasks = len(tasks)
        high = sum(1 for t in tasks if str(t.get('priority', '')).lower() == 'high')
        med = sum(1 for t in tasks if str(t.get('priority', '')).lower() == 'medium')
        low = sum(1 for t in tasks if str(t.get('priority', '')).lower() == 'low')

        base_cost = total_days * 150
        overhead = base_cost * 0.20
        total_cost = base_cost + overhead

        high_ratio = high / total_tasks if total_tasks else 0
        long_tasks = sum(1 for t in tasks if int(t.get('days', 0)) > 5)
        long_ratio = long_tasks / total_tasks if total_tasks else 0

        risk_score = min(100, int((high_ratio * 0.6 + long_ratio * 0.4) * 100))
        confidence_score = plan.get('confidence_score', 85)

        return {
            'total_days': total_days,
            'total_tasks': total_tasks,
            'high': high, 'med': med, 'low': low,
            'base_cost': base_cost,
            'overhead': overhead,
            'total_cost': total_cost,
            'risk_score': risk_score,
            'confidence_score': confidence_score,
            'avg_days': total_days / total_tasks if total_tasks else 0,
            'long_tasks': long_tasks
        }

    @staticmethod
    def render_analytics(plan: dict):
        m = AnalyticsEngine.compute_metrics(plan)
        tasks = plan.get("tasks", [])

        st.markdown("## 📊 التحليل الهندسي والمالي التفصيلي")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 إجمالي الأيام", f"{m['total_days']} يوم")
        c2.metric("💰 التكلفة المقدرة", f"${m['total_cost']:,.0f}", delta=f"${m['base_cost']:,.0f} أساسي")
        c3.metric("⚠️ درجة المخاطرة", f"{m['risk_score']}%", delta="عالية" if m['risk_score'] > 50 else "منخفضة")
        c4.metric("🎯 نسبة الثقة", f"{m['confidence_score']}%")
        st.divider()

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig1 = go.Figure(data=[go.Pie(
                labels=['عالية (High)', 'متوسطة (Medium)', 'منخفضة (Low)'],
                values=[m['high'], m['med'], m['low']],
                marker=dict(colors=['#ef4444', '#f59e0b', '#10b981']),
                hole=0.35
            )])
            fig1.update_layout(title="توزيع المهام حسب مستوى الأولوية")
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            if tasks:
                df_tasks = pd.DataFrame(tasks)
                fig2 = px.bar(
                    df_tasks, x='title', y='days', color='priority',
                    title="المدة الزمنية التقديرية لكل مهمة (أيام)",
                    color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'}
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 📋 جدول مؤشرات الأداء الحيوية (KPIs)")
        df_analytics = pd.DataFrame({
            'المقياس الهندسي': [
                'إجمالي أيام التنفيذ', 'عدد المهام الكلي', 'مهام عالية الأولوية', 'مهام متوسطة', 'مهام منخفضة',
                'التكلفة التشغيلية الأساسية', 'تكلفة المخاطر والطوارئ', 'التكلفة الكلية المتوقعة',
                'مؤشر المخاطرة المعمارية', 'درجة ثقة النموذج', 'متوسط أمد المهمة الواحدة'
            ],
            'القيمة التقديرية': [
                f"{m['total_days']} أيام", m['total_tasks'], m['high'], m['med'], m['low'],
                f"${m['base_cost']:,.0f}", f"${m['overhead']:,.0f}", f"${m['total_cost']:,.0f}",
                f"{m['risk_score']}%", f"{m['confidence_score']}%", f"{m['avg_days']:.1f} يوم"
            ]
        })
        st.dataframe(df_analytics, use_container_width=True, hide_index=True)


# =====================================================================
# 6. EXPORT ENGINE (MULTI-FORMAT)
# =====================================================================
class ExportEngine:
    @staticmethod
    def generate_pdf(plan: dict) -> bytes:
        if not REPORTLAB_AVAILABLE:
            return b""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"<b>Enterprise Architecture Document</b>", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Client:</b> {plan.get('client')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Budget:</b> {plan.get('budget_str')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Signature:</b> {plan.get('signature')}", styles['Normal']))
        elements.append(Spacer(1, 12))

        table_data = [["Task", "Days", "Cost ($)", "Priority"]]
        for t in plan.get("tasks", []):
            table_data.append([t.get('title', ''), str(t.get('days', '')), f"${t.get('cost', 0)}", t.get('priority', '')])

        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
        ]))
        elements.append(t)
        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def generate_excel(plan: dict) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame([{
                'العميل': plan.get('client'),
                'الملخص': plan.get('executive_summary'),
                'الميزانية': plan.get('budget_str'),
                'التوقيع الرقمي': plan.get('signature')
            }]).to_excel(writer, sheet_name='الملخص', index=False)

            if plan.get('tasks'):
                pd.DataFrame(plan['tasks']).to_excel(writer, sheet_name='المهام', index=False)
        return buffer.getvalue()

    @staticmethod
    def generate_txt(plan: dict) -> bytes:
        txt = f"=== خطة مشروع: {plan.get('client')} ===\n"
        txt += f"التاريخ: {plan.get('timestamp')}\n"
        txt += f"التوقيع الرقمي: {plan.get('signature')}\n\n"
        txt += f"الملخص التنفيذي:\n{plan.get('executive_summary')}\n\n"
        txt += "المهام التنفيذية:\n"
        for i, t in enumerate(plan.get("tasks", []), 1):
            txt += f"{i}. {t.get('title')} ({t.get('priority')}) - {t.get('days')} أيام\n"
            txt += f"   الوصف: {t.get('description')}\n"
        return txt.encode('utf-8')


# =====================================================================
# 7. NOTIFICATION & PAYMENT ENGINE
# =====================================================================
class CommercialEngine:
    @staticmethod
    def send_telegram(plan: dict, bot_token: str, chat_id: str) -> bool:
        if not bot_token or not chat_id:
            return False
        msg = (
            f"🚀 *مشروع جديد - وكيل مهنة PRO*\n\n"
            f"👤 *العميل:* {plan.get('client')}\n"
            f"💰 *الميزانية:* {plan.get('budget_str')}\n"
            f"🔑 *التوقيع:* `{plan.get('signature', 'N/A')}`\n"
            f"⏱️ *التاريخ:* {plan.get('timestamp')}"
        )
        try:
            res = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    @staticmethod
    def get_checkout_url(email: str, plan_type: str = "monthly") -> str:
        store_slug = os.getenv("LEMONSQUEEZY_STORE_SLUG", "mihna")
        return f"https://{store_slug}.lemonsqueezy.com/buy?checkout[email]={email.strip()}&plan={plan_type}"


# =====================================================================
# 8. UI STYLE & CSS INJECTION
# =====================================================================
def init_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "selected_plan" not in st.session_state:
        st.session_state.selected_plan = None
    if "lang" not in st.session_state:
        st.session_state.lang = "ar"
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

def inject_custom_css():
    lang = st.session_state.lang
    theme = st.session_state.theme
    direction = "rtl" if lang == "ar" else "ltr"

    if theme == "dark":
        bg_main, bg_sidebar = "#0b0f19", "#0f172a"
        text_color = "#f8fafc"
        input_bg = "#1e293b"
        input_text = "#ffffff"
        input_border = "#3b82f6"
    else:
        bg_main, bg_sidebar = "#f8fafc", "#ffffff"
        text_color = "#0f172a"
        input_bg = "#ffffff"
        input_text = "#0f172a"
        input_border = "#2563eb"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Cairo', sans-serif !important;
            direction: {direction};
            background-color: {bg_main} !important;
            color: {text_color} !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {bg_sidebar} !important;
        }}

        .stButton button {{
            border-radius: 8px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
        }}

        .plan-card {{
            background-color: {input_bg};
            border: 1px solid {input_border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 9. HITL (HUMAN-IN-THE-LOOP) TASK EDITOR
# =====================================================================
def render_hitl_editor(plan: dict):
    st.markdown("### ✏️ مراجعة وتعديل المهام التفاعلي (HITL Engine)")
    st.caption("تتيح لك هذه الأداة تعديل المهام والقيام بإعادة حساب التوقيع الرقمي فوراً.")

    tasks = plan.get("tasks", [])
    updated_tasks = []
    p_options = ["High", "Medium", "Low"]

    for idx, task in enumerate(tasks):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                title = st.text_input(f"المهمة #{idx+1}", value=task.get('title', ''), key=f"hitl_t_{idx}")
            with c2:
                days = st.number_input(f"الأيام", min_value=1, value=int(task.get('days', 2)), key=f"hitl_d_{idx}")
            with c3:
                cost = st.number_input(f"التكلفة ($)", min_value=0, value=int(task.get('cost', 100)), key=f"hitl_c_{idx}")
            with c4:
                curr_prio = str(task.get('priority', 'Medium')).capitalize()
                idx_prio = p_options.index(curr_prio) if curr_prio in p_options else 1
                prio = st.selectbox(f"الأولوية", p_options, index=idx_prio, key=f"hitl_p_{idx}")

            desc = st.text_area(f"الوصف #{idx+1}", value=task.get('description', ''), key=f"hitl_desc_{idx}", height=60)

            updated_tasks.append({
                "title": title,
                "description": desc,
                "days": days,
                "cost": cost,
                "priority": prio
            })

    if st.button("✅ اعتماد التعديلات وتحديث التوقيع الرقمي", type="primary", use_container_width=True):
        plan["tasks"] = updated_tasks
        plan["signature"] = VaultSecurity.sign_payload(plan)
        st.session_state.selected_plan = plan
        st.success("✅ تم تحديث الخطة، التوقيع المشفر، والتحليلات بنجاح!")
        st.rerun()


# =====================================================================
# 10. AUTHENTICATION PAGE
# =====================================================================
def render_auth_page():
    t = TRANSLATIONS[st.session_state.lang]
    inject_custom_css()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center;'>{t['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>{t['subtitle']}</p>", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs([t["login_tab"], t["signup_tab"]])

        with tab_login:
            identifier = st.text_input(t["email"], key="login_id")
            password = st.text_input(t["password"], type="password", key="login_pass")
            if st.button(t["login_btn"], use_container_width=True, type="primary"):
                user = DatabaseEngine.get_user(identifier)
                if user and VaultSecurity.verify_password(password, user["password"]):
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("✅ تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة.")

        with tab_signup:
            username = st.text_input("اسم المستخدم", key="signup_user")
            email = st.text_input("البريد الإلكتروني", key="signup_email")
            p1 = st.text_input(t["password"], type="password", key="signup_p1")
            p2 = st.text_input(t["confirm_password"], type="password", key="signup_p2")

            if st.button(t["signup_btn"], use_container_width=True):
                if p1 != p2:
                    st.error("⚠️ كلمتا المرور غير متطابقتين.")
                elif not username or not email or not p1:
                    st.error("⚠️ يرجى إكمال جميع الحقول.")
                else:
                    hashed = VaultSecurity.hash_password(p1)
                    if DatabaseEngine.register_user(username, email, hashed):
                        st.success("✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
                    else:
                        st.error("❌ اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل.")


# =====================================================================
# 11. MAIN APPLICATION ENTRY
# =====================================================================
def main():
    st.set_page_config(page_title="وكيل مهنة PRO - PHOENIX Enterprise", page_icon="🧠", layout="wide")
    init_session()

    # Initialize Database
    DatabaseEngine.init_db()

    if not st.session_state.authenticated:
        render_auth_page()
        return

    inject_custom_css()
    t = TRANSLATIONS[st.session_state.lang]
    user = st.session_state.user

    # ----- SIDEBAR -----
    with st.sidebar:
        st.markdown(f"### 👤 {user.get('username', 'المستخدم')}")
        st.caption(f"📧 {user.get('email', '')}")
        st.info(f"⚡ {t['credits']}: {user.get('credits', 0)}")
        st.caption(f"🛡️ {t['plan']}: {user.get('plan_status', 'Free')}")

        if st.button(t["logout"], use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

        st.divider()

        # Language & Theme Switcher
        c_l, c_t = st.columns(2)
        with c_l:
            if st.button("🌐 English" if st.session_state.lang == "ar" else "🌐 العربية", use_container_width=True):
                st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
                st.rerun()
        with c_t:
            if st.button("☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark", use_container_width=True):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                st.rerun()

        st.divider()
        st.markdown("### ⚙️ إعدادات الذكاء الاصطناعي")
        api_key = st.text_input(t["gemini_key"], type="password", value=os.getenv("GEMINI_API_KEY", ""))

        st.divider()
        st.markdown("### 📲 قنوات الإشعار")
        tg_bot = st.text_input("Telegram Bot Token", type="password", value=os.getenv("TELEGRAM_BOT_TOKEN", ""))
        tg_chat = st.text_input("Telegram Chat ID", value=os.getenv("TELEGRAM_CHAT_ID", ""))

        st.divider()
        act_code = st.text_input(t["activate_code"], type="password")
        if st.button(t["activate_btn"], use_container_width=True):
            if act_code in ["PRO2026", "PHOENIX", "MIHNA"]:
                DatabaseEngine.update_credits(user.get("email"), 9999, "VIP Unlimited")
                user["credits"] = 9999
                user["plan_status"] = "VIP Unlimited"
                st.success("✨ تم تفعيل الحساب غير المحدود!")
                st.rerun()

    # ----- MAIN CONTENT AREA -----
    st.markdown(f"<h1 style='text-align:center;'>🧠 {t['title']}</h1>", unsafe_allow_html=True)

    tab_gen, tab_an, tab_dash, tab_exp = st.tabs([t["tab_gen"], t["tab_analytics"], t["tab_dashboard"], t["tab_export"]])

    # TAB 1: GENERATION & ARCHITECTURE
    with tab_gen:
        c1, c2 = st.columns(2)
        with c1:
            client = st.text_input(t["client"], value="مؤسسة أفق التعليمية")
            budget = st.text_input(t["budget"], value="8000 - 12000 $")
        with c2:
            timeline = st.text_input(t["timeline"], value="8 أسابيع")
            tech = st.text_input(t["tech"], value="Flutter, Node.js, Supabase, WebRTC")

        desc = st.text_area(t["scope"], value="منصة تعليمية تفاعلية للطلاب تدعم الفصول المباشرة والاختبارات الآلية...", height=120)

        if st.button(t["generate_btn"], type="primary", use_container_width=True):
            if not api_key:
                st.error("❌ يرجى توفير مفتاح Gemini API في الشريط الجانبي.")
            elif user.get("credits", 0) <= 0:
                st.error("🚫 رصيدك المجاني انتهى! يرجى الاشتراك أو تفعيل كود الخصم.")
            else:
                with st.spinner("🔄 جارِ معالجة المتطلبات وتوليد الخطة..."):
                    try:
                        req = {"client": client, "desc": desc, "budget": budget, "timeline": timeline, "tech": tech}
                        plan = PhoenixAI.generate_architecture(api_key, req, lang=st.session_state.lang)

                        # Save and Deduct
                        if DatabaseEngine.save_project(user.get("email"), plan):
                            user["credits"] -= 1
                            DatabaseEngine.update_credits(user.get("email"), user["credits"])
                            st.session_state.selected_plan = plan

                            # Alert
                            CommercialEngine.send_telegram(plan, tg_bot, tg_chat)
                            st.success("✅ تم توليد الخطة وحفظها بنجاح!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ: {e}")

        if st.session_state.selected_plan:
            plan = st.session_state.selected_plan
            st.divider()
            st.markdown(f"""
            <div class="plan-card">
                <h3>🏢 العميل: {plan.get('client')}</h3>
                <p><b>🔑 التوقيع الرقمي (HMAC-SHA512):</b> <code>{plan.get('signature')}</code></p>
                <p><b>📅 تاريخ التوليد:</b> {plan.get('timestamp')}</p>
                <hr>
                <h4>📌 الملخص التنفيذي:</h4>
                <p>{plan.get('executive_summary')}</p>
            </div>
            """, unsafe_allow_html=True)

            render_hitl_editor(plan)

    # TAB 2: ANALYTICS
    with tab_an:
        if st.session_state.selected_plan:
            AnalyticsEngine.render_analytics(st.session_state.selected_plan)
        else:
            st.info("💡 قم بتوليد خطة أولاً لعرض التحليلات التفاعلية.")

    # TAB 3: DASHBOARD / ARCHIVE
    with tab_dash:
        st.subheader("🗄️ أرشيف مشاريعك المسجلة")
        projects = DatabaseEngine.get_projects(user.get("email"))
        if projects:
            st.dataframe(pd.DataFrame(projects), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد مشاريع سابقة في أرشيفك.")

    # TAB 4: EXPORT OPTIONS
    with tab_exp:
        if st.session_state.selected_plan:
            plan = st.session_state.selected_plan
            st.subheader("📦 تصدير خطة المشروع والوثائق")

            col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

            with col_exp1:
                st.download_button(
                    label=t["export_json"],
                    data=json.dumps(plan, indent=2, ensure_ascii=False),
                    file_name=f"project_{plan.get('client')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col_exp2:
                st.download_button(
                    label=t["export_excel"],
                    data=ExportEngine.generate_excel(plan),
                    file_name=f"project_{plan.get('client')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col_exp3:
                st.download_button(
                    label=t["export_pdf"],
                    data=ExportEngine.generate_pdf(plan),
                    file_name=f"project_{plan.get('client')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with col_exp4:
                st.download_button(
                    label=t["export_txt"],
                    data=ExportEngine.generate_txt(plan),
                    file_name=f"project_{plan.get('client')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.info("💡 يرجى اختيار أو إنشاء خطة أولاً لتتمكن من التصدير.")

if __name__ == "__main__":
    main()
