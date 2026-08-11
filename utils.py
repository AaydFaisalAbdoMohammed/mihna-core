#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
UTILITIES MODULE: Security, Notifications, Exports, UI Helpers, Translations
===============================================================================
"""

import os
import re
import io
import json
import time
import uuid
import hmac
import hashlib
import urllib.parse
from urllib.parse import quote_plus
import datetime
import logging

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------- Optional Dependencies -----------------
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_PDF_AVAILABLE = True
except ImportError:
    ARABIC_PDF_AVAILABLE = False


# =====================================================================
# 1. ENVIRONMENT & CONFIG HELPERS
# =====================================================================
def get_env_or_secret(key: str, default_val: str = "") -> str:
    """الحصول على قيمة من متغير البيئة أو st.secrets."""
    if key in os.environ:
        return os.environ[key]
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default_val


# =====================================================================
# 2. SECURITY ENGINE
# =====================================================================
class SecurityEngine:
    HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_ENTERPRISE_ULTIMATE")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def hash_password(password: str) -> str:
        if BCRYPT_AVAILABLE:
            try:
                salt = bcrypt.gensalt(rounds=12)
                return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            except Exception as e:
                logging.error(f"Bcrypt hash error: {e}")
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        if not hashed or not password:
            return False
        if BCRYPT_AVAILABLE and hashed.startswith("$2"):
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except Exception:
                pass
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed

    @staticmethod
    def generate_signature(data_dict: dict) -> str:
        clean_payload = {k: v for k, v in data_dict.items() if k not in ["signature", "timestamp", "is_tampered"]}
        serialized = json.dumps(clean_payload, sort_keys=True, ensure_ascii=False)
        return hmac.new(SecurityEngine.HMAC_KEY.encode(), serialized.encode(), hashlib.sha512).hexdigest()

    @staticmethod
    def verify_signature(data_dict: dict, signature: str) -> bool:
        if not signature:
            return False
        expected_sig = SecurityEngine.generate_signature(data_dict)
        return hmac.compare_digest(expected_sig, signature)


# =====================================================================
# 3. NOTIFICATION ENGINE
# =====================================================================
class NotificationEngine:
    @staticmethod
    def create_whatsapp_link(phone: str, message: str) -> str:
        encoded_msg = urllib.parse.quote(message)
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"


# =====================================================================
# 4. EXPORT UTILITIES
# =====================================================================
def generate_qr_code_image(target_url: str) -> bytes:
    if QRCODE_AVAILABLE:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(target_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    return b""


def generate_excel_download(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    if OPENPYXL_AVAILABLE:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Project Tasks')
        return output.getvalue()
    else:
        return df.to_csv(index=False).encode('utf-8')


def generate_pdf_plan(plan: dict, signature: str, detailed_text: str) -> bytes:
    buffer = io.BytesIO()
    if not REPORTLAB_AVAILABLE:
        buffer.write(detailed_text.encode('utf-8'))
        return buffer.getvalue()

    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    def prepare_text(text_val):
        if ARABIC_PDF_AVAILABLE:
            try:
                reshaped = arabic_reshaper.reshape(text_val)
                return get_display(reshaped)
            except Exception:
                return text_val
        return text_val

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, alignment=2)

    story.append(Paragraph(prepare_text(f"خطة مشروع: {plan['project_name']}"), title_style))
    story.append(Spacer(1, 15))

    info_text = f"المجال التقني: {plan['domain']} | الميزانية: ${plan['budget']} | المدة: {plan['target_days']} يوم"
    story.append(Paragraph(prepare_text(info_text), body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(prepare_text("--- تفاصيل الخطة التنفيذية والكوادر المخصصة ---"), title_style))
    for line in detailed_text.split("\n"):
        if line.strip():
            story.append(Paragraph(prepare_text(line.strip()), body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 15))
    story.append(Paragraph(prepare_text(f"التوقيع الرقمي HMAC-SHA512: {signature[:40]}..."), body_style))

    doc.build(story)
    return buffer.getvalue()


def build_detailed_plan_text(plan: dict) -> str:
    from ai import PhoenixAI  # استيراد داخلي لتجنب التعارض الدائري

    p_name = plan.get('project_name', 'المشروع')
    domain = plan.get('domain', 'تقني')
    budget = float(plan.get('budget', 0))
    days = int(plan.get('target_days', 0))
    tech = plan.get('tech', plan.get('tech_stack', 'Flutter, Node.js, Supabase, PostgreSQL'))
    risk = plan.get('risk', 'متوسط')
    tasks = plan.get('tasks', [])

    working_hours_per_day = 8
    total_man_hours = days * working_hours_per_day
    daily_rate = budget / max(1, days)
    hourly_rate = budget / max(1, total_man_hours)

    contingency_rate = 0.15 if risk in ["عالي", "High"] else (0.10 if risk in ["متوسط", "Medium"] else 0.05)
    contingency_amount = budget * contingency_rate
    effective_operational_budget = budget - contingency_amount

    cloud_infra_cost = budget * 0.10
    dev_labor_cost = effective_operational_budget - cloud_infra_cost

    specialists = PhoenixAI.calculate_specialists_breakdown(budget, days, domain)
    specialists_str = ""
    for s in specialists:
        specialists_str += f"""
* {s['icon']} **{s['role']}**
  * ⏱️ **إجمالي الساعات:** {s['total_hours']} ساعة ({s['allocated_days']} أيام عمل)
  * 💵 **أجر الساعة الهندسية:** ${s['hourly_rate']:,.2f} / ساعة | **اليومي:** ${s['daily_rate']:,.2f} / يوم
  * 💰 **إجمالي المستحقات:** `${s['total_cost']:,.2f}` ({s['ratio_pct']}% من ميزانية الكوادر)
"""

    tasks_breakdown_str = ""
    for idx, t in enumerate(tasks, 1):
        t_cost = float(t.get('cost', 0))
        t_days = int(t.get('days', 0))
        t_hours = t_days * working_hours_per_day
        cost_percentage = (t_cost / max(1, budget)) * 100
        daily_t_cost = t_cost / max(1, t_days)
        hourly_t_cost = t_cost / max(1, t_hours)

        tasks_breakdown_str += f"""
#### Phase {idx}: {t.get('task', 'مهمة')}
* ⏱️ **المدة الزمنية:** {t_days} أيام عمل ({t_hours} ساعة هندسية)
* 💰 **التكلفة المخصصة:** ${t_cost:,.2f} ({cost_percentage:.1f}% من إجمالي الميزانية)
* 📊 **المعدل اليومي للإنفاق:** ${daily_t_cost:,.2f} / يوم | **الساعة:** ${hourly_t_cost:,.2f} / ساعة
* 📌 **الحالة التنفيذية:** {t.get('status', 'مخطط')}
"""

    return f"""📌 **المستند التنفيذي والهندسي المتكامل لمشروع ({p_name})**
*تاريخ التوليد والتوقيع الرقمي: {plan.get('generated_at', datetime.datetime.now().strftime('%Y-%m-%d'))}*

---

### 1. نظرة عامة والأهداف التنفيذية (Executive Summary & KPIs)
يهدف مشروع **{p_name}** إلى تقديم حل سحابي برمجي فائق الأداء في قطاع **{domain}**، معتمداً على البيئة والتقنيات: **({tech})**.
* **الميزانية الكلية (Total Budget):** `${budget:,.2f}`
* **المدى الزمني المستهدف (Timeline):** `{days}` يوماً تقويمياً.
* **مستوى تحمل المخاطر (Risk Profile):** `{risk}`.

---

### 2. توزيع الكوادر والتخصصات الهندسية وأجورهم (Engineering Specialists & Payroll Allocation)
تم استخدام خوارزمية **Phoenix Resource Allocation Engine** لتحديد الكوادر الدقيقة المطلوبة وحساب أجورهم:
{specialists_str}

---

### 3. الحسابات المالية والهندسية التفصيلية (Precise Cost & Time Allocation)
* ⏳ **إجمالي الساعات الهندسية (Total Man-Hours):** `{total_man_hours:,}` ساعة عمل ({working_hours_per_day} ساعات/يوم).
* 💵 **معدل التكلفة اليومي الكلي:** `${daily_rate:,.2f}` / يوم.
* ⏱️ **معدل تكلفة الساعة الهندسية:** `${hourly_rate:,.2f}` / ساعة.
* 🛡️ **احتياطي الطوارئ والمخاطر ({contingency_rate*100:.0f}% Risk Reserve):** `${contingency_amount:,.2f}`.
* ☁️ **تكاليف البنية التحتية والاستضافة Cloud Infrastructure:** `${cloud_infra_cost:,.2f}`.
* 🛠️ **صافي ميزانية تطوير الكوادر (Effective Dev Budget):** `${dev_labor_cost:,.2f}`.

---

### 4. التفصيل المرحلي للمهام (Work Breakdown Structure)
{tasks_breakdown_str}

---

### 5. مصفوفة الأمان والتوقيع الرقمي المشفر (Digital HMAC Signature)
* **التوقيع الرقمي:** تم توقيع هذه الخطة رسمياً وحفظها في قاعدة بيانات Cloud SQL.
* **تشفير HMAC-SHA512:** المعيار السري المعتمد في المؤسسة.
"""


# =====================================================================
# 5. VISUALIZATION: HALF-DOUGHNUT GAUGE
# =====================================================================
def create_half_doughnut_gauge(val: float, title: str, color: str, prefix: str = "", suffix: str = "", max_val: float = 100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={'prefix': prefix, 'suffix': suffix, 'font': {'size': 26, 'color': color, 'family': 'Tajawal, sans-serif'}},
        title={'text': title, 'font': {'size': 14, 'color': '#94A3B8'}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "#64748B"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "rgba(226, 232, 240, 0.15)",
            'bordercolor': "rgba(255,255,255,0.1)",
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=15, r=15, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#F8FAFC")
    )
    return fig


# =====================================================================
# 6. TRANSLATIONS DICTIONARY (UI Labels)
# =====================================================================
T = {
    'ar': {
        'title': "🚀 وكيل مهنة PRO | PHOENIX Enterprise v13.6",
        'subtitle': "المنصة المتقدمة لهندسة خطط المشاريع، حساب أجور المتخصصين، وتأمين البيانات بـ Cloud SQL و HMAC-SHA512.",
        'lang_select': "🌐 لغة الواجهة (Language):",
        'theme_select': "🎨 مظهر التطبيق (Theme):",
        'dark': "🌙 الداكن (Dark)",
        'light': "☀️ الفاتح (Light)",
        'user': "👤 المستخدم:",
        'credits': "💳 الرصيد الحالي:",
        'points': "نقاط مجانية",
        'renew_title': "🛒 ترقية الاشتراك",
        'renew_btn': "⚡ اشترك الآن وترقية الحساب",
        'logout_btn': "🚪 تسجيل الخروج",
        'notify_settings': "📲 إعدادات الإشعارات الفورية",
        'wa_phone': "رقم الواتساب",
        'tg_handle': "معرف التليجرام",
        'tab1': "🏗️ بناء الخطة والكوادر",
        'tab2': "📊 التحليلات التفاعلية 6D",
        'tab3': "✏️ محرر المهام والتقرير النصي",
        'tab4': "🔄 التغذية الراجعة والتكيّف السعري",
        'tab5': "💳 الحساب والاشتراكات",
        'tab6': "🗄️ أرشفة Cloud SQL (7-Tables Schema)",
        'tab_admin': "👑 لوحة الإدارة العليا (CEO Panel)",
        'quick_templates': "⚡ قوالب جاهزة للبدء السريع",
        'ecom': "🛒 متجر إلكتروني",
        'edu': "🎓 منصة تعليمية",
        'delivery': "🚗 تطبيق توصيل",
        'p_name': "اسم المشروع",
        'tech_domain': "المجال التقني",
        'budget': "الميزانية التقديرية ($)",
        'tech_stack': "التقنيات المستخدمة",
        'target_days': "المدة الزمنية المستهدفة (يوم)",
        'risk_level': "تحمل المخاطر",
        'scope': "نطاق العمل (Scope of Work)",
        'generate_btn': "🚀 توليد وحساب الكوادر والتوقيع الرقمي (1 نقطة)",
        'export_excel': "📥 تحميل جدول المهام (Excel)",
        'export_pdf': "📄 تحميل الخطة التنفيذية (PDF)",
        'detailed_plan': "📜 الخطة التنفيذية النصية الشاملة والمعمقة",
        'save_re_sign': "💾 حفظ التعديلات وإعادة التوقيع الرقمي",
        'digital_sig': "🔑 التوقيع الرقمي المشفر (HMAC-SHA512):",
        'sig_valid': "✔ توقيع موثوق وسليم",
        'sig_invalid': "❌ تم التلاعب بالبيانات",
        'send_wa': "📱 إرسال عبر WhatsApp",
        'send_tg': "📲 إشعار Telegram Bot",
        'spec_title': "👥 الكوادر والمتخصصون المطلوبون وأجورهم المخصصة (Specialist Payroll & Hours)",
        'tasks_title': "📋 مراحل ونطاق المهام الفنية",
        'login_welcome': "مرحباً بك مجدداً!",
        'signup_welcome': "انضم إلى منصة PHOENIX Enterprise",
        'login_btn': "🚀 تسجيل الدخول",
        'signup_btn': "✨ إنشاء حساب وتفعيل 5 نقاط هدية",
        'email_label': "البريد الإلكتروني",
        'pass_label': "كلمة المرور",
        'confirm_pass_label': "تأكيد كلمة المرور",
        'fullname_label': "الاسم الكامل",
        'qr_scan_title': "📲 امسح الـ QR للتسجيل السريع",
        'qr_scan_caption': "للحملات الإعلانية والجوال: امسح الرمز للتوجيه الفوري وإنشاء حساب جديد",
        'pricing_adapted_title': "🔄 نظام التغذية الراجعة المغلقة والتكيّف السعري (AI Closed-Loop Feedback)",
        'pricing_adapted_caption': "نظام ذكي يربط آراء العملاء فورياً بضبط الخيارات السعرية والميزات داخل الكود لضمان أعلى ملاءمة للسوق.",
        'share_feedback_title': "📝 شاركنا رأيك (واربح 1 نقطة مجانية أوتوماتيكياً)",
        'star_rating_label': "تقييمك الكلي للمنصة (حدد عدد النجوم):",
        'market_proof_title': "🏆 لوحة إثبات احتياج السوق وقوة التكيف",
        'live_feedback_stream': "💬 سجل آراء جميع العملاء الحية (Live Stream):",
        'account_info_title': "👤 بيانات الحساب",
        'upgrade_plans_title': "🛒 خطط الترقية المتاحة (التسيعر الديناميكي المكيّف)",
        'payment_logs_title': "📩 سجل إشعارات الدفع والعمليات الذكية",
        'cloudsql_title': "🗄️ الأرشيف والتكامل مع Cloud SQL (7-Tables Schema)",
        'cloudsql_caption': "عرض أحدث المشاريع المسجلة في هيكل الجداول الكامل من الصور السبع.",
        'ceo_title': "👑 لوحة قيادة الإدارة العليا والمالك (CEO Control Center)",
        'ceo_caption': "مرحباً بك! هذه الصفحة مخفية عن جميع المستخدمين العاديين وتظهر فقط للمالك والمشرفين المعتمدين.",
        'grant_admin_title': "🔑 تعيين وإضافة مشرف جديد (Grant Supervisor Admin Privilege)",
        'grant_admin_btn': "✨ تفعيل صلاحية المشرف",
        'users_log_title': "📋 سجل جميع المستخدمين واشتراكاتهم الحية",
        'demands_title': "💬 طلبات ورغبات المستخدمين من جدول التغذية الراجعة (User Demands & Needs)"
    },
    'en': {
        'title': "🚀 Wakeel Mehna PRO | PHOENIX Enterprise v13.6",
        'subtitle': "Advanced Engineering Project Plan Builder & Specialist Payroll Engine Secured with Cloud SQL & HMAC-SHA512.",
        'lang_select': "🌐 Interface Language:",
        'theme_select': "🎨 Application Theme:",
        'dark': "🌙 Dark",
        'light': "☀️ Light",
        'user': "👤 User:",
        'credits': "💳 Balance:",
        'points': "points",
        'renew_title': "🛒 Upgrade Plan",
        'renew_btn': "⚡ Upgrade & Subscribe Now",
        'logout_btn': "🚪 Log Out",
        'notify_settings': "📲 Instant Notifications",
        'wa_phone': "WhatsApp Phone",
        'tg_handle': "Telegram Handle",
        'tab1': "🏗️ Build Plan & Payroll",
        'tab2': "📊 Advanced 6D Analytics",
        'tab3': "✏️ Task Editor & Text Plan",
        'tab4': "🔄 Feedback & Pricing",
        'tab5': "💳 Account & Subscriptions",
        'tab6': "🗄️ Cloud SQL 7-Tables Archive",
        'tab_admin': "👑 CEO & Admin Panel",
        'quick_templates': "⚡ Quick Start Templates",
        'ecom': "🛒 E-Commerce App",
        'edu': "🎓 E-Learning Platform",
        'delivery': "🚗 Delivery App",
        'p_name': "Project Name",
        'tech_domain': "Technical Domain",
        'budget': "Estimated Budget ($)",
        'tech_stack': "Tech Stack",
        'target_days': "Target Timeline (Days)",
        'risk_level': "Risk Tolerance",
        'scope': "Scope of Work",
        'generate_btn': "🚀 Generate Plan, Payroll & Sign (1 Credit)",
        'export_excel': "📥 Download Tasks (Excel)",
        'export_pdf': "📄 Download Plan (PDF)",
        'detailed_plan': "📜 Extended Text Plan",
        'save_re_sign': "💾 Save Edits & Re-Sign Digitally",
        'digital_sig': "🔑 Encrypted HMAC Signature:",
        'sig_valid': "✔ Valid Signature",
        'sig_invalid': "❌ Invalid Signature",
        'send_wa': "📱 Send via WhatsApp",
        'send_tg': "📲 Notify Telegram Bot",
        'spec_title': "👥 Specialist Payroll & Hourly Rate Breakdown",
        'tasks_title': "📋 Technical Task Phases & Scope",
        'login_welcome': "Welcome Back!",
        'signup_welcome': "Join PHOENIX Enterprise",
        'login_btn': "🚀 Sign In",
        'signup_btn': "✨ Create Account & Get 5 Bonus Points",
        'email_label': "Email Address",
        'pass_label': "Password",
        'confirm_pass_label': "Confirm Password",
        'fullname_label': "Full Name",
        'qr_scan_title': "📲 Scan QR Code for Fast Registration",
        'qr_scan_caption': "For Ads & Mobile: Scan code for instant redirect and account creation",
        'pricing_adapted_title': "🔄 AI Closed-Loop Feedback & Dynamic Pricing Engine",
        'pricing_adapted_caption': "Smart AI system adapting pricing & feature priorities directly from live market feedback.",
        'share_feedback_title': "📝 Share Your Feedback (Earn 1 Free Bonus Credit)",
        'star_rating_label': "Your Overall Rating (Select Stars):",
        'market_proof_title': "🏆 Market Validation & Adaptation Panel",
        'live_feedback_stream': "💬 Live Stream User Feedback:",
        'account_info_title': "👤 Account Details",
        'upgrade_plans_title': "🛒 Available Upgrade Plans (Dynamic Pricing)",
        'payment_logs_title': "📩 Payment & AI Execution Log",
        'cloudsql_title': "🗄️ Cloud SQL Archive (7-Tables Schema)",
        'cloudsql_caption': "Displaying latest projects stored across the complete 7-tables architecture.",
        'ceo_title': "👑 CEO & Owner Control Center",
        'ceo_caption': "Welcome! This panel is strictly hidden from regular users and visible only to system owner & supervisors.",
        'grant_admin_title': "🔑 Grant Supervisor Admin Privilege",
        'grant_admin_btn': "✨ Activate Supervisor Privileges",
        'users_log_title': "📋 Active Users & Subscriptions Log",
        'demands_title': "💬 User Demands & Market Feature Requests"
    }
}


# =====================================================================
# 7. SESSION MANAGEMENT & UI HELPERS
# =====================================================================
def init_session():
    if 'lang' not in st.session_state:
        st.session_state.lang = 'ar'
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = {
            'email': '',
            'username': 'زائر',
            'credits': 5,
            'role': 'Free Trial',
            'is_subscribed': False,
            'is_admin': False
        }
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'plan_signature' not in st.session_state:
        st.session_state.plan_signature = None
    if 'notify_whatsapp' not in st.session_state:
        st.session_state.notify_whatsapp = "+967700000000"
    if 'notify_telegram' not in st.session_state:
        st.session_state.notify_telegram = "@Ayad_Developer"
    if 'form_scope' not in st.session_state:
        st.session_state.form_scope = ""
    if 'form_pname' not in st.session_state:
        st.session_state.form_pname = "منصة تجارة سحابية Pro"
    if 'form_domain' not in st.session_state:
        st.session_state.form_domain = "التجارة الإلكترونية"
    if 'form_budget' not in st.session_state:
        st.session_state.form_budget = 3500
    if 'form_days' not in st.session_state:
        st.session_state.form_days = 30
    if 'payment_notifications' not in st.session_state:
        st.session_state.payment_notifications = []


def update_language():
    selected = st.session_state.lang_radio
    st.session_state.lang = 'ar' if ("العربية" in selected or "Arabic" in selected) else 'en'


def update_theme():
    selected = st.session_state.theme_radio
    st.session_state.theme = 'dark' if ("الداكن" in selected or "Dark" in selected) else 'light'


def apply_template(scope, domain, budget, days, pname):
    st.session_state.form_scope = scope
    st.session_state.form_domain = domain
    st.session_state.form_budget = budget
    st.session_state.form_days = days
    st.session_state.form_pname = pname


# =====================================================================
# 8. ULTRA-LUXURIOUS GLASSMORPHIC CSS INJECTION
# =====================================================================
def inject_custom_css():
    lang = st.session_state.lang
    theme = st.session_state.theme
    direction = "rtl" if lang == "ar" else "ltr"
    align_text = "right" if lang == "ar" else "left"

    if theme == "dark":
        bg_main = "#070A12"
        bg_sidebar = "#0F172A"
        text_color = "#F8FAFC"
        glass_bg = "rgba(15, 23, 42, 0.72)"
        glass_border = "rgba(255, 255, 255, 0.12)"
        glass_shadow = "0 20px 60px rgba(0, 0, 0, 0.55)"
        glass_focus_bg = "rgba(24, 34, 58, 0.92)"
        glass_focus_border = "rgba(99, 102, 241, 0.85)"
        glass_focus_shadow = "0 0 45px rgba(99, 102, 241, 0.45), inset 0 0 20px rgba(99, 102, 241, 0.15)"
        glow_colors = {
            "builder": "rgba(59,130,246,0.35)",
            "analytics": "rgba(16,185,129,0.35)",
            "editor": "rgba(139,92,246,0.35)",
            "feedback": "rgba(245,158,11,0.35)",
            "account": "rgba(236,72,153,0.35)",
            "cloudsql": "rgba(6,182,212,0.35)",
            "ceo": "rgba(217,119,6,0.40)"
        }
    else:
        bg_main = "#F8FAFC"
        bg_sidebar = "#FFFFFF"
        text_color = "#0F172A"
        glass_bg = "rgba(255, 255, 255, 0.78)"
        glass_border = "rgba(255, 255, 255, 0.80)"
        glass_shadow = "0 20px 60px rgba(31, 38, 135, 0.08)"
        glass_focus_bg = "rgba(255, 255, 255, 0.96)"
        glass_focus_border = "rgba(37, 99, 235, 0.85)"
        glass_focus_shadow = "0 0 45px rgba(37, 99, 235, 0.30), inset 0 0 20px rgba(37, 99, 235, 0.10)"
        glow_colors = {
            "builder": "rgba(59,130,246,0.25)",
            "analytics": "rgba(16,185,129,0.25)",
            "editor": "rgba(139,92,246,0.25)",
            "feedback": "rgba(245,158,11,0.25)",
            "account": "rgba(236,72,153,0.25)",
            "cloudsql": "rgba(6,182,212,0.25)",
            "ceo": "rgba(217,119,6,0.30)"
        }

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');
        * {{ font-family: 'Tajawal', sans-serif !important; }}

        .stApp {{
            background-color: {bg_main};
            background-image: 
                radial-gradient(at 10% 10%, rgba(99,102,241,0.08) 0px, transparent 50%),
                radial-gradient(at 90% 20%, rgba(16,185,129,0.06) 0px, transparent 50%),
                radial-gradient(at 50% 80%, rgba(139,92,246,0.07) 0px, transparent 50%);
            color: {text_color};
        }}

        /* --- Glass Cards --- */
        .glass-card {{
            background: {glass_bg};
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-radius: 32px;
            border: 1px solid {glass_border};
            box-shadow: {glass_shadow};
            padding: 28px;
            margin-bottom: 24px;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }}
        .glass-card::before {{
            content: '';
            position: absolute;
            top: -30%;
            right: -10%;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            z-index: 0;
            pointer-events: none;
        }}
        .glass-card::after {{
            content: '';
            position: absolute;
            bottom: -20%;
            left: -10%;
            width: 140px;
            height: 140px;
            border-radius: 50%;
            z-index: 0;
            pointer-events: none;
        }}
        .glass-card:hover, .glass-card:focus-within {{
            background: {glass_focus_bg};
            border-color: {glass_focus_border};
            box-shadow: {glass_focus_shadow};
            transform: translateY(-4px) scale(1.005);
        }}

        .glass-card-builder {{ border-left: 5px solid #3B82F6; }}
        .glass-card-builder::before {{ background: radial-gradient(circle, {glow_colors['builder']} 0%, transparent 70%); }}
        .glass-card-builder:hover {{ border-color: #3B82F6; box-shadow: 0 0 40px {glow_colors['builder']}; }}

        .glass-card-analytics {{ border-left: 5px solid #10B981; }}
        .glass-card-analytics::before {{ background: radial-gradient(circle, {glow_colors['analytics']} 0%, transparent 70%); }}
        .glass-card-analytics:hover {{ border-color: #10B981; box-shadow: 0 0 40px {glow_colors['analytics']}; }}

        .glass-card-editor {{ border-left: 5px solid #8B5CF6; }}
        .glass-card-editor::before {{ background: radial-gradient(circle, {glow_colors['editor']} 0%, transparent 70%); }}
        .glass-card-editor:hover {{ border-color: #8B5CF6; box-shadow: 0 0 40px {glow_colors['editor']}; }}

        .glass-card-feedback {{ border-left: 5px solid #F59E0B; }}
        .glass-card-feedback::before {{ background: radial-gradient(circle, {glow_colors['feedback']} 0%, transparent 70%); }}
        .glass-card-feedback:hover {{ border-color: #F59E0B; box-shadow: 0 0 40px {glow_colors['feedback']}; }}

        .glass-card-account {{ border-left: 5px solid #EC4899; }}
        .glass-card-account::before {{ background: radial-gradient(circle, {glow_colors['account']} 0%, transparent 70%); }}
        .glass-card-account:hover {{ border-color: #EC4899; box-shadow: 0 0 40px {glow_colors['account']}; }}

        .glass-card-cloudsql {{ border-left: 5px solid #06B6D4; }}
        .glass-card-cloudsql::before {{ background: radial-gradient(circle, {glow_colors['cloudsql']} 0%, transparent 70%); }}
        .glass-card-cloudsql:hover {{ border-color: #06B6D4; box-shadow: 0 0 40px {glow_colors['cloudsql']}; }}

        .glass-card-ceo {{ border-left: 5px solid #D97706; }}
        .glass-card-ceo::before {{ background: radial-gradient(circle, {glow_colors['ceo']} 0%, transparent 70%); }}
        .glass-card-ceo:hover {{ border-color: #D97706; box-shadow: 0 0 40px {glow_colors['ceo']}; }}

        [data-testid="stSidebarCollapseButton"] {{
            display: flex !important;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(10px);
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            border: 1px solid {glass_border} !important;
            color: #94A3B8 !important;
            transition: all 0.3s ease;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebarCollapseButton"]:hover {{
            background: rgba(255,255,255,0.15) !important;
            box-shadow: 0 0 25px {glow_colors['builder']};
            transform: scale(1.1);
        }}

        .badge-green {{ background-color: #10B981; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(16,185,129,0.3); }}
        .badge-purple {{ background-color: #8B5CF6; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(139,92,246,0.3); }}
        .badge-gold {{ background-color: #F59E0B; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(245,158,11,0.3); }}

        .checkout-btn {{
            display: block; width: 100%; text-align: center;
            background: linear-gradient(135deg, #2563EB, #1D4ED8);
            color: white !important; padding: 12px 16px; border-radius: 14px;
            font-weight: bold; text-decoration: none; border: none; font-size: 14px;
            box-shadow: 0 6px 20px rgba(37,99,235,0.35);
            transition: all 0.3s ease;
        }}
        .checkout-btn:hover {{ transform: scale(1.02); box-shadow: 0 8px 25px rgba(37,99,235,0.5); }}

        .checkout-btn-yearly {{
            display: block; width: 100%; text-align: center;
            background: linear-gradient(135deg, #D97706, #B45309);
            color: white !important; padding: 12px 16px; border-radius: 14px;
            font-weight: bold; text-decoration: none; border: none; font-size: 14px;
            box-shadow: 0 6px 20px rgba(217,119,6,0.35);
            transition: all 0.3s ease;
        }}
        .checkout-btn-yearly:hover {{ transform: scale(1.02); box-shadow: 0 8px 25px rgba(217,119,6,0.5); }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background: {glass_bg};
            padding: 10px;
            border-radius: 18px;
            border: 1px solid {glass_border};
            box-shadow: {glass_shadow};
            backdrop-filter: blur(12px);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255,255,255,0.08);
            color: #3B82F6;
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(59,130,246,0.2);
            border-bottom: 3px solid #3B82F6;
        }}
    </style>
    """, unsafe_allow_html=True)
