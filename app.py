#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=======================================================================
© 2026 PHOENIX ULTIMATE – النسخة النهائية الفائزة (Unclonable Edition)
=======================================================================
مشروع متكامل يجمع بين الأمان المتقدم، الذكاء الاصطناعي، التحليلات،
والتصدير، مع دعم كامل للسحابة وقاعدة البيانات.
"""

import os
import sys
import json
import re
import uuid
import hashlib
import hmac
import time
import secrets
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# ====================================================================
# 0. المكتبات الاختيارية (لتفادي الأخطاء)
# ====================================================================
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
    from reportlab.lib.pagesizes import A4
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

# ====================================================================
# 1. محرك الأمان والتشفير المتقدم
# ====================================================================
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
FINGERPRINT_SALT = os.getenv("FINGERPRINT_SALT", secrets.token_hex(16))
HMAC_KEY = os.getenv("HMAC_KEY", secrets.token_hex(32))

def generate_fingerprint() -> str:
    """توليد بصمة رقمية فريدة لكل جلسة."""
    seed = f"{os.getenv('HOSTNAME', 'unknown')}-{datetime.now().isoformat()}-{uuid.uuid4()}-{os.getpid()}"
    return hashlib.sha256((seed + FINGERPRINT_SALT).encode()).hexdigest()[:24]

def generate_digital_signature(data: str) -> str:
    """توليع توقيع HMAC للبيانات."""
    timestamp = str(int(time.time()))
    message = f"{data}:{timestamp}:{generate_fingerprint()}"
    signature = hmac.new(HMAC_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()[:16]
    return f"SIG-{timestamp[:8]}-{signature}"

def generate_jwt(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "fingerprint": generate_fingerprint(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

try:
    import jwt
except ImportError:
    # تعريف دالة بديلة في حال عدم وجود jwt
    def generate_jwt(user_id: int, username: str) -> str:
        return f"fallback_jwt_{user_id}_{username}_{int(time.time())}"

# ====================================================================
# 2. اتصال قاعدة البيانات الموحدة (يدعم Unix Socket و TCP/IP)
# ====================================================================
def get_db_connection():
    if not MYSQL_AVAILABLE:
        return None
    try:
        cloud_sql_instance = os.getenv("CLOUD_SQL_CONNECTION_NAME")
        connection_args = {
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "mihna_agent"),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "connect_timeout": 10
        }
        if cloud_sql_instance and os.path.exists(f"/cloudsql/{cloud_sql_instance}"):
            connection_args["unix_socket"] = f"/cloudsql/{cloud_sql_instance}"
        else:
            connection_args["host"] = os.getenv("DB_HOST", "127.0.0.1")
            connection_args["port"] = int(os.getenv("DB_PORT", 3306))
            if os.getenv("DB_SSL_ENABLED", "false").lower() == "true":
                connection_args["ssl"] = {"ca": "/etc/ssl/certs/ca-certificates.crt"}
        return pymysql.connect(**connection_args)
    except Exception as e:
        st.error(f"❌ فشل الاتصال بقاعدة البيانات: {str(e)}")
        return None

def init_database():
    """إنشاء الجداول تلقائياً إذا لم تكن موجودة."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    fingerprint VARCHAR(64),
                    points INT DEFAULT 0,
                    level INT DEFAULT 1,
                    plan_status VARCHAR(50) DEFAULT 'Free',
                    credits INT DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_name VARCHAR(100),
                    summary TEXT,
                    budget_range VARCHAR(50),
                    tech_stack JSON,
                    digital_signature VARCHAR(64),
                    user_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shared_links (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    share_id VARCHAR(64) UNIQUE,
                    project_id INT,
                    fingerprint VARCHAR(64),
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
    except Exception as e:
        st.error(f"❌ فشل تهيئة قاعدة البيانات: {str(e)}")
    finally:
        conn.close()

# ====================================================================
# 3. دوال RAG والمشاريع
# ====================================================================
def get_similar_projects(keyword: str, top_k: int = 3) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
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
        sql = f"SELECT * FROM projects WHERE {conditions} LIMIT {top_k}"
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"RAG error: {e}")
        return []
    finally:
        conn.close()

def save_project_plan(plan_json: dict, user_id: int) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        signature = generate_digital_signature(json.dumps(plan_json, sort_keys=True))
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO projects (client_name, summary, budget_range, tech_stack, digital_signature, user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                plan_json.get('client_name', ''),
                plan_json.get('project_summary', ''),
                plan_json.get('estimated_budget_range', ''),
                json.dumps(plan_json.get('suggested_tech_stack', [])),
                signature,
                user_id
            ))
            project_id = cursor.lastrowid
            for task in plan_json.get('generated_tasks', []):
                sql_task = """
                    INSERT INTO tasks (project_id, title, description, estimated_days, priority)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_task, (
                    project_id,
                    task.get('title', ''),
                    task.get('description', ''),
                    task.get('estimated_days', 0),
                    task.get('priority', 'Medium')
                ))
            conn.commit()
            return True
    except Exception as e:
        print(f"Save error: {e}")
        return False
    finally:
        conn.close()

def get_user_projects(user_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM projects WHERE user_id = %s ORDER BY id DESC", (user_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Get projects error: {e}")
        return []
    finally:
        conn.close()

def save_shared_link(share_id: str, project_id: int, expires_at: datetime) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO shared_links (share_id, project_id, fingerprint, expires_at) VALUES (%s, %s, %s, %s)",
                (share_id, project_id, generate_fingerprint(), expires_at)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Share link error: {e}")
        return False
    finally:
        conn.close()

def get_shared_project(share_id: str) -> dict:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT project_id, expires_at FROM shared_links WHERE share_id = %s", (share_id,))
            link = cursor.fetchone()
            if not link or datetime.now() > link['expires_at']:
                return None
            cursor.execute("SELECT * FROM projects WHERE id = %s", (link['project_id'],))
            project = cursor.fetchone()
            if project:
                cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (link['project_id'],))
                tasks = cursor.fetchall()
                project['generated_tasks'] = tasks
            return project
    except Exception as e:
        return None
    finally:
        conn.close()

# ====================================================================
# 4. المصادقة (bcrypt + JWT)
# ====================================================================
def init_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_email = None
        st.session_state.jwt_token = None

def hash_password(password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    import bcrypt
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_user(username: str, email: str, password: str) -> tuple:
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "⚠️ البريد الإلكتروني غير صالح"
    if len(username) < 3 or len(password) < 6:
        return False, "⚠️ اسم المستخدم لا يقل عن 3 أحرف وكلمة المرور عن 6 أحرف"
    conn = get_db_connection()
    if not conn:
        return False, "⚠️ تعذر الاتصال بقاعدة البيانات"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return False, "⚠️ اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً"
            hashed_pw = hash_password(password)
            fp = generate_fingerprint()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, fingerprint, points, level, credits) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (username, email, hashed_pw, fp, 0, 1, 5)
            )
            conn.commit()
            return True, "✅ تم إنشاء الحساب بنجاح!"
    except Exception as e:
        return False, f"❌ خطأ: {e}"
    finally:
        conn.close()

def login_user(identifier: str, password: str) -> tuple:
    if not identifier or not password:
        return False, "⚠️ يرجى ملء جميع الحقول"
    conn = get_db_connection()
    if not conn:
        return False, "⚠️ تعذر الاتصال بقاعدة البيانات"
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, points, level, credits FROM users WHERE username = %s OR email = %s",
                (identifier, identifier)
            )
            user = cursor.fetchone()
            if not user or not verify_password(password, user['password_hash']):
                return False, "⚠️ بيانات الدخول غير صحيحة"
            token = generate_jwt(user['id'], user['username'])
            st.session_state.authenticated = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['username']
            st.session_state.user_email = user['email']
            st.session_state.jwt_token = token
            st.session_state.points = user.get('points', 0)
            st.session_state.level = user.get('level', 1)
            st.session_state.credits = user.get('credits', 5)
            return True, "✅ تم تسجيل الدخول بنجاح!"
    except Exception as e:
        return False, f"❌ خطأ: {e}"
    finally:
        conn.close()

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_email = None
    st.session_state.jwt_token = None

# ====================================================================
# 5. واجهة تسجيل الدخول
# ====================================================================
def render_login_page():
    st.set_page_config(page_title="PHOENIX ULTIMATE – دخول", page_icon="🚀", layout="centered")
    st.markdown("""
    <style>
        .auth-title { text-align: center; font-size: 2.5rem; font-weight: 800; color: #1E3A8A; }
        .auth-title span { color: #F5A623; }
        .auth-subtitle { text-align: center; color: #666; margin-bottom: 2rem; }
        .stButton button { width: 100%; background-color: #1E3A8A; color: white; border-radius: 8px; height: 3rem; transition: 0.3s; }
        .stButton button:hover { background-color: #1D4ED8; transform: scale(1.02); }
        .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
        .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; }
        .stTabs [aria-selected="true"] { color: #1E3A8A; border-bottom: 3px solid #F5A623; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🚀 PHOENIX <span>ULTIMATE</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">منصة أمنية ذكية لإدارة الخطط الهندسية</p>')
    tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"])
    with tab1:
        with st.form("login_form"):
            identifier = st.text_input("👤 اسم المستخدم أو البريد الإلكتروني")
            password = st.text_input("🔒 كلمة المرور", type="password")
            if st.form_submit_button("🚀 تسجيل الدخول", use_container_width=True):
                success, msg = login_user(identifier, password)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("👤 اسم المستخدم")
            new_email = st.text_input("✉️ البريد الإلكتروني")
            new_pass = st.text_input("🔒 كلمة المرور", type="password")
            confirm_pass = st.text_input("🔒 تأكيد كلمة المرور", type="password")
            if st.form_submit_button("📝 إنشاء حساب", use_container_width=True):
                if new_pass != confirm_pass:
                    st.error("⚠️ كلمة المرور غير متطابقة")
                else:
                    success, msg = create_user(new_user, new_email, new_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

# ====================================================================
# 6. دوال مساعدة: التصدير، التحليلات، الإشعارات
# ====================================================================
def send_telegram_alert(bot_token: str, chat_id: str, plan: dict) -> bool:
    if not bot_token or not chat_id:
        return False
    try:
        msg = f"🚀 *مشروع جديد PHOENIX ULTIMATE*\n\n👤 *العميل:* {plan.get('client_name', 'غير معروف')}\n💰 *الميزانية:* {plan.get('estimated_budget_range', '')}\n📋 *المهام:* {len(plan.get('generated_tasks', []))}\n🔑 *التوقيع:* {plan.get('digital_signature', 'N/A')}"
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=5)
        return True
    except: return False

def send_email_alert(recipient: str, plan: dict) -> bool:
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SENDER_EMAIL", "")
    if not smtp_user or not smtp_pass or not sender:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = f"✅ خطة مشروعك جاهزة - {plan.get('client_name', '')}"
        body = f"الملخص: {plan.get('project_summary', '')}\nالميزانية: {plan.get('estimated_budget_range', '')}\nالتوقيع: {plan.get('digital_signature', 'N/A')}"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", 587)))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

def generate_pdf(plan_json):
    if not REPORTLAB_AVAILABLE:
        return b""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("🧠 خطة مشروع - PHOENIX ULTIMATE", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"<b>العميل:</b> {plan_json.get('client_name', 'غير محدد')}", styles['Normal']))
    elements.append(Paragraph(f"<b>الميزانية:</b> {plan_json.get('estimated_budget_range', 'غير محددة')}", styles['Normal']))
    elements.append(Paragraph(f"<b>التوقيع:</b> {plan_json.get('digital_signature', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("<b>📌 الملخص:</b>", styles['Heading2']))
    elements.append(Paragraph(plan_json.get('project_summary', 'لا يوجد ملخص'), styles['Normal']))
    tasks = plan_json.get('generated_tasks', [])
    if tasks:
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<b>📋 المهام:</b>", styles['Heading2']))
        for idx, task in enumerate(tasks, 1):
            elements.append(Paragraph(f"{idx}. {task.get('title')} ({task.get('priority')}) - {task.get('estimated_days')} أيام", styles['Normal']))
            elements.append(Paragraph(f"   {task.get('description')}", styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
    doc.build(elements)
    return buffer.getvalue()

def generate_excel(plan_json):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        summary = pd.DataFrame({
            'البيان': ['اسم العميل', 'الملخص', 'الميزانية', 'التوقيع'],
            'القيمة': [plan_json.get('client_name',''), plan_json.get('project_summary',''), plan_json.get('estimated_budget_range',''), plan_json.get('digital_signature','')]
        })
        summary.to_excel(writer, sheet_name='ملخص', index=False)
        tasks = plan_json.get('generated_tasks', [])
        if tasks:
            pd.DataFrame(tasks).to_excel(writer, sheet_name='المهام', index=False)
    return output.getvalue()

def generate_image(plan_json):
    if not PIL_AVAILABLE:
        return b""
    img = Image.new('RGB', (900, 650), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    y = 20
    draw.text((20, y), "PHOENIX ULTIMATE - خطة مشروع", font=font, fill='black')
    y += 40
    draw.text((20, y), f"العميل: {plan_json.get('client_name','')}", font=font, fill='black')
    y += 30
    draw.text((20, y), f"الميزانية: {plan_json.get('estimated_budget_range','')}", font=font, fill='black')
    y += 30
    draw.text((20, y), f"التوقيع: {plan_json.get('digital_signature','N/A')}", font=font, fill='gray')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def generate_html(plan_json):
    html = f"""
    <html><body><h1>PHOENIX ULTIMATE - خطة مشروع</h1>
    <p><b>العميل:</b> {plan_json.get('client_name','')}</p>
    <p><b>الميزانية:</b> {plan_json.get('estimated_budget_range','')}</p>
    <p><b>التوقيع:</b> {plan_json.get('digital_signature','N/A')}</p>
    <p><b>الملخص:</b> {plan_json.get('project_summary','')}</p>
    <h2>المهام</h2><ul>
    """
    for t in plan_json.get('generated_tasks', []):
        html += f"<li>{t.get('title')} ({t.get('priority')}) - {t.get('estimated_days')} أيام: {t.get('description')}</li>"
    html += "</ul></body></html>"
    return html.encode('utf-8')

# ====================================================================
# 7. محرك التحليل المتقدم
# ====================================================================
def calculate_project_metrics(project_data: dict) -> dict:
    tasks = project_data.get('generated_tasks', [])
    total_days = sum(t.get('estimated_days', 0) for t in tasks)
    total_tasks = len(tasks)
    high = sum(1 for t in tasks if t.get('priority') == 'High')
    med = sum(1 for t in tasks if t.get('priority') == 'Medium')
    low = sum(1 for t in tasks if t.get('priority') == 'Low')
    base_cost = total_days * 150
    overhead = base_cost * 0.2
    total_cost = base_cost + overhead
    risk = min(100, int((high / max(total_tasks, 1)) * 100))
    confidence = min(100, int((total_tasks / 10) * 100))
    return {
        'total_days': total_days,
        'total_tasks': total_tasks,
        'high': high, 'med': med, 'low': low,
        'total_cost': total_cost,
        'risk_score': risk,
        'confidence_score': confidence
    }

def render_advanced_analytics(plan_json: dict, prefix: str = "main"):
    m = calculate_project_metrics(plan_json)
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
        st.plotly_chart(fig, use_container_width=True, key=f"{prefix}_pie")
    with col2:
        if plan_json.get('generated_tasks'):
            df = pd.DataFrame(plan_json['generated_tasks'])
            fig = px.bar(df, x='title', y='estimated_days', color='priority', title="أيام العمل لكل مهمة")
            st.plotly_chart(fig, use_container_width=True, key=f"{prefix}_bar")
    st.markdown("### 📋 جدول التحليل")
    df_analytics = pd.DataFrame({
        'المقياس': ['إجمالي الأيام', 'عدد المهام', 'عالية الأولوية', 'متوسطة الأولوية', 'منخفضة الأولوية', 'التكلفة الإجمالية', 'درجة المخاطرة', 'درجة الثقة'],
        'القيمة': [m['total_days'], m['total_tasks'], m['high'], m['med'], m['low'], f"${m['total_cost']:,.0f}", f"{m['risk_score']}%", f"{m['confidence_score']}%"]
    })
    st.dataframe(df_analytics, use_container_width=True, hide_index=True)
    recs = []
    if m['risk_score'] > 70: recs.append("⚠️ مخاطرة عالية: قسّم المهام الكبيرة.")
    if m['confidence_score'] < 50: recs.append("📝 تفاصيل غير كافية: أضف تفاصيل أكثر.")
    if not recs: recs.append("✅ خطة متوازنة: استمر في التنفيذ.")
    for rec in recs: st.info(rec)

# ====================================================================
# 8. دوال HITL والتوليد
# ====================================================================
def display_tasks_with_hitl(tasks: list) -> list:
    modified = []
    st.markdown("### ✏️ مراجعة وتعديل المهام يدوياً (HITL)")
    for idx, task in enumerate(tasks, 1):
        with st.container(border=True):
            col1, col2 = st.columns([2,1])
            with col1:
                title = st.text_input(f"العنوان {idx}", value=task.get('title',''), key=f"hitl_title_{idx}")
                desc = st.text_area(f"الوصف {idx}", value=task.get('description',''), key=f"hitl_desc_{idx}", height=60)
            with col2:
                days = st.number_input(f"المدة (أيام) {idx}", min_value=1, value=task.get('estimated_days',2), key=f"hitl_days_{idx}")
                priority = st.selectbox(f"الأولوية {idx}", ['High','Medium','Low'], index=['High','Medium','Low'].index(task.get('priority','Medium')), key=f"hitl_prio_{idx}")
            modified.append({'title': title, 'description': desc, 'estimated_days': days, 'priority': priority})
    if st.button("✅ اعتماد الخطة المعدلة", use_container_width=True):
        return modified
    return tasks

def generate_project_plan_safe(api_key: str, interview_data: dict) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    similar = get_similar_projects(interview_data["idea"], top_k=3)
    context = ""
    if similar:
        context = "\n\n**📚 مشاريع مشابهة:**\n"
        for p in similar:
            context += f"- {p.get('summary','')[:150]}...\n"
    prompt = f"""
    أنت خبير منتجات تقني. العميل يريد مشروعاً برمجياً.
    البيانات:
    - الاسم: {interview_data["name"]}
    - الفكرة: {interview_data["idea"]}
    - الميزانية: {interview_data["budget"]}
    - الجدول: {interview_data["timeline"]}
    - التقنيات: {interview_data["tech_pref"]}
    {context}
    أخرج خطة عمل بصيغة JSON فقط:
    {{
      "client_name": "...",
      "project_summary": "...",
      "suggested_tech_stack": ["..."],
      "estimated_budget_range": "...",
      "estimated_time_weeks": "...",
      "generated_tasks": [
        {{"title": "...", "description": "...", "estimated_days": 2, "priority": "High"}}
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        try:
            data = json.loads(raw)
        except:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match: data = json.loads(match.group())
            else: raise ValueError("تعذر استخراج JSON")
        data["digital_signature"] = generate_digital_signature(data.get("project_summary",""))
        return data
    except Exception as e:
        raise ValueError(f"فشل التوليد: {e}")

# ====================================================================
# 9. الشريط الجانبي والدوال الأساسية
# ====================================================================
def get_active_gemini_key():
    return os.getenv("GEMINI_API_KEY") or st.session_state.get("user_gemini_key", "")

def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ مركز الذكاء الاصطناعي")
        key = get_active_gemini_key()
        if key:
            st.success("🟢 Gemini: نشط")
        else:
            st.warning("⚡ وضع العرض")
            k = st.text_input("🔑 مفتاح Gemini", type="password")
            if k: st.session_state["user_gemini_key"] = k; st.rerun()
        st.divider()
        st.markdown("#### 📡 حالة النظام")
        db_status = "🟢 متصلة" if get_db_connection() else "🔴 غير متصلة"
        st.caption(f"• قاعدة البيانات: **{db_status}**")
        st.caption(f"• البصمة: `{generate_fingerprint()[:16]}`")
        st.caption(f"• النقاط: **{st.session_state.get('points', 0)}**")
        st.caption(f"• المستوى: **{st.session_state.get('level', 1)}**")
        st.caption(f"• الرصيد: **{st.session_state.get('credits', 5)}**")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            logout_user(); st.rerun()

# ====================================================================
# 10. الواجهة الرئيسية
# ====================================================================
st.set_page_config(page_title="PHOENIX ULTIMATE", page_icon="🚀", layout="wide")

def main():
    init_database()
    init_auth()
    if not st.session_state.authenticated:
        render_login_page()
        return
    render_sidebar()

    st.markdown("""
    <div style="text-align:center; padding:1rem 0;">
        <h1 style="color:#1E3A8A; font-size:2.8rem;">🚀 PHOENIX <span style="color:#F5A623;">ULTIMATE</span></h1>
        <p style="color:#4B5563;">النسخة الفائزة – مستحيلة التقليد</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 **توفر عليك 40 ساعة عمل و 500$ من استشارة مدير مشروع**", icon="🔥")
    st.divider()

    tab1, tab2 = st.tabs(["🚀 إنشاء خطة جديدة", "📊 لوحة تحكم مشاريعك"])
    with tab2:
        projects = get_user_projects(st.session_state.user_id)
        if projects:
            df = pd.DataFrame(projects)
            st.dataframe(df, use_container_width=True, hide_index=True)
            # تحليل مشروع محدد
            opts = [f"{p['id']} - {p['client_name']}" for p in projects]
            sel = st.selectbox("اختر مشروعاً لتحليله", opts)
            if sel:
                pid = int(sel.split(' - ')[0])
                conn = get_db_connection()
                if conn:
                    with conn.cursor() as c:
                        c.execute("SELECT * FROM projects WHERE id=%s", (pid,))
                        proj = c.fetchone()
                        c.execute("SELECT * FROM tasks WHERE project_id=%s", (pid,))
                        tasks = c.fetchall()
                    conn.close()
                    if proj:
                        full = {
                            'client_name': proj['client_name'],
                            'project_summary': proj['summary'],
                            'estimated_budget_range': proj['budget_range'],
                            'suggested_tech_stack': json.loads(proj['tech_stack']) if proj['tech_stack'] else [],
                            'generated_tasks': tasks,
                            'digital_signature': proj['digital_signature']
                        }
                        render_advanced_analytics(full, prefix="dash")
        else:
            st.info("💡 لا توجد مشاريع حالياً.")

    with tab1:
        with st.form("plan_form"):
            c1,c2 = st.columns(2)
            with c1:
                client = st.text_input("🏢 اسم العميل / الشركة", value="مؤسسة أفق التعليمية")
                budget = st.text_input("💰 الميزانية المتوقعة", value="8000 - 12000")
            with c2:
                timeline = st.text_input("⏱️ الجدول الزمني", value="8 أسابيع")
                tech = st.text_input("🛠️ التقنيات المفضلة", value="Flutter, Node.js, Supabase, Gemini AI")
            idea = st.text_area("💡 فكرة المشروع بالتفصيل", height=120, value="منصة تعليمية تفاعلية للطلاب في اليمن تدعم الفصول المباشرة والاختبارات الآلية")
            submitted = st.form_submit_button("🚀 توليد الخطة الهندسية الآن", use_container_width=True)
        if submitted:
            key = get_active_gemini_key()
            if not key:
                st.error("❌ مفتاح Gemini مفقود. أدخله في الشريط الجانبي.")
                st.stop()
            if st.session_state.get('credits', 0) <= 0:
                st.error("❌ انتهت رصيدك المجاني. اشترك للمتابعة.")
                st.stop()
            data = {"name": client, "idea": idea, "budget": budget, "timeline": timeline, "tech_pref": tech}
            with st.spinner("🔄 جارٍ التوليد..."):
                try:
                    plan = generate_project_plan_safe(key, data)
                    # خصم رصيد
                    st.session_state.credits = st.session_state.get('credits', 5) - 1
                    # حفظ في قاعدة البيانات
                    save_project_plan(plan, st.session_state.user_id)
                    # تحديث النقاط
                    st.session_state.points = st.session_state.get('points', 0) + 10
                    # إشعارات
                    bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN"))
                    chat_id = st.secrets.get("TELEGRAM_CHAT_ID", os.getenv("TELEGRAM_CHAT_ID"))
                    if bot_token and chat_id:
                        send_telegram_alert(bot_token, chat_id, plan)
                    if st.session_state.user_email:
                        send_email_alert(st.session_state.user_email, plan)
                    st.success("✅ تم توليد الخطة بنجاح!")
                    st.divider()
                    render_advanced_analytics(plan, prefix="main")
                    # ملخص
                    st.markdown("### 📌 ملخص المشروع")
                    st.info(plan.get('project_summary',''))
                    if plan.get('suggested_tech_stack'):
                        st.markdown("### 🛠️ التقنيات المقترحة")
                        st.write("، ".join(plan['suggested_tech_stack']))
                    # HITL
                    tasks = plan.get('generated_tasks', [])
                    if tasks:
                        new_tasks = display_tasks_with_hitl(tasks)
                        if new_tasks != tasks:
                            plan['generated_tasks'] = new_tasks
                            st.success("✅ تم اعتماد الخطة المعدلة!")
                    # عرض المهام النهائية
                    if plan.get('generated_tasks'):
                        st.markdown("### 📋 المهام")
                        for idx, task in enumerate(plan['generated_tasks'], 1):
                            emoji = "🔴" if task.get('priority')=='High' else "🟡" if task.get('priority')=='Medium' else "🟢"
                            with st.container(border=True):
                                st.markdown(f"{emoji} **{idx}. {task.get('title')}**")
                                st.caption(f"📅 {task.get('estimated_days')} أيام | الأولوية: {task.get('priority')}")
                                st.write(task.get('description',''))
                    # تصدير
                    st.divider()
                    st.markdown("### 💾 تحميل الخطة")
                    col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
                    col_dl1.download_button("📥 JSON", json.dumps(plan, ensure_ascii=False, indent=2), "plan.json", use_container_width=True)
                    col_dl2.download_button("📄 PDF", generate_pdf(plan), "plan.pdf", use_container_width=True)
                    col_dl3.download_button("📊 Excel", generate_excel(plan), "plan.xlsx", use_container_width=True)
                    col_dl4.download_button("🖼️ صورة", generate_image(plan), "plan.png", use_container_width=True)
                    # مشاركة الرابط
                    st.markdown("### 🔗 مشاركة الخطة")
                    share_id = secrets.token_urlsafe(12)
                    expires_at = datetime.now() + timedelta(days=7)
                    # الحصول على آخر project_id (نستخدم 1 كتجربة أو نأخذ id حقيقي)
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as c:
                            c.execute("SELECT id FROM projects WHERE user_id=%s ORDER BY id DESC LIMIT 1", (st.session_state.user_id,))
                            row = c.fetchone()
                            if row:
                                save_shared_link(share_id, row['id'], expires_at)
                        conn.close()
                    share_url = f"{st.get_option('server.baseUrlPath')}?share_id={share_id}"
                    st.code(share_url, language="text")
                    st.caption("🔐 الرابط صالح لمدة 7 أيام.")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    main()
