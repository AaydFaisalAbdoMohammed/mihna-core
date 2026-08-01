#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  وكيل مهنة PHOENIX PRO - النسخة الألماسية المدمجة (Enterprise Edition)       ║
║  تجمع بين الهيكلية النظيفة (OOP)، الواجهة العصرية، والترسانة التقنية الكاملة ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import uuid
import hashlib
import hmac
import time
import secrets
import requests
import bcrypt
import jwt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
import google.generativeai as genai

# ============================================================
# 0. معالجة الوحدات الاختيارية (لتجنب انهيار Cloud Shell)
# ============================================================
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import pymysql
    import pymysql.cursors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


# ============================================================
# 1. إعدادات الواجهة (Streamlit Configuration)
# ============================================================
st.set_page_config(page_title="وكيل مهنة PHOENIX PRO", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .main-header { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 1rem; }
    .watermark-badge { font-size: 0.8rem; color: #94a3b8; border: 1px dashed #475569; padding: 6px 12px; border-radius: 6px; background: #1e293b; display: inline-block; }
    .stButton button { background-color: #3b82f6; color: white; border-radius: 8px; font-weight: bold; transition: 0.3s; }
    .stButton button:hover { background-color: #2563eb; transform: scale(1.02); }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. محرك الأمان والتشفير (Security & Cryptography Engine)
# ============================================================
class SecurityEngine:
    JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
    FINGERPRINT_SALT = os.getenv("FINGERPRINT_SALT", secrets.token_hex(16))
    HMAC_KEY = os.getenv("HMAC_KEY", secrets.token_hex(32))

    @staticmethod
    def generate_fingerprint() -> str:
        seed = f"{os.getenv('HOSTNAME', 'unknown')}-{datetime.now().isoformat()}-{uuid.uuid4()}-{os.getpid()}"
        return hashlib.sha256((seed + SecurityEngine.FINGERPRINT_SALT).encode()).hexdigest()[:24]

    @staticmethod
    def generate_digital_signature(data: str) -> str:
        timestamp = str(int(time.time()))
        message = f"{data}:{timestamp}:{SecurityEngine.generate_fingerprint()}"
        signature = hmac.new(SecurityEngine.HMAC_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()[:16]
        return f"SIG-{timestamp[:8]}-{signature}"

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def generate_jwt(user_id: int, username: str) -> str:
        payload = {
            "user_id": user_id,
            "username": username,
            "fingerprint": SecurityEngine.generate_fingerprint(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SecurityEngine.JWT_SECRET, algorithm="HS256")


# ============================================================
# 3. محرك قواعد البيانات (Database Engine)
# ============================================================
class DatabaseEngine:
    @staticmethod
    def get_connection():
        if not MYSQL_AVAILABLE: return None
        try:
            cloud_sql_instance = os.getenv("CLOUD_SQL_CONNECTION_NAME")
            conn_args = {
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv("DB_NAME", "mihna_agent"),
                "charset": "utf8mb4",
                "cursorclass": pymysql.cursors.DictCursor,
                "connect_timeout": 5
            }
            if cloud_sql_instance and os.path.exists(f"/cloudsql/{cloud_sql_instance}"):
                conn_args["unix_socket"] = f"/cloudsql/{cloud_sql_instance}"
            else:
                conn_args["host"] = os.getenv("DB_HOST", "127.0.0.1")
                conn_args["port"] = int(os.getenv("DB_PORT", 3306))
            return pymysql.connect(**conn_args)
        except Exception:
            return None

    @staticmethod
    def init_db():
        conn = DatabaseEngine.get_connection()
        if not conn: return False
        try:
            with conn.cursor() as c:
                c.execute("""CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, email VARCHAR(100) UNIQUE, password_hash VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
                c.execute("""CREATE TABLE IF NOT EXISTS projects (id INT AUTO_INCREMENT PRIMARY KEY, client_name VARCHAR(100), summary TEXT, budget_range VARCHAR(50), tech_stack JSON, digital_signature VARCHAR(64), user_id INT)""")
                conn.commit()
            return True
        finally:
            conn.close()


# ============================================================
# 4. محرك الذكاء الاصطناعي (AI & Generation Engine)
# ============================================================
class AIEngine:
    @staticmethod
    def generate_plan(api_key: str, data: dict) -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        أنت مستشار هندسي في "وكيل مهنة PHOENIX PRO". حلل الفكرة:
        العميل: {data['name']} | الفكرة: {data['idea']} | المدة: {data['timeline']} | الميزانية: {data['budget']}
        
        أخرج الإجابة بتنسيق JSON حصرياً كالتالي:
        {{
            "client_name": "{data['name']}",
            "project_summary": "ملخص تنفيذي",
            "suggested_tech_stack": ["React", "Node.js"],
            "estimated_budget_range": "{data['budget']}",
            "estimated_time_weeks": "{data['timeline']}",
            "risk_score": 15,
            "confidence_score": 92,
            "generated_tasks": [
                {{"title": "مهمة 1", "description": "وصف", "estimated_days": 3, "cost": 500, "priority": "High"}}
            ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            import re
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            plan = json.loads(match.group() if match else response.text)
            plan["digital_signature"] = SecurityEngine.generate_digital_signature(plan.get("project_summary", ""))
            return plan
        except Exception as e:
            raise ValueError(f"فشل التوليد: {str(e)}")


# ============================================================
# 5. محرك الإشعارات (Notification Engine)
# ============================================================
class NotificationEngine:
    @staticmethod
    def send_telegram(plan: dict) -> bool:
        bot_token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
        if not bot_token or not chat_id: return False
        msg = f"🚀 *مشروع جديد PHOENIX PRO*\n\n👤 *العميل:* {plan.get('client_name')}\n💰 *الميزانية:* {plan.get('estimated_budget_range')}\n🔑 *البصمة:* {SecurityEngine.generate_fingerprint()[:16]}"
        try:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=5)
            return True
        except: return False


# ============================================================
# 6. محرك التصدير (Export Engine)
# ============================================================
class ExportEngine:
    @staticmethod
    def build_pdf(data: dict) -> bytes:
        if not REPORTLAB_AVAILABLE: return b""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>Enterprise Plan: {data.get('client_name', '')}</b>", styles['Title']), Spacer(1, 15)]
        
        table_data = [["Task", "Days", "Cost", "Priority"]]
        for t in data.get("generated_tasks", []):
            table_data.append([t.get('title', ''), str(t.get('estimated_days', 0)), f"${t.get('cost', 0)}", t.get('priority', '')])
            
        t = Table(table_data)
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3b82f6")), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke)]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()

    @staticmethod
    def build_excel(tasks: list) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Plan")
        return buffer.getvalue()


# ============================================================
# 7. النظام والتطبيق الرئيسي (Main Application Workflow)
# ============================================================
def init_session():
    if "auth" not in st.session_state: st.session_state.auth = False
    if "points" not in st.session_state: st.session_state.points = 200
    if "plan" not in st.session_state: st.session_state.plan = None

def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/isometric-folders/100/rocket.png", width=80)
        st.markdown("### 🔐 لوحة التحكم المركزية")
        
        if not st.session_state.auth:
            user = st.text_input("👤 المستخدم")
            pwd = st.text_input("🔑 كلمة المرور", type="password")
            if st.button("🚀 تسجيل الدخول", use_container_width=True):
                st.session_state.auth = True # Mocking Auth for demo
                st.rerun()
        else:
            st.success("🟢 متصل")
            st.metric("🏆 نقاط الإنتاجية", f"{st.session_state.points} PTS")
            
            api_key = st.text_input("مفتاح Gemini API", type="password", value=os.getenv("GEMINI_API_KEY", ""))
            st.session_state.api_key = api_key
            
            if st.button("🚪 تسجيل الخروج", use_container_width=True):
                st.session_state.auth = False
                st.rerun()

def main():
    init_session()
    DatabaseEngine.init_db()
    render_sidebar()
    
    st.markdown('<div class="main-header">🔥 وكيل مهنة PHOENIX PRO <br><span style="font-size:1.2rem; color:#94a3b8;">Enterprise AI Architecture</span></div>', unsafe_allow_html=True)

    if not st.session_state.auth:
        st.info("👈 يرجى تسجيل الدخول من القائمة الجانبية للبدء.")
        return

    tabs = st.tabs(["🚀 التوليد الذكي", "🎛️ التعديل البشري (HITL)", "📊 التحليلات المتقدمة", "📦 التصدير والمشاركة"])

    # Tab 1: Generation
    with tabs[0]:
        st.subheader("📝 إعداد الخطة الهندسية")
        c1, c2 = st.columns([2, 1])
        with c1:
            idea = st.text_area("💡 الفكرة:", "تطوير منصة سحابية لإدارة عقود الضمان باستخدام Flutter و Node.js", height=100)
        with c2:
            budget = st.text_input("💰 الميزانية ($)", "5000 - 8000")
            timeline = st.text_input("⏳ المدة المستهدفة", "6 أسابيع")
            name = st.text_input("👤 اسم العميل", "شركة أفق")

        if st.button("⚡ توليد الخطة الاستراتيجية", use_container_width=True):
            if not st.session_state.get('api_key'):
                st.error("يرجى إدخال مفتاح Gemini API في القائمة الجانبية.")
            else:
                with st.spinner("🔄 الذكاء الاصطناعي يحلل المتطلبات ويصيغ الهيكلية..."):
                    try:
                        plan = AIEngine.generate_plan(st.session_state.api_key, {"name": name, "idea": idea, "budget": budget, "timeline": timeline})
                        st.session_state.plan = plan
                        st.session_state.points += 25
                        NotificationEngine.send_telegram(plan)
                        st.success("✅ تم توليد الخطة بنجاح! (+25 نقطة)")
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")

    # Tab 2: HITL
    with tabs[1]:
        st.subheader("🎛️ مراجعة وتعديل المهام يدوياً")
        if st.session_state.plan:
            df = pd.DataFrame(st.session_state.plan.get("generated_tasks", []))
            edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            if st.button("💾 حفظ التعديلات", use_container_width=True):
                st.session_state.plan["generated_tasks"] = edited.to_dict("records")
                st.success("تم تحديث المهام بنجاح.")
        else:
            st.info("قم بتوليد الخطة أولاً.")

    # Tab 3: Analytics
    with tabs[2]:
        st.subheader("📊 ذكاء الأعمال والتحليلات")
        if st.session_state.plan:
            p = st.session_state.plan
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("⚠️ نسبة المخاطرة", f"{p.get('risk_score', 0)}%")
            col2.metric("🎯 نسبة الثقة", f"{p.get('confidence_score', 0)}%")
            tasks = p.get("generated_tasks", [])
            total_cost = sum(float(t.get('cost', 0)) for t in tasks)
            col3.metric("💰 التكلفة التقديرية", f"${total_cost:,.0f}")
            col4.metric("📋 عدد المهام", len(tasks))

            if tasks:
                df_chart = pd.DataFrame(tasks)
                if 'priority' in df_chart.columns and 'estimated_days' in df_chart.columns:
                    fig = px.bar(df_chart, x="title", y="estimated_days", color="priority", title="توزيع الأيام حسب المهام", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("التحليلات تتطلب توليد خطة أولاً.")

    # Tab 4: Export
    with tabs[3]:
        st.subheader("📦 تصدير البيانات ومشاركتها")
        if st.session_state.plan:
            fp = SecurityEngine.generate_fingerprint()
            st.markdown(f'<div class="watermark-badge">🔐 البصمة الرقمية: {fp}</div><br><br>', unsafe_allow_html=True)
            
            c_a, c_b, c_c = st.columns(3)
            
            # JSON
            json_str = json.dumps(st.session_state.plan, ensure_ascii=False, indent=2)
            c_a.download_button("📦 تصدير JSON خام", json_str, "plan.json", "application/json", use_container_width=True)
            
            # Excel
            excel_bytes = ExportEngine.build_excel(st.session_state.plan.get("generated_tasks", []))
            c_b.download_button("📊 تصدير Excel", excel_bytes, "plan.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
            # PDF
            if REPORTLAB_AVAILABLE:
                pdf_bytes = ExportEngine.build_pdf(st.session_state.plan)
                c_c.download_button("📄 تصدير PDF", pdf_bytes, "plan.pdf", "application/pdf", use_container_width=True)
            else:
                c_c.warning("مكتبة ReportLab غير مثبتة للتصدير كـ PDF.")
        else:
            st.info("لا توجد بيانات للتصدير.")

if __name__ == "__main__":
    main()
