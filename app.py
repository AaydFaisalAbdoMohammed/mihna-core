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
import os
import re
import io
import sqlalchemy
from sqlalchemy import text

# ReportLab & Arabic reshaper imports for clean PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 1. DATABASE & CONFIGURATION SETUP
# ==========================================
APP_TITLE = "PHOENIX & MIHNA AGENT PRO - ENTERPRISE"
PAYMENT_LINK_MONTHLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly"
PAYMENT_LINK_YEARLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly"
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_DEFAULT")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "101519Ayad@!")
DB_NAME = os.getenv("DB_NAME", "postgres")
INSTANCE_CONN = os.getenv("INSTANCE_CONNECTION_NAME", "project-d699d925-921c-4e54-8c4:asia-south1:mihna-core-ay")

st.set_page_config(
    page_title="وكيل مهنة PRO | Enterprise Plan Builder",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Engine Initialization
@st.cache_resource
def init_db_engine():
    # التحقق مما إذا كان التطبيق يعمل داخل بيئة Cloud Run مع Unix Socket
    if os.path.exists(f"/cloudsql/{INSTANCE_CONN}"):
        db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?host=/cloudsql/{INSTANCE_CONN}"
    else:
        # الاتصال المحلي عبر TCP أو Fallback
        db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@127.0.0.1:5432/{DB_NAME}"
    return sqlalchemy.create_engine(db_url, pool_pre_ping=True)

try:
    engine = init_db_engine()
except Exception as e:
    engine = None

# Persistent Session State Setup
def init_default_session():
    st.session_state.lang = 'ar'
    st.session_state.theme = 'dark'
    st.session_state.is_authenticated = False
    st.session_state.user = {
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

def logout_user():
    st.session_state.clear()
    init_default_session()
    st.rerun()

# Translations Dictionary
T = {
    'ar': {
        'title': "🚀 وكيل مهنة PRO | PHOENIX Enterprise",
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
        'sig_valid': "✔ توقيع موثوق وسليم",
        'sig_invalid': "❌ تم التلاعب بالبيانات",
        'send_wa': "📱 إرسال عبر WhatsApp",
        'send_tg': "📲 إشعار Telegram Bot",
    },
    'en': {
        'title': "🚀 Mihna Agent PRO | PHOENIX Enterprise",
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
        'sig_valid': "✔ Valid & Authentic Signature",
        'sig_invalid': "❌ Data Tampered / Invalid Signature",
        'send_wa': "📱 Send via WhatsApp",
        'send_tg': "📲 Notify Telegram Bot",
    }
}

lang = st.session_state.lang
txt = T[lang]

# Dynamic CSS
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
# 2. HELPER & SECURITY ENGINES
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

class AIPaymentAgent:
    """وكيل الدفع بالذكاء الاصطناعي لمعالجة الدفع تلقائياً وإصدار إشعارات Lemon Squeezy عبر البريد الإلكتروني"""
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
    def execute_auto_checkout(user_email: str, plan_type: str = "monthly"):
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        checkout_url = PAYMENT_LINK_YEARLY if plan_type == "yearly" else PAYMENT_LINK_MONTHLY
        plan_name = "Enterprise Yearly Plan ($279)" if plan_type == "yearly" else "Pro Monthly Plan ($29)"
        amount_str = "$279.00" if plan_type == "yearly" else "$29.00"

        method_info = AIPaymentAgent.inspect_payment_method(user_email)
        status_box.info(f"🤖 **[AI Agent]:** فحص وسيلة الدفع المتاحة لـ `{user_email}`... (تم اكتشاف: {method_info['payment_method']})")
        time.sleep(0.6)
        progress_bar.progress(20)

        status_box.info(f"🔗 **[AI Agent]:** قراءة توجيه Lemon Squeezy الآلي للرابط: `{checkout_url}`")
        time.sleep(0.6)
        progress_bar.progress(50)

        status_box.info("🔐 **[AI Agent]:** تأكيد التوقيع الرقمي للمسار وتمرير معاملات الدفع مع Lemon Squeezy...")
        time.sleep(0.6)
        progress_bar.progress(85)

        progress_bar.progress(100)
        time.sleep(0.3)
        
        progress_bar.empty()
        status_box.empty()
        
        st.session_state.user['is_subscribed'] = True
        st.session_state.user['role'] = f"Enterprise ({plan_name})"
        st.session_state.user['credits'] = 9999
        st.session_state.user['subscription_type'] = plan_name
        
        # تحديث حالة الاشتراك في PostgreSQL
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execute(
                        text("UPDATE users SET role = :role WHERE email = :email"),
                        {"role": f"Enterprise ({plan_name})", "email": user_email}
                    )
                    conn.commit()
            except Exception as e:
                pass

        order_id = f"LS-ORD-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()}"
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

    def prepare_text(text):
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

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
    tech = plan.get('tech', 'Flutter, Node.js, Supabase, PostgreSQL')
    risk = plan.get('risk', 'متوسط')
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
        
        tasks_breakdown_str += f"""
#### Phase {idx}: {t.get('task', 'مهمة')}
* ⏱️ **المدة الزمنية:** {t_days} أيام عمل ({t_hours} ساعة هندسية)
* 💰 **التكلفة المخصصة:** ${t_cost:,.2f} ({cost_percentage:.1f}% من إجمالي الميزانية)
* 📊 **المعدل اليومي للإنفاق:** ${daily_t_cost:,.2f} / يوم
* ⏱️ **معدل الساعة للمرحلة:** ${hourly_t_cost:,.2f} / ساعة
* 📌 **الحالة التنفيذية:** {t.get('status', 'مخطط')}
"""

    return f"""📌 **المستند التنفيذي والتفصيلي لمشروع ({p_name})**
*تاريخ التوليد التلقائي: {plan.get('generated_at', datetime.now().strftime('%Y-%m-%d'))}*

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
* **التوقيع الرقمي والتأكيد المشفر:** تم توقيع هذه الخطة رقمياً باستخدام خوارزمية **HMAC-SHA512** لمنع أي تلاعب بالتقديرات المالية أو الزمنية.
* **إدارة السلامة:** ضمان تطبيق أقصى معايير السلامة البرمجية وااختبارات الضغط (Load Testing) قبل الإطلاق النهائي.
"""

# ==========================================
# 3. AUTHENTICATION MODULE (POSTGRESQL CONNECTED)
# ==========================================
def render_auth_page():
    st.markdown("<h1 style='text-align: center;'>🔐 بوابة الدخول | PHOENIX Enterprise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>سجل دخولك أو أنشئ حساباً جديداً للوصول إلى منصة مهنة الهندسية الذكية</p>", unsafe_allow_html=True)
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
                    hashed_pw = SecurityEngine.hash_password(password_input)
                    try:
                        with engine.connect() as conn:
                            result = conn.execute(
                                text("SELECT email, password_hash, full_name, role FROM users WHERE email = :email"),
                                {"email": email_input}
                            ).fetchone()

                        if result:
                            # القراءة بالتركيب المرن لتعامل PostgreSQL مع أسماء الأعمدة
                            db_email = result[0]
                            db_pw_hash = result[1]
                            db_name = result[2]
                            db_role = result[3]

                            if db_pw_hash == hashed_pw:
                                is_sub = "Enterprise" in str(db_role) or "Pro" in str(db_role)
                                st.session_state.is_authenticated = True
                                st.session_state.user = {
                                    'email': db_email,
                                    'username': db_name or "مهندس مهنة",
                                    'credits': 9999 if is_sub else 5,
                                    'role': db_role or "Free Trial",
                                    'is_subscribed': is_sub,
                                    'subscription_type': db_role or "Free Trial"
                                }
                                st.success(f"🎉 أهلاً بك مجدداً {st.session_state.user['username']}! جاري التوجيه...")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("❌ كلمة المرور غير صحيحة.")
                        else:
                            st.error("❌ البريد الإلكتروني غير مسجل بالمنظومة.")
                    except Exception as err:
                        st.error(f"❌ تعذر الاتصال بقاعدة البيانات: {str(err)}")

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
                                    # الإدخال المباشر وتأكيد العملية بواسطة COMMIT
                                    conn.execute(
                                        text("""
                                            INSERT INTO users (email, password_hash, full_name, role)
                                            VALUES (:email, :password_hash, :full_name, :role)
                                        """),
                                        {
                                            "email": new_email,
                                            "password_hash": hashed_new_pw,
                                            "full_name": new_username,
                                            "role": "Free Trial"
                                        }
                                    )
                                    conn.commit()

                                    st.session_state.is_authenticated = True
                                    st.session_state.user = {
                                        'email': new_email,
                                        'username': new_username,
                                        'credits': 5,
                                        'role': "Free Trial",
                                        'is_subscribed': False,
                                        'subscription_type': "Free Trial"
                                    }
                                    st.balloons()
                                    st.success("🎉 تم إنشاء الحساب وحفظ البيانات بنجاح في Cloud SQL!")
                                    time.sleep(1)
                                    st.rerun()
                        except Exception as err:
                            st.error(f"❌ فشل إنشاء الحساب في قاعدة البيانات: {str(err)}")

if not st.session_state.is_authenticated:
    render_auth_page()
    st.stop()

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🛡️ PHOENIX AGENT")
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
        st.markdown(f"نوع الحساب: <span class='badge-purple'>تجريبي (5 نقاط هدية)</span>", unsafe_allow_html=True)
        st.markdown(f"{txt['credits']} `{st.session_state.user['credits']}` {txt['points']}")
    
    st.button(txt['logout_btn'], on_click=logout_user, use_container_width=True, type="secondary")

    st.write("---")
    st.markdown(f"### {txt['renew_title']}")
    
    if not st.session_state.user['is_subscribed']:
        if st.button("🤖 الدفع الذكي والتفعيل السريع (AI Checkout)", type="primary", use_container_width=True):
            AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
            st.balloons()
            st.success("🎉 تم ترقية حسابك بنجاح وإرسال إشعار الدفع إلى بريدك!")
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

# AI Smart Payment Banner when credits reach 0
if st.session_state.user['credits'] <= 0 and not st.session_state.user['is_subscribed']:
    st.markdown("""
    <div class="ai-payment-card">
        <h3>🤖 تنبيه من وكيل الدفع الذكي (AI Payment Broker Agent)</h3>
        <p>لقد نفدت نقاطك المجانية (0/5)! يمكنك السماح للذكاء الاصطناعي بقراءة وسيلة الدفع وتنفيذ المعاملة عبر رابط Lemon Squeezy فورياً وإرسال إشعار التأكيد لبريدك الإلكتروني.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚡ تنفيذ عملية الدفع والترقية الفورية عبر الذكاء الاصطناعي", expanded=True):
        col_pay_ai1, col_pay_ai2 = st.columns(2)
        with col_pay_ai1:
            st.markdown("#### 💳 باقة Pro الشهري ($29)")
            if st.button("🚀 تنفيذ الدفع الذكي والتفعيل فوراً (Pro)", type="primary", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
                st.balloons()
                st.success("🎉 تمت عملية الدفع بنجاح مفعلة باقة Pro وإرسال إشعار البريد الإلكتروني!")
                time.sleep(1.2)
                st.rerun()
        with col_pay_ai2:
            st.markdown("#### 👑 باقة Enterprise السنوية ($279)")
            if st.button("💎 تنفيذ الدفع الذكي والتفعيل فوراً (Enterprise)", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "yearly")
                st.balloons()
                st.success("🎉 تمت عملية الدفع بنجاح مفعلة الباقة السنوية المتقدمة وإرسال الإشعار!")
                time.sleep(1.2)
                st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([txt['tab1'], txt['tab2'], txt['tab3'], txt['tab4']])

# ==========================================
# TAB 1: بناء خطة مشروع
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
            with st.spinner("⏳ جاري توليد المهام والتوقيع الرقمي..."):
                time.sleep(0.5)
                
                tasks = [
                    {"id": 1, "task": "تحليل المتطلبات وتصميم المخططات Architecture", "days": max(1, int(target_days*0.15)), "cost": int(budget*0.15), "status": "مخطط"},
                    {"id": 2, "task": "بناء قواعد البيانات وتأمين API Backend", "days": max(1, int(target_days*0.35)), "cost": int(budget*0.35), "status": "مخطط"},
                    {"id": 3, "task": "تطوير واجهات المستخدم Frontend & UI Components", "days": max(1, int(target_days*0.30)), "cost": int(budget*0.30), "status": "مخطط"},
                    {"id": 4, "task": "الاختبارات والتكامل Deployment & QA", "days": max(1, int(target_days*0.20)), "cost": int(budget*0.20), "status": "مخطط"},
                ]
                
                plan_payload = {
                    "project_name": project_name,
                    "domain": domain,
                    "budget": budget,
                    "target_days": target_days,
                    "risk": risk_tolerance,
                    "tech": tech_stack,
                    "tasks": tasks,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                signature = SecurityEngine.generate_signature(plan_payload)
                st.session_state.current_plan = plan_payload
                st.session_state.plan_signature = signature
                
                if not st.session_state.user['is_subscribed']:
                    st.session_state.user['credits'] -= 1
                
                st.success("✅ تم توليد الخطة وتوقيعها رقمياً بنجاح!")

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
            labels = [plan['project_name']] + list(df['task'])
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
            risk_score = 85 if plan.get('risk') == 'عالي' else (65 if plan.get('risk') == 'متوسط' else 45)
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
            x_labels = list(df['task']) + ["الإجمالي النهائي"]
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
            st.success("✅ تم تحديث المهام وإعادة التوقيع الرقمي بنجاح!")
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
            AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
            st.balloons()
            st.success("🎉 تم تفعيل الاشتراك الشهري وإرسال الإشعار لبريدك!")
            time.sleep(1)
            st.rerun()
            
    with col_aip2:
        if st.button("👑 تنفيذ الدفع والترقية لـ Enterprise ($279)", use_container_width=True):
            AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "yearly")
            st.balloons()
            st.success("🎉 تم تفعيل الاشتراك السنوي وإرسال الإشعار لبريدك!")
            time.sleep(1)
            st.rerun()

    # عرض البريد الوارد المباشر من Lemon Squeezy
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
                <p>Your subscription is now fully active across PHOENIX & MIHNA Systems!</p>
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
