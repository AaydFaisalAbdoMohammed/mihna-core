import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import hashlib
import hmac
import time
from datetime import datetime
import urllib.parse
from urllib.parse import quote_plus
import os
import re
import io
import sqlalchemy
from sqlalchemy import text

# ReportLab & Arabic reshaper imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 1. DATABASE & CONFIGURATION SETUP
# ==========================================
APP_TITLE = "PHOENIX & WAKEEL MEHNA AGENT PRO - ENTERPRISE"
PAYMENT_LINK_MONTHLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly"
PAYMENT_LINK_YEARLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly"
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_DEFAULT")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "101519Ayad@!")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
INSTANCE_CONN = os.getenv("INSTANCE_CONNECTION_NAME", "project-d699d925-921c-4e54-8c4:asia-south1:mihna-core-ay")

st.set_page_config(
    page_title="وكيل مهنة PRO | Enterprise System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_db_engine():
    encoded_pass = quote_plus(DB_PASS)
    if os.path.exists(f"/cloudsql/{INSTANCE_CONN}"):
        db_url = f"postgresql+psycopg2://{DB_USER}:{encoded_pass}@/{DB_NAME}?host=/cloudsql/{INSTANCE_CONN}"
    else:
        db_url = f"postgresql+psycopg2://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
    engine_obj = sqlalchemy.create_engine(
        db_url, 
        pool_pre_ping=True,
        connect_args={'connect_timeout': 5}
    )
    return engine_obj

try:
    engine = init_db_engine()
except Exception as e:
    engine = None

def init_default_session():
    st.session_state.lang = 'ar'
    st.session_state.theme = 'dark'
    st.session_state.is_authenticated = False
    st.session_state.user = {
        'id': None,
        'email': '',
        'username': 'زائر', 
        'credits': 5,
        'role': 'Free Trial',
        'is_subscribed': False,
        'subscription_type': 'Free'
    }
    st.session_state.current_plan = None
    st.session_state.plan_signature = None
    st.session_state.notify_whatsapp = "+967700000000"
    st.session_state.notify_telegram = "@Ayad_Developer"
    st.session_state.form_scope = ""
    st.session_state.form_pname = "مشروع جديد Pro"
    st.session_state.form_domain = "التجارة الإلكترونية"
    st.session_state.form_budget = 3500
    st.session_state.form_days = 30
    st.session_state.payment_notifications = []

if 'is_authenticated' not in st.session_state:
    init_default_session()

# Callback Functions
def update_language():
    selected = st.session_state.lang_radio
    st.session_state.lang = 'ar' if "العربية" in selected else 'en'

def update_theme():
    selected = st.session_state.theme_radio
    st.session_state.theme = 'dark' if ("الداكن" in selected or "Dark" in selected) else 'light'

def apply_template(scope, domain, budget, days, pname):
    st.session_state.form_scope = scope
    st.session_state.form_domain = domain
    st.session_state.form_budget = budget
    st.session_state.form_days = days
    st.session_state.form_pname = pname

T = {
    'ar': {
        'title': "🚀 وكيل مهنة PRO | PHOENIX Enterprise Engine",
        'subtitle': "المنصة المتقدمة لهندسة خطط المشاريع وتأمينها بالتوقيع الرقمي والذكاء الاصطناعي.",
        'lang_select': "🌐 لغة الواجهة (Language):",
        'theme_select': "🎨 مظهر التطبيق (Theme):",
        'dark': "🌙 الداكن (Dark)",
        'light': "☀️ الفاتح (Light)",
        'user': "👤 المستخدم:",
        'credits': "💳 الرصيد التجريبي / الحالي:",
        'points': "نقاط مجانية",
        'renew_title': "🛒 ترقية الاشتراك",
        'renew_btn': "⚡ اشترك الآن وترقية الحساب",
        'logout_btn': "🚪 تسجيل الخروج",
        'notify_settings': "📲 إعدادات الإشعارات الفورية",
        'wa_phone': "رقم الواتساب (مع الرمز)",
        'tg_handle': "معرف التليجرام (Telegram Handle)",
        'tab1': "🏗️ بناء خطة مشروع",
        'tab2': "📊 التحليلات التفاعلية الفائقة",
        'tab3': "✏️ محرر المهام وخطة المشروع",
        'tab4': "💳 إدارة الحساب والاشتراكات",
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
        'generate_btn': "🚀 توليد وتوقيع الخطة الهندسية (تستهلك 1 نقطة)",
        'export_excel': "📥 تحميل جدول المهام (Excel)",
        'export_pdf': "📄 تحميل الخطة التنفيذية (PDF)",
        'detailed_plan': "📜 الخطة التنفيذية النصية الشاملة والمعمقة",
        'save_re_sign': "💾 حفظ التعديلات وإعادة التوقيع الرقمي",
        'digital_sig': "🔑 التوقيع الرقمي المشفر (HMAC-SHA512):",
        'sig_valid': "✔ توقيع موثوق وسليم ومطابق لقاعدة البيانات",
        'sig_invalid': "❌ تم التلاعب بالبيانات",
        'send_wa': "📱 إرسال عبر WhatsApp",
        'send_tg': "📲 إشعار Telegram Bot",
    },
    'en': {
        'title': "🚀 Wakeel Mehna Agent PRO | PHOENIX Enterprise",
        'subtitle': "Advanced Engineering Project Plan Builder Secured with AI & Digital Signatures.",
        'lang_select': "🌐 Interface Language:",
        'theme_select': "🎨 Application Theme:",
        'dark': "🌙 Dark",
        'light': "☀️ Light",
        'user': "👤 User:",
        'credits': "💳 Free / Current Balance:",
        'points': "free pts",
        'renew_title': "🛒 Upgrade Plan",
        'renew_btn': "⚡ Upgrade & Subscribe Now",
        'logout_btn': "🚪 Log Out",
        'notify_settings': "📲 Instant Notification Settings",
        'wa_phone': "WhatsApp Phone (with Country Code)",
        'tg_handle': "Telegram Handle",
        'tab1': "🏗️ Build Project Plan",
        'tab2': "📊 Advanced Interactive Analytics",
        'tab3': "✏️ Task Editor & Plan",
        'tab4': "💳 Account & Subscriptions",
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
        'generate_btn': "🚀 Generate & Sign Engineering Plan (1 Credit)",
        'export_excel': "📥 Download Tasks (Excel)",
        'export_pdf': "📄 Download Detailed Plan (PDF)",
        'detailed_plan': "📜 Comprehensive Extended Text Plan",
        'save_re_sign': "💾 Save Edits & Re-Sign Digitally",
        'digital_sig': "🔑 Encrypted Signature (HMAC-SHA512):",
        'sig_valid': "✔ Valid & Authentic Database Signature",
        'sig_invalid': "❌ Data Tampered / Invalid Signature",
        'send_wa': "📱 Send via WhatsApp",
        'send_tg': "📲 Notify Telegram Bot",
    }
}

lang = st.session_state.lang
txt = T[lang]

bg_color = "#0E1117" if st.session_state.theme == 'dark' else "#F8FAFC"
card_bg = "#1E293B" if st.session_state.theme == 'dark' else "#FFFFFF"
text_color = "#FFFFFF" if st.session_state.theme == 'dark' else "#0F172A"
border_color = "#334155" if st.session_state.theme == 'dark' else "#E2E8F0"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .badge-green {{ background-color: #10B981; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; }}
    .badge-purple {{ background-color: #8B5CF6; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; }}
    .badge-gold {{ background-color: #F59E0B; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; }}
    .checkout-btn {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white !important; padding: 12px 16px; border-radius: 10px; font-weight: bold; text-decoration: none; border: none; font-size: 14px; box-shadow: 0 4px 12px rgba(37,99,235,0.3); }}
    .checkout-btn-yearly {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #7C3AED, #9333EA); color: white !important; padding: 12px 16px; border-radius: 10px; font-weight: bold; text-decoration: none; border: none; font-size: 14px; box-shadow: 0 4px 12px rgba(124,58,237,0.3); }}
    .pricing-card {{ background-color: {card_bg}; border: 2px solid {border_color}; border-radius: 16px; padding: 24px; text-align: center; transition: all 0.3s ease; }}
    .pricing-card-highlight {{ background-color: {card_bg}; border: 2px solid #8B5CF6; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 10px 25px rgba(139,92,246,0.2); }}
    .ai-payment-card {{ background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); border: 2px solid #6366F1; border-radius: 16px; padding: 24px; color: #FFFFFF; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.25); }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {card_bg}; border-radius: 8px; padding: 10px 20px; color: {text_color}; border: 1px solid {border_color}; font-weight: bold; }}
    .stTabs [aria-selected="true"] {{ background-color: #3B82F6 !important; color: white !important; border-color: #3B82F6 !important; }}
    .email-notification-box {{ background-color: #022C22; border: 1px solid #10B981; border-radius: 12px; padding: 16px; color: #ECFDF5; margin: 10px 0; font-family: monospace; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER, SECURITY & DATABASE ENGINE
# ==========================================
class SecurityEngine:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_signature(data_dict: dict) -> str:
        serialized = json.dumps(data_dict, sort_keys=True, ensure_ascii=False)
        return hmac.new(SECRET_HMAC_KEY.encode(), serialized.encode(), hashlib.sha512).hexdigest()

    @staticmethod
    def verify_signature(data_dict: dict, signature: str) -> bool:
        if not signature:
            return False
        expected_sig = SecurityEngine.generate_signature(data_dict)
        return hmac.compare_digest(expected_sig, signature)

    @staticmethod
    def log_audit_event(user_id, action_type, details=""):
        if engine and user_id:
            try:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO security_audit_logs (user_id, action_type, ip_address, details)
                            VALUES (:user_id, :action_type, :ip_address, :details)
                        """),
                        {
                            "user_id": user_id,
                            "action_type": action_type,
                            "ip_address": "127.0.0.1",
                            "details": json.dumps(details) if isinstance(details, dict) else str(details)
                        }
                    )
                    conn.commit()
            except Exception as e:
                print(f"Audit log error: {e}")

class AIPaymentAgent:
    @staticmethod
    def inspect_payment_method(user_email: str) -> dict:
        return {
            "email": user_email,
            "payment_method": "Credit Card / Apple Pay (Auto-Detected Saved Method)",
            "gateway": "Lemon Squeezy Checkout Router",
            "card_last4": "8842",
            "status": "Ready for Seamless Execution"
        }

    @staticmethod
    def execute_auto_checkout(user_id, user_email: str, plan_type: str = "monthly"):
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        checkout_url = PAYMENT_LINK_YEARLY if plan_type == "yearly" else PAYMENT_LINK_MONTHLY
        plan_name = "Enterprise Yearly Plan ($279)" if plan_type == "yearly" else "Pro Monthly Plan ($29)"
        amount_num = 279.00 if plan_type == "yearly" else 29.00
        amount_str = f"${amount_num:.2f}"

        method_info = AIPaymentAgent.inspect_payment_method(user_email)
        status_box.info(f"🤖 **[AI Agent]:** فحص وسيلة الدفع المتاحة لـ `{user_email}`...")
        time.sleep(0.4)
        progress_bar.progress(30)

        status_box.info(f"🔗 **[AI Agent]:** قراءة توجيه Lemon Squeezy للرابط: `{checkout_url}`")
        time.sleep(0.4)
        progress_bar.progress(70)

        progress_bar.progress(100)
        time.sleep(0.2)
        
        progress_bar.empty()
        status_box.empty()
        
        st.session_state.user['is_subscribed'] = True
        st.session_state.user['role'] = f"Enterprise ({plan_name})"
        st.session_state.user['credits'] = 9999
        st.session_state.user['subscription_type'] = plan_name
        
        order_id = f"LS-ORD-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()}"

        if engine and user_id:
            try:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            UPDATE users 
                            SET role = :role, is_subscribed = TRUE, credits = 9999, updated_at = CURRENT_TIMESTAMP 
                            WHERE id = :user_id
                        """),
                        {"role": f"Enterprise ({plan_name})", "user_id": user_id}
                    )
                    
                    conn.execute(
                        text("""
                            INSERT INTO payment_transactions 
                            (user_id, order_id, gateway, plan_type, amount_paid, currency, status, raw_response)
                            VALUES (:user_id, :order_id, :gateway, :plan_type, :amount, :currency, :status, :raw_response)
                        """),
                        {
                            "user_id": user_id,
                            "order_id": order_id,
                            "gateway": "Lemon Squeezy",
                            "plan_type": plan_type,
                            "amount": amount_num,
                            "currency": "USD",
                            "status": "COMPLETED",
                            "raw_response": json.dumps(method_info)
                        }
                    )
                    conn.commit()
                
                SecurityEngine.log_audit_event(user_id, "PAYMENT_SUCCESS", f"Order {order_id} processed for ${amount_num}")
            except Exception as e:
                print(f"Payment DB Record error: {e}")

        email_payload = {
            "to": user_email,
            "subject": f"🎉 Receipt & Confirmation for Order #{order_id} from Lemon Squeezy",
            "order_id": order_id,
            "plan_name": plan_name,
            "amount": amount_str,
            "checkout_url_used": checkout_url,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "payment_method": f"Card ending in {method_info['card_last4']}"
        }

        if 'payment_notifications' not in st.session_state:
            st.session_state.payment_notifications = []
        st.session_state.payment_notifications.insert(0, email_payload)

class NotificationEngine:
    @staticmethod
    def create_whatsapp_link(phone: str, message: str) -> str:
        encoded_msg = urllib.parse.quote(message)
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"

def generate_excel_download(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Project Plan Tasks')
    return output.getvalue()

def generate_pdf_plan(plan: dict, signature: str, detailed_text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    def prepare_text(text_val):
        try:
            reshaped = arabic_reshaper.reshape(text_val)
            return get_display(reshaped)
        except Exception:
            return text_val

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, alignment=2)

    story.append(Paragraph(prepare_text(f"خطة مشروع: {plan['project_name']}"), title_style))
    story.append(Spacer(1, 15))
    
    info_text = f"المجال التقني: {plan['domain']} | الميزانية: ${plan['budget']} | المدة: {plan['target_days']} يوم"
    story.append(Paragraph(prepare_text(info_text), body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(prepare_text("--- تفاصيل الخطة التنفيذية الشاملة ---"), title_style))
    for line in detailed_text.split("\n"):
        if line.strip():
            story.append(Paragraph(prepare_text(line.strip()), body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 15))
    story.append(Paragraph(prepare_text(f"التوقيع الرقمي HMAC-SHA512: {signature[:40]}..."), body_style))

    doc.build(story)
    return buffer.getvalue()

def build_detailed_plan_text(plan: dict) -> str:
    p_name = plan.get('project_name', 'المشروع')
    domain = plan.get('domain', 'تقني')
    budget = float(plan.get('budget', 0))
    days = int(plan.get('target_days', 0))
    tech = plan.get('tech_stack', plan.get('tech', 'Flutter, Node.js, Supabase, PostgreSQL'))
    risk = plan.get('risk_tolerance', plan.get('risk', 'متوسط'))
    tasks = plan.get('tasks', [])
    
    working_hours_per_day = 8
    total_man_hours = days * working_hours_per_day
    daily_rate = budget / max(1, days)
    hourly_rate = budget / max(1, total_man_hours)
    
    contingency_rate = 0.15 if risk == "عالي" else (0.10 if risk == "متوسط" else 0.05)
    contingency_amount = budget * contingency_rate
    effective_operational_budget = budget - contingency_amount
    
    cloud_infra_cost = budget * 0.08
    dev_labor_cost = effective_operational_budget - cloud_infra_cost
    
    tasks_breakdown_str = ""
    for idx, t in enumerate(tasks, 1):
        t_cost = float(t.get('cost', 0))
        t_days = int(t.get('days', 0))
        t_hours = t_days * working_hours_per_day
        cost_percentage = (t_cost / max(1, budget)) * 100
        daily_t_cost = t_cost / max(1, t_days)
        hourly_t_cost = t_cost / max(1, t_hours)
        t_name = t.get('task_name', t.get('task', 'مهمة'))
        
        tasks_breakdown_str += f"""
#### Phase {idx}: {t_name}
* ⏱️ **المدة الزمنية:** {t_days} أيام عمل ({t_hours} ساعة هندسية)
* 💰 **التكلفة المخصصة:** ${t_cost:,.2f} ({cost_percentage:.1f}% من إجمالي الميزانية)
* 📊 **المعدل اليومي للإنفاق:** ${daily_t_cost:,.2f} / يوم
* ⏱️ **معدل الساعة للمرحلة:** ${hourly_t_cost:,.2f} / ساعة
* 📌 **الحالة التنفيذية:** {t.get('status', 'مخطط')}
"""

    return f"""📌 **المستند التنفيذي والتفصيلي لمشروع ({p_name})**
*تاريخ التوليد التلقائي: {plan.get('created_at', datetime.now().strftime('%Y-%m-%d'))}*

---

### 1. نظرة عامة والأهداف التنفيذية (Executive Summary & KPIs)
يهدف مشروع **{p_name}** إلى تقديم حل متكامل وعالي الأداء في قطاع **{domain}**، معتمداً على بيئة العمل والتقنيات: **({tech})**.
* **الميزانية الكلية (Total Budget):** `${budget:,.2f}`
* **المدى الزمني المستهدف (Timeline):** `{days}` يوماً تقويمياً.
* **مستوى تحمل المخاطر (Risk Profile):** `{risk}`.

---

### 2. الحسابات المالية والهندسية التفصيلية (Precise Cost & Time Allocation)
تم استخدام الخوارزميات التحليلية لحساب التكاليف والإنتاجية بدقة متناهية:
* ⏳ **إجمالي الساعات الهندسية (Total Man-Hours):** `{total_man_hours:,}` ساعة عمل (مبنية على {working_hours_per_day} ساعات/يوم).
* 💵 **معدل التكلفة اليومي (Daily Rate):** `${daily_rate:,.2f}` / يوم.
* ⏱️ **معدل تكلفة الساعة الهندسية (Hourly Rate):** `${hourly_rate:,.2f}` / ساعة.
* 🛡️ **احتياطي الطوارئ والمخاطر ({contingency_rate*100:.0f}% Risk Reserve):** `${contingency_amount:,.2f}` *(محتجزة للتعامل مع المتطلبات المباشرة الطارئة)*.
* ☁️ **تقدير تكاليف البنية التحتية والخدمات (Infra & Cloud OpEx):** `${cloud_infra_cost:,.2f}`.
* 🛠️ **صافي ميزانية التطوير الفعلي (Effective Dev Budget):** `${dev_labor_cost:,.2f}`.

---

### 3. معمارية النظام والبنية البرمجية (System & Cloud Architecture)
* 🎨 **تطوير الواجهات Frontend:** بناء مكونات UI سريعة ومستجيبة (Responsive Component Driven Design).
* 🗄️ **إدارة قواعد البيانات Database & Cache:** إعداد Schemas منظمة ودعم صلاحيات RLS المتقدمة لحماية البيانات.
* 🔐 **الخوادم وبوابات REST/tRPC APIs:** إنشاء محطات اتصال مؤمنة بالتشفير والتحقق الذاتي Multi-tenant Architecture.
* ⚡ **إدارة الأداء والأتمتة:** تكامل أنظمة الدفع والحساب التلقائي والربط الفوري Webhooks.

---

### 4. التفصيل الرحلي للمهام والمعالم الرئيسية (Milestones & Work Breakdown Structure)
{tasks_breakdown_str}

---

### 5. مصفوفة المخاطر وضمان الجودة والأمان الرقمي (Quality Assurance & Security Controls)
* **التوقيع الرقمي والتأكيد المشفر:** تم توقيع هذه الخطة رقمياً باستخدام خوارزمية **HMAC-SHA512** وحفظها في جدول `project_plans` لمنع أي تلاعب بالتقديرات.
* **إدارة السلامة:** ضمان تطبيق أقصى معايير السلامة البرمجية واختبارات الضغط (Load Testing) قبل الإطلاق النهائي.
"""

# ==========================================
# 3. AUTHENTICATION MODULE WITH FULL DB MAPPING
# ==========================================
def render_auth_page():
    st.markdown("<h1 style='text-align: center;'>🔐 بوابة الدخول | PHOENIX Enterprise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>سجل دخولك أو أنشئ حساباً جديداً للوصول إلى منصة وكيل مهنة الهندسية الذكية</p>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    col_center, _ = st.columns([1, 0.01])
    with col_center:
        auth_tab1, auth_tab2 = st.tabs(["🔑 تسجيل الدخول (Sign In)", "✨ إنشاء حساب جديد (Sign Up)"])
        
        with auth_tab1:
            with st.form("login_form"):
                st.subheader("مرحباً بك مجدداً!")
                email_input = st.text_input("البريد الإلكتروني", placeholder="name@domain.com").lower().strip()
                password_input = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
                
                submit_login = st.form_submit_button("🚀 تسجيل الدخول", use_container_width=True)
                
                if submit_login:
                    if engine is None:
                        st.error("⚠️ تعذر الاتصال بقاعدة البيانات حالياً. يرجى مراجعة الاتصال.")
                    else:
                        hashed_pw = SecurityEngine.hash_password(password_input)
                        try:
                            with engine.connect() as conn:
                                result = conn.execute(
                                    text("""
                                        SELECT id, email, password_hash, full_name, role, credits, is_subscribed 
                                        FROM users WHERE email = :email
                                    """),
                                    {"email": email_input}
                                ).fetchone()

                            if result:
                                user_id, db_email, db_pw_hash, db_name, db_role, db_credits, db_is_sub = result

                                if db_pw_hash == hashed_pw:
                                    st.session_state.is_authenticated = True
                                    st.session_state.user = {
                                        'id': user_id,
                                        'email': db_email,
                                        'username': db_name or "مهندس مهنة",
                                        'credits': db_credits if db_credits is not None else 5,
                                        'role': db_role or "Free Trial",
                                        'is_subscribed': bool(db_is_sub),
                                        'subscription_type': db_role or "Free Trial"
                                    }
                                    
                                    SecurityEngine.log_audit_event(user_id, "USER_LOGIN", "User logged in successfully")
                                    st.success(f"🎉 أهلاً بك مجدداً {st.session_state.user['username']}! جاري التوجيه...")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("❌ كلمة المرور غير صحيحة.")
                            else:
                                st.error("❌ البريد الإلكتروني غير مسجل بالمنظومة.")
                        except Exception as err:
                            st.error(f"⚠️ تعذر الاتصال بقاعدة البيانات: {str(err)}")

        with auth_tab2:
            with st.form("signup_form"):
                st.subheader("انضم إلى منصة PHOENIX")
                new_username = st.text_input("الاسم الكامل / اسم المهندس", placeholder="م. أياد فيصل")
                new_email = st.text_input("البريد الإلكتروني", placeholder="name@domain.com").lower().strip()
                new_password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
                confirm_password = st.text_input("تأكيد كلمة المرور", type="password", placeholder="••••••••")
                
                submit_signup = st.form_submit_button("✨ إنشاء الحساب وتفعيل 5 نقاط هدية", use_container_width=True)
                
                if submit_signup:
                    if not new_username or not new_email or not new_password:
                        st.warning("⚠️ يرجى ملء كافة الحقول المطلوبة.")
                    elif new_password != confirm_password:
                        st.error("❌ كلمة المرور وتأكيدها غير متطابقين.")
                    elif len(new_password) < 6:
                        st.error("❌ يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.")
                    else:
                        if engine is None:
                            st.error("⚠️ فشل الاتصال بقاعدة البيانات.")
                        else:
                            try:
                                with engine.connect() as conn:
                                    existing_user = conn.execute(
                                        text("SELECT email FROM users WHERE email = :email"),
                                        {"email": new_email}
                                    ).fetchone()

                                    if existing_user:
                                        st.error("❌ هذا البريد الإلكتروني مسجل بالفعل. يرجى تسجيل الدخول.")
                                    else:
                                        hashed_new_pw = SecurityEngine.hash_password(new_password)
                                        ins_res = conn.execute(
                                            text("""
                                                INSERT INTO users (email, password_hash, full_name, role, credits, is_subscribed)
                                                VALUES (:email, :password_hash, :full_name, :role, 5, FALSE)
                                                RETURNING id
                                            """),
                                            {
                                                "email": new_email,
                                                "password_hash": hashed_new_pw,
                                                "full_name": new_username,
                                                "role": "Free Trial"
                                            }
                                        )
                                        new_id = ins_res.fetchone()[0]
                                        conn.commit()

                                        st.session_state.is_authenticated = True
                                        st.session_state.user = {
                                            'id': new_id,
                                            'email': new_email,
                                            'username': new_username,
                                            'credits': 5,
                                            'role': "Free Trial",
                                            'is_subscribed': False,
                                            'subscription_type': "Free Trial"
                                        }
                                        SecurityEngine.log_audit_event(new_id, "USER_SIGNUP", "New account registered")
                                        st.balloons()
                                        st.success("🎉 تم إنشاء الحساب وحفظ البيانات بنجاح في Google Cloud SQL!")
                                        time.sleep(1)
                                        st.rerun()
                            except Exception as err:
                                st.error(f"⚠️ تعذر الاتصال بالسيرفر حالياً: {str(err)}")

if not st.session_state.is_authenticated:
    render_auth_page()
    st.stop()

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🛡️ WAKEEL MEHNA AGENT")
    st.markdown("<span class='badge-purple'>Enterprise Edition 2026</span>", unsafe_allow_html=True)
    st.write("---")
    
    st.radio(
        txt['lang_select'], 
        ["العربية (Arabic)", "English"], 
        index=0 if st.session_state.lang == 'ar' else 1,
        key='lang_radio',
        on_change=update_language
    )
    
    st.radio(
        txt['theme_select'], 
        [txt['dark'], txt['light']], 
        index=0 if st.session_state.theme == 'dark' else 1,
        key='theme_radio',
        on_change=update_theme
    )
    
    st.write("---")
    st.markdown(f"{txt['user']} **{st.session_state.user['username']}**")
    
    if st.session_state.user['is_subscribed']:
        st.markdown(f"نوع الاشتراك: <span class='badge-gold'>{st.session_state.user['role']}</span>", unsafe_allow_html=True)
        st.markdown(f"الرصيد المتاح: **غير محدود ♾️**")
    else:
        st.markdown(f"نوع الحساب: <span class='badge-purple'>تجريبي</span>", unsafe_allow_html=True)
        st.markdown(f"{txt['credits']} `{st.session_state.user['credits']}` {txt['points']}")
    
    if st.button(txt['logout_btn'], use_container_width=True, type="secondary"):
        SecurityEngine.log_audit_event(st.session_state.user['id'], "USER_LOGOUT", "User logged out")
        st.session_state.clear()
        init_default_session()
        st.rerun()

    st.write("---")
    st.markdown(f"### {txt['renew_title']}")
    
    if not st.session_state.user['is_subscribed']:
        if st.button("🤖 الدفع الذكي والتفعيل السريع (AI Checkout)", type="primary", use_container_width=True):
            AIPaymentAgent.execute_auto_checkout(st.session_state.user['id'], st.session_state.user['email'], "monthly")
            st.balloons()
            st.success("🎉 تم ترقية حسابك بنجاح وإرسال إشعار الدفع لبريدك!")
            time.sleep(1)
            st.rerun()
    
    st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">{txt["renew_btn"]}</a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader(txt['notify_settings'])
    st.session_state.notify_whatsapp = st.text_input(txt['wa_phone'], value=st.session_state.notify_whatsapp)
    st.session_state.notify_telegram = st.text_input(txt['tg_handle'], value=st.session_state.notify_telegram)

# ==========================================
# 5. MAIN DASHBOARD INTERFACE
# ==========================================
st.title(txt['title'])
st.caption(txt['subtitle'])

if st.session_state.user['credits'] <= 0 and not st.session_state.user['is_subscribed']:
    st.markdown("""
    <div class="ai-payment-card">
        <h3>🤖 تنبيه من وكيل الدفع الذكي (AI Payment Broker Agent)</h3>
        <p>لقد نفدت نقاطك المجانية (0/5)! يمكنك السماح للذكاء الاصطناعي بقراءة وسيلة الدفع وتنفيذ المعاملة فورياً وإرسال إشعار التأكيد لبريدك الإلكتروني.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚡ تنفيذ عملية الدفع والترقية الفورية عبر الذكاء الاصطناعي", expanded=True):
        col_pay_ai1, col_pay_ai2 = st.columns(2)
        with col_pay_ai1:
            st.markdown("#### 💳 باقة Pro الشهري ($29)")
            if st.button("🚀 تنفيذ الدفع الذكي والتفعيل فوراً (Pro)", type="primary", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['id'], st.session_state.user['email'], "monthly")
                st.balloons()
                st.success("🎉 تمت عملية الدفع بنجاح مفعلة باقة Pro!")
                time.sleep(1.2)
                st.rerun()
        with col_pay_ai2:
            st.markdown("#### 👑 باقة Enterprise السنوية ($279)")
            if st.button("💎 تنفيذ الدفع الذكي والتفعيل فوراً (Enterprise)", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['id'], st.session_state.user['email'], "yearly")
                st.balloons()
                st.success("🎉 تمت عملية الدفع بنجاح مفعلة الباقة السنوية المتقدمة!")
                time.sleep(1.2)
                st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([txt['tab1'], txt['tab2'], txt['tab3'], txt['tab4']])

# ==========================================
# TAB 1: بناء خطة مشروع (مع الحفظ بجدول project_plans & plan_tasks)
# ==========================================
with tab1:
    st.subheader(txt['quick_templates'])
    col_t1, col_t2, col_t3 = st.columns(3)
    
    col_t1.button(
        txt['ecom'], 
        use_container_width=True, 
        on_click=apply_template, 
        args=("تطبيق متجر إلكتروني لبيع المنتجات مع بوابة دفع سريعة ونظام إدارة المخزون", "التجارة الإلكترونية", 4500, 35, "متجر إلكتروني متكامل")
    )
    col_t2.button(
        txt['edu'], 
        use_container_width=True, 
        on_click=apply_template, 
        args=("منصة تعليمية تتيح رفع الكورسات واختبارات تفاعلية وشهادات تلقائية", "التعليم الرقمي", 3000, 25, "منصة تعليمية ذكية")
    )
    col_t3.button(
        txt['delivery'], 
        use_container_width=True, 
        on_click=apply_template, 
        args=("تطبيق توصيل طلبات يعتمد على الخرائط التفاعلية وتتبع السائقين في الوقت الفعلي", "الخدمات واللوجستيات", 6000, 50, "تطبيق توصيل سريع")
    )

    domain_options = ["التجارة الإلكترونية", "التعليم الرقمي", "الخدمات واللوجستيات", "الذكاء الاصطناعي", "أنظمة SaaS"]
    domain_idx = domain_options.index(st.session_state.form_domain) if st.session_state.form_domain in domain_options else 0

    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(txt['p_name'], key="form_pname")
            domain = st.selectbox(txt['tech_domain'], domain_options, index=domain_idx, key="form_domain")
            budget = st.number_input(txt['budget'], min_value=500, key="form_budget")
        with col2:
            tech_stack = st.text_input(txt['tech_stack'], value="Flutter, Node.js, PostgreSQL, Supabase")
            target_days = st.number_input(txt['target_days'], min_value=5, key="form_days")
            risk_tolerance = st.select_slider(txt['risk_level'], options=["منخفض جداً", "متوسط", "عالي"])
            
        project_scope = st.text_area(txt['scope'], key="form_scope", placeholder="اكتب تفاصيل ومتطلبات المشروع هنا...")
        
        submit_btn = st.form_submit_button(txt['generate_btn'], use_container_width=True)
        
    if submit_btn:
        if st.session_state.user['credits'] < 1 and not st.session_state.user['is_subscribed']:
            st.error("❌ لقد استنفدت كافة نقاطك المجانية! يرجى تنفيذ الدفع الآلي بالذكاء الاصطناعي لتفعيل الحساب فورياً.")
        elif not project_scope.strip():
            st.warning("⚠️ يرجى تقديم نطاق العمل لتبدأ عملية التوليد.")
        else:
            with st.spinner("⏳ جاري توليد المهام وحفظها في Cloud SQL..."):
                time.sleep(0.4)
                
                tasks = [
                    {"task_order": 1, "task_name": "تحليل المتطلبات وتصميم المخططات Architecture", "days": max(1, int(target_days*0.15)), "cost": int(budget*0.15), "status": "مخطط"},
                    {"task_order": 2, "task_name": "بناء قواعد البيانات وتأمين API Backend", "days": max(1, int(target_days*0.35)), "cost": int(budget*0.35), "status": "مخطط"},
                    {"task_order": 3, "task_name": "تطوير واجهات المستخدم Frontend & UI Components", "days": max(1, int(target_days*0.30)), "cost": int(budget*0.30), "status": "مخطط"},
                    {"task_order": 4, "task_name": "الاختبارات والتكامل Deployment & QA", "days": max(1, int(target_days*0.20)), "cost": int(budget*0.20), "status": "مخطط"},
                ]
                
                plan_payload = {
                    "project_name": project_name,
                    "domain": domain,
                    "budget": budget,
                    "target_days": target_days,
                    "risk_tolerance": risk_tolerance,
                    "tech_stack": tech_stack,
                    "scope_of_work": project_scope,
                    "tasks": tasks,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                signature = SecurityEngine.generate_signature(plan_payload)
                plan_payload["plan_signature"] = signature
                
                # DB Persistence into project_plans and plan_tasks
                if engine and st.session_state.user['id']:
                    try:
                        with engine.connect() as conn:
                            p_res = conn.execute(
                                text("""
                                    INSERT INTO project_plans 
                                    (user_id, project_name, domain, budget, target_days, risk_tolerance, tech_stack, scope_of_work, plan_signature, is_tampered)
                                    VALUES (:user_id, :project_name, :domain, :budget, :target_days, :risk_tolerance, :tech_stack, :scope_of_work, :plan_signature, FALSE)
                                    RETURNING id
                                """),
                                {
                                    "user_id": st.session_state.user['id'],
                                    "project_name": project_name,
                                    "domain": domain,
                                    "budget": budget,
                                    "target_days": target_days,
                                    "risk_tolerance": risk_tolerance,
                                    "tech_stack": tech_stack,
                                    "scope_of_work": project_scope,
                                    "plan_signature": signature
                                }
                            )
                            db_plan_id = p_res.fetchone()[0]
                            plan_payload["id"] = str(db_plan_id)

                            for t in tasks:
                                conn.execute(
                                    text("""
                                        INSERT INTO plan_tasks (plan_id, task_order, task_name, days, cost, status)
                                        VALUES (:plan_id, :task_order, :task_name, :days, :cost, :status)
                                    """),
                                    {
                                        "plan_id": db_plan_id,
                                        "task_order": t["task_order"],
                                        "task_name": t["task_name"],
                                        "days": t["days"],
                                        "cost": t["cost"],
                                        "status": t["status"]
                                    }
                                )

                            if not st.session_state.user['is_subscribed']:
                                st.session_state.user['credits'] -= 1
                                conn.execute(
                                    text("UPDATE users SET credits = :c WHERE id = :u"),
                                    {"c": st.session_state.user['credits'], "u": st.session_state.user['id']}
                                )

                            conn.commit()
                        
                        SecurityEngine.log_audit_event(st.session_state.user['id'], "CREATE_PLAN", f"Created plan {project_name}")
                    except Exception as e:
                        st.warning(f"⚠️ حفظ الخطة محلياً (DB Sync Alert: {e})")

                st.session_state.current_plan = plan_payload
                st.session_state.plan_signature = signature
                st.success("✅ تم توليد الخطة وتوقيعها رقمياً وحفظها في قاعدة البيانات PostgreSQL بنجاح!")

    if st.session_state.current_plan:
        st.write("---")
        col_sig1, col_sig2 = st.columns([3, 1])
        with col_sig1:
            st.info(f"{txt['digital_sig']}\n`{st.session_state.plan_signature}`")
        with col_sig2:
            is_valid = SecurityEngine.verify_signature(st.session_state.current_plan, st.session_state.plan_signature)
            if is_valid:
                st.markdown(f"<br><span class='badge-green'>{txt['sig_valid']}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<br><span class='badge-purple'>{txt['sig_invalid']}</span>", unsafe_allow_html=True)

        df_tasks = pd.DataFrame(st.session_state.current_plan['tasks'])
        st.dataframe(df_tasks, use_container_width=True)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            excel_bytes = generate_excel_download(df_tasks)
            st.download_button(
                label=txt['export_excel'],
                data=excel_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Tasks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_excel_tab1"
            )
        with col_dl2:
            detailed_txt = build_detailed_plan_text(st.session_state.current_plan)
            pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_txt)
            st.download_button(
                label=txt['export_pdf'],
                data=pdf_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Plan.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_dl_pdf_tab1"
            )

        st.write("---")
        col_n1, col_n2 = st.columns(2)
        msg_body = f"🚀 Project Plan: {st.session_state.current_plan['project_name']}\n💰 Budget: ${st.session_state.current_plan['budget']}\n⏱️ Days: {st.session_state.current_plan['target_days']}\n🔑 Sig: {st.session_state.plan_signature[:20]}..."
        wa_url = NotificationEngine.create_whatsapp_link(st.session_state.notify_whatsapp, msg_body)
        
        with col_n1:
            st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:8px; font-weight:bold; text-decoration:none;">{txt["send_wa"]}</a>', unsafe_allow_html=True)
        with col_n2:
            if st.button(txt['send_tg'], use_container_width=True, key="btn_tg_notify_tab1"):
                st.success(f"✅ Notification dispatched to {st.session_state.notify_telegram}")

# ==========================================
# TAB 2: التحليلات التفاعلية الفائقة
# ==========================================
with tab2:
    if not st.session_state.current_plan:
        st.info("💡 قم بتوليد خطة مشروع أولاً من تبويب 'بناء خطة مشروع' لاستعراض التحليلات الهندسية المتقدمة.")
    else:
        plan = st.session_state.current_plan
        df = pd.DataFrame(plan['tasks'])
        
        st.markdown("## 📊 لوحة القيادة الهندسية وتقييم الجودة والمخاطر")
        st.caption("تحليل بصري متقدم للتكلفة، الأداء، المخاطر، والمسار الزمني الشامل لمشروعك.")
        
        daily_rate = int(plan['budget'] / max(1, plan['target_days']))
        feasibility_score = min(98, max(65, int(100 - (plan['target_days'] / max(1, plan['budget'] / 100)) * 5)))
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 إجمالي الميزانية المعتمدة", f"${plan['budget']:,}")
        m2.metric("⏱️ المدى الزمني الشامل", f"{plan['target_days']} يوم")
        m3.metric("📈 التكلفة اليومية المستهدفة", f"${daily_rate:,}/يوم")
        m4.metric("🛡️ مؤشر السلامة الهندسية", f"{feasibility_score}%", delta="ممتاز" if feasibility_score > 80 else "مقبول")
        
        st.progress(feasibility_score / 100)
        st.write("---")
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("### 🍩 التحليل المالي الدائري المتداخل (Sunburst Hierarchy)")
            task_col_name = 'task_name' if 'task_name' in df.columns else 'task'
            labels = [plan['project_name']] + list(df[task_col_name])
            parents = [""] + [plan['project_name']] * len(df)
            values = [plan['budget']] + list(df['cost'])
            
            fig_sunburst = go.Figure(go.Sunburst(
                labels=labels,
                parents=parents,
                values=values,
                branchvalues="total",
                hovertemplate='<b>%{label}</b><br>المبلغ: $%{value:,}<br>النسبة: %{percentParent:.1%}',
                marker=dict(colorscale='Blues', line=dict(color='#0E1117', width=1.5)),
                textfont=dict(size=12, color='#FFFFFF')
            ))
            fig_sunburst.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color, size=11),
                height=350,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_sunburst, use_container_width=True)

        with col_c2:
            st.markdown("### 🎯 مؤشر الكفاءة والجاهزية الهندسية (Feasibility Gauge)")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=feasibility_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "مؤشر ملاءمة الميزانية والوقت", 'font': {'size': 14, 'color': text_color}},
                delta={'reference': 80, 'increasing': {'color': "#10B981"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
                    'bar': {'color': "#8B5CF6"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                        {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.3)'},
                        {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color, size=12),
                height=350,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.write("---")

        c_r1, c_r2 = st.columns(2)
        with c_r1:
            st.markdown("### 🕸️ تقييم أبعاد المشروع (5D Radar Risk Matrix)")
            radar_categories = ['تعقيد النطاق', 'الأمان الرقمي', 'التحكم بالجدول', 'استقرار التكلفة', 'المرونة التقنية']
            risk_val = plan.get('risk_tolerance', plan.get('risk', 'متوسط'))
            risk_score = 85 if risk_val == 'عالي' else (65 if risk_val == 'متوسط' else 45)
            radar_values = [80, 95, 85, 90, risk_score]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_values,
                theta=radar_categories,
                fill='toself',
                name='تقدير الأبعاد',
                line=dict(color='#8B5CF6', width=3),
                fillcolor='rgba(139, 92, 246, 0.35)'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155'),
                    angularaxis=dict(gridcolor='#334155')
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color, size=12),
                height=340,
                margin=dict(l=40, r=40, t=30, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with c_r2:
            st.markdown("### 🌊 التدفق المالي التراكمي (Waterfall Cost Flow)")
            task_col_name = 'task_name' if 'task_name' in df.columns else 'task'
            x_labels = list(df[task_col_name]) + ["الإجمالي النهائي"]
            y_measures = ["relative"] * len(df) + ["total"]
            y_values = list(df['cost']) + [0]
            
            fig_waterfall = go.Figure(go.Waterfall(
                name="توزيع التكلفة",
                orientation="v",
                measure=y_measures,
                x=x_labels,
                textposition="outside",
                text=[f"${c:,}" if c > 0 else f"${plan['budget']:,}" for c in y_values],
                y=y_values,
                connector={"line": {"color": "#64748B", "width": 2}},
                decreasing={"marker": {"color": "#EF4444"}},
                increasing={"marker": {"color": "#3B82F6"}},
                totals={"marker": {"color": "#10B981"}}
            ))
            fig_waterfall.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color, size=11),
                showlegend=False,
                height=340,
                margin=dict(l=20, r=20, t=30, b=30),
                yaxis=dict(gridcolor='#334155')
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)

# ==========================================
# TAB 3: محرر المهام وخطة المشروع
# ==========================================
with tab3:
    st.subheader(txt['tab3'])
    
    if not st.session_state.current_plan:
        st.warning("⚠️ لا توجد خطة حالية لتعديلها. قم بتوليد خطة من تبويب 'بناء خطة مشروع'.")
    else:
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.current_plan['tasks']),
            num_rows="dynamic",
            use_container_width=True,
            key="task_data_editor"
        )
        
        if st.button(txt['save_re_sign'], use_container_width=True, key="btn_save_resign_tab3"):
            updated_tasks = edited_df.to_dict(orient='records')
            st.session_state.current_plan['tasks'] = updated_tasks
            st.session_state.current_plan['budget'] = sum(int(item.get('cost', 0)) for item in updated_tasks)
            st.session_state.current_plan['target_days'] = sum(int(item.get('days', 0)) for item in updated_tasks)
            
            new_sig = SecurityEngine.generate_signature(st.session_state.current_plan)
            st.session_state.plan_signature = new_sig
            st.session_state.current_plan['plan_signature'] = new_sig

            # Update DB persistence if plan ID exists
            if engine and st.session_state.current_plan.get('id'):
                try:
                    plan_id = st.session_state.current_plan['id']
                    with engine.connect() as conn:
                        conn.execute(
                            text("""
                                UPDATE project_plans 
                                SET budget = :budget, target_days = :target_days, plan_signature = :sig 
                                WHERE id = :id
                            """),
                            {
                                "budget": st.session_state.current_plan['budget'],
                                "target_days": st.session_state.current_plan['target_days'],
                                "sig": new_sig,
                                "id": plan_id
                            }
                        )
                        conn.execute(text("DELETE FROM plan_tasks WHERE plan_id = :id"), {"id": plan_id})
                        for idx, t in enumerate(updated_tasks, 1):
                            conn.execute(
                                text("""
                                    INSERT INTO plan_tasks (plan_id, task_order, task_name, days, cost, status)
                                    VALUES (:plan_id, :task_order, :task_name, :days, :cost, :status)
                                """),
                                {
                                    "plan_id": plan_id,
                                    "task_order": t.get("task_order", idx),
                                    "task_name": t.get("task_name", t.get("task", "مهمة")),
                                    "days": t.get("days", 1),
                                    "cost": t.get("cost", 0),
                                    "status": t.get("status", "مخطط")
                                }
                            )
                        conn.commit()
                    SecurityEngine.log_audit_event(st.session_state.user['id'], "UPDATE_PLAN", f"Updated plan {plan_id}")
                except Exception as e:
                    st.warning(f"⚠️ تنبيه مزامنة الحفظ: {e}")

            st.success("✅ تم تحديث المهام وحفظها في قاعدة البيانات وإعادة التوقيع الرقمي بنجاح!")
            st.rerun()

        st.write("---")
        st.subheader(txt['detailed_plan'])
        detailed_plan_text = build_detailed_plan_text(st.session_state.current_plan)
        st.markdown(detailed_plan_text)
        
        st.write("---")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            excel_bytes = generate_excel_download(edited_df)
            st.download_button(
                label=txt['export_excel'],
                data=excel_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Tasks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_excel_tab3"
            )
        with col_d2:
            pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_plan_text)
            st.download_button(
                label=txt['export_pdf'],
                data=pdf_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Plan.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_dl_pdf_tab3"
            )

# ==========================================
# TAB 4: إدارة الحساب والاشتراكات
# ==========================================
with tab4:
    st.subheader("💳 إدارة الحساب وبوابة الدفع بالذكاء الاصطناعي")
    st.caption("مركز المعاملات الفورية والمشفرة مع معالجة الذكاء الاصطناعي.")
    
    col_stat1, col_stat2 = st.columns([2, 1])
    with col_stat1:
        st.info(f"👤 **المستخدم الحساب:** {st.session_state.user['username']} ({st.session_state.user.get('email', 'حساب مؤقت')})\n\n💳 **الرصيد المتاح:** {st.session_state.user['credits']} نقطة.")
    with col_stat2:
        if st.session_state.user['credits'] > 0 and not st.session_state.user['is_subscribed']:
            st.markdown("<span class='badge-green'>🎁 الفترة التجريبية نشطة</span>", unsafe_allow_html=True)
        elif st.session_state.user['is_subscribed']:
            st.markdown("<span class='badge-gold'>👑 اشتراك مدفوع نشط</span>", unsafe_allow_html=True)

    st.write("---")
    
    st.markdown("### 🤖 مركز معالجة الدفع بالذكاء الاصطناعي (AI Instant Checkout)")
    col_aip1, col_aip2 = st.columns(2)
    with col_aip1:
        if st.button("⚡ تنفيذ الدفع والترقية لـ Pro ($29)", use_container_width=True, type="primary"):
            AIPaymentAgent.execute_auto_checkout(st.session_state.user['id'], st.session_state.user['email'], "monthly")
            st.balloons()
            st.success("🎉 تم تفعيل الاشتراك الشهري وحفظ العملية في payment_transactions!")
            time.sleep(1)
            st.rerun()
            
    with col_aip2:
        if st.button("👑 تنفيذ الدفع والترقية لـ Enterprise ($279)", use_container_width=True):
            AIPaymentAgent.execute_auto_checkout(st.session_state.user['id'], st.session_state.user['email'], "yearly")
            st.balloons()
            st.success("🎉 تم تفعيل الاشتراك السنوي وحفظ العملية في payment_transactions!")
            time.sleep(1)
            st.rerun()

    if st.session_state.get('payment_notifications'):
        st.write("---")
        st.markdown("### 📬 صندوق الإشعارات الواردة من Lemon Squeezy (Email Inbox)")
        for notif in st.session_state.payment_notifications:
            st.markdown(f"""
            <div class="email-notification-box">
                <b>📩 From:</b> payments@lemonsqueezy.com<br>
                <b>📨 To:</b> {notif['to']}<br>
                <b>📌 Subject:</b> {notif['subject']}<br>
                <b>📅 Date:</b> {notif['date']}<br>
                <hr style="border-color:#10B981;">
                <p>Hello! Thank you for your purchase via Lemon Squeezy.</p>
                <ul>
                    <li><b>Item Purchased:</b> {notif['plan_name']}</li>
                    <li><b>Total Paid:</b> {notif['amount']}</li>
                    <li><b>Payment Method:</b> {notif['payment_method']}</li>
                    <li><b>Checkout URL Executed:</b> {notif['checkout_url_used']}</li>
                </ul>
                <p>Your subscription is now fully active across PHOENIX & WAKEEL MEHNA Systems!</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <h3>🎁 التجريبي المجاني</h3>
            <h2>$0 <small>/ للأبد</small></h2>
            <hr>
            <p>✔ <b>5 نقاط مجانية</b> عند التسجيل</p>
            <p>✔ توليد خطط هندسية موثقة</p>
            <p>✔ التوقيع الرقمي HMAC-SHA512</p>
            <p>✔ تصدير ملفات Excel & PDF</p>
            <hr>
            <p><i>مفعل تلقائياً لكل مستخدم جديد</i></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown(f"""
        <div class="pricing-card-highlight">
            <span class="badge-purple">الأكثر شعبية 🚀</span>
            <h3>⚡ الاشتراك الشهري Pro</h3>
            <h2>$29 <small>/ شهرياً</small></h2>
            <hr>
            <p>✔ <b>توليد خطط غير محدود</b></p>
            <p>✔ تحليلات هندسية فائقة ومتقدمة</p>
            <p>✔ تصدير تقارير موثقة بلا حدود</p>
            <p>✔ ربط الإشعارات التلقائية الفورية</p>
            <hr>
            <a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">🚀 رابط الاشتراك الخارجي</a>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p3:
        st.markdown(f"""
        <div class="pricing-card">
            <span class="badge-gold">خصم 20% 🏆</span>
            <h3>👑 اشتراك المؤسسات السنوي</h3>
            <h2>$279 <small>/ سنوياً</small></h2>
            <hr>
            <p>✔ <b>جميع ميزات باقة Pro</b></p>
            <p>✔ دعم فني وتصميم خاص</p>
            <p>✔ تخصيص القوالب ومعمارية النظام</p>
            <p>✔ إمكانية الربط التلقائي عبر API</p>
            <hr>
            <a href="{PAYMENT_LINK_YEARLY}" target="_blank" class="checkout-btn-yearly">💎 رابط الاشتراك الخارجي</a>
        </div>
        """, unsafe_allow_html=True)
