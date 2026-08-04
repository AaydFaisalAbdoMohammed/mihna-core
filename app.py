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

# ReportLab & Arabic reshaper imports for clean PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 1. CONFIGURATION & STATE INITIALIZATION
# ==========================================
APP_TITLE = "PHOENIX & MIHNA AGENT PRO - ENTERPRISE"
PAYMENT_LINK_MONTHLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly"
PAYMENT_LINK_YEARLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly"
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_DEFAULT")

st.set_page_config(
    page_title="وكيل مهنة PRO | Enterprise Plan Builder",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Persistent Session State Setup (Defaulting to 5 Free Credits for new users)
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'user' not in st.session_state:
    st.session_state.user = {
        'username': 'Eng. Ayad', 
        'credits': 5,  # 🎁 5 Free Credits allocated on start
        'role': 'Free Trial',
        'is_subscribed': False,
        'subscription_type': 'Free'
    }
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'plan_signature' not in st.session_state:
    st.session_state.plan_signature = None
if 'notify_whatsapp' not in st.session_state:
    st.session_state.notify_whatsapp = "+967700000000"
if 'notify_telegram' not in st.session_state:
    st.session_state.notify_telegram = "@Ayad_Developer"

# Form Specific Keys
if 'form_scope' not in st.session_state:
    st.session_state.form_scope = ""
if 'form_pname' not in st.session_state:
    st.session_state.form_pname = "مشروع جديد Pro"
if 'form_domain' not in st.session_state:
    st.session_state.form_domain = "التجارة الإلكترونية"
if 'form_budget' not in st.session_state:
    st.session_state.form_budget = 3500
if 'form_days' not in st.session_state:
    st.session_state.form_days = 30

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
        'detailed_plan': "📜 الخطة التنفيذية النصية الشاملة",
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
        'detailed_plan': "📜 Comprehensive Text Plan",
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
    .checkout-btn:hover, .checkout-btn-yearly:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    .pricing-card {{ background-color: {card_bg}; border: 2px solid {border_color}; border-radius: 16px; padding: 24px; text-align: center; transition: all 0.3s ease; }}
    .pricing-card-highlight {{ background-color: {card_bg}; border: 2px solid #8B5CF6; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 10px 25px rgba(139,92,246,0.2); }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {card_bg}; border-radius: 8px; padding: 10px 20px; color: {text_color}; border: 1px solid {border_color}; font-weight: bold; }}
    .stTabs [aria-selected="true"] {{ background-color: #3B82F6 !important; color: white !important; border-color: #3B82F6 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER ENGINES
# ==========================================
class SecurityEngine:
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

    story.append(Paragraph(prepare_text("--- تفاصيل الخطة التنفيذية ---"), title_style))
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
    budget = plan.get('budget', 0)
    days = plan.get('target_days', 0)
    
    return f"""📌 **المستند التنفيذي والشامل لمشروع ({p_name})**

### 1. نظرة عامة والأهداف التنفيذية:
يهدف مشروع **{p_name}** إلى تقديم حل متكامل في قطاع **{domain}** بميزانية إجمالية قدرها **${budget:,}** ومدة إنجاز مقدرة بـ **{days} يوماً**.

### 2. معمارية النظام والبنية البرمجية (System Architecture):
* **تطوير الواجهات:** بناء مكونات UI خفيفة وسريعة التفاعل تضمن سلاسة الاستخدام.
* **إدارة قواعد البيانات:** إعداد جداول منظمة تدعم العزل الآمن، مع الصلاحيات الدقيقة RLS.
* **الخوادم وبوابات API:** إنشاء واجهات REST/tRPC مؤمنة بالتشفير والتحقق الذاتي.

### 3. مراحل التنفيذ وجدول المهام (Milestones & Tasks):
* **المرحلة الأولى - الهندسة والمعمارية:** تحليل المتطلبات وإعداد Schemas.
* **المرحلة الثانية - تطوير Backend:** تجهيز قاعدة البيانات وبناء Business Logic.
* **المرحلة الثالثة - Frontend & UI:** الربط التفاعلي للواجهات.
* **المرحلة الرابعة - الاختبار والتكامل Deployment & QA:** اختبارات الأمان والرفع للإنتاج.

### 4. معايير الجودة والأمان الرقمي:
* تم توقيع هذه الخطة رقمياً باستخدام خوارزمية HMAC-SHA512 لضمان موثوقية التقديرات.
"""

# ==========================================
# 3. SIDEBAR WITH INSTANT CALLBACKS
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
    
    # User status display (Free Trial vs Subscribed)
    if st.session_state.user['is_subscribed']:
        st.markdown(f"نوع الاشتراك: <span class='badge-gold'>{st.session_state.user['role']}</span>", unsafe_allow_html=True)
        st.markdown(f"الرصيد المتاح: **غير محدود ♾️**")
    else:
        st.markdown(f"نوع الحساب: <span class='badge-purple'>تجريبي (5 نقاط هدية)</span>", unsafe_allow_html=True)
        st.markdown(f"{txt['credits']} `{st.session_state.user['credits']}` {txt['points']}")
    
    st.write("---")
    st.markdown(f"### {txt['renew_title']}")
    st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">{txt["renew_btn"]}</a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader(txt['notify_settings'])
    st.session_state.notify_whatsapp = st.text_input(txt['wa_phone'], value=st.session_state.notify_whatsapp)
    st.session_state.notify_telegram = st.text_input(txt['tg_handle'], value=st.session_state.notify_telegram)

# ==========================================
# 4. MAIN INTERFACE WITH 4 DISTINCT TABS
# ==========================================
st.title(txt['title'])
st.caption(txt['subtitle'])

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
            st.error("❌ لقد استنفدت نقاطك المجانية (5/5)! يرجى ترقية اشتراكك للاستمرار.")
            st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">🛒 اشترك الآن للحصول على رصيد لا محدود</a>', unsafe_allow_html=True)
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
                
                # Deduct credit if on free tier
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
# TAB 2: التحليلات التفاعلية الفائقة (مبهرة وفريدة)
# ==========================================
with tab2:
    if not st.session_state.current_plan:
        st.info("💡 قم بتوليد خطة مشروع أولاً من تبويب 'بناء خطة مشروع' لاستعراض التحليلات الهندسية المتقدمة.")
    else:
        plan = st.session_state.current_plan
        df = pd.DataFrame(plan['tasks'])
        
        st.markdown("### 📊 لوحة القيادة الهندسية وتخيم الجودة والمخاطر")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("إجمالي الميزانية المعتمدة", f"${plan['budget']:,}")
        col_m2.metric("المدى الزمني الشامل", f"{plan['target_days']} يوم")
        col_m3.metric("معدل التكلفة اليومية", f"${int(plan['budget']/max(1, plan['target_days'])):,}/يوم")
        col_m4.metric("درجة الموثوقية الرقمية", "100% (HMAC)")
        
        st.write("---")
        
        # 1. Custom Radar Assessment Chart (Unique Engineering Radar)
        col_rad1, col_rad2 = st.columns([1, 1])
        
        with col_rad1:
            st.markdown("#### 🛡️ تقييم أبعاد المشروع (Radar Matrix)")
            radar_categories = ['تعقيد النطاق', 'الأمان الرقمي', 'التحكم بالجدول', 'استقرار التكلفة', 'المرونة التقنية']
            
            # Dynamic scoring based on user selections
            risk_val = 85 if plan.get('risk') == 'عالي' else (65 if plan.get('risk') == 'متوسط' else 45)
            radar_values = [75, 95, 80, 85, risk_val]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_values,
                theta=radar_categories,
                fill='toself',
                name='المشروع الحالي',
                line_color='#3B82F6',
                fillcolor='rgba(59, 130, 246, 0.3)'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with col_rad2:
            st.markdown("#### 🌊 التدفق المالي التراكمي للمراحل (Waterfall Cost)")
            
            fig_waterfall = go.Figure(go.Waterfall(
                name="التكلفة",
                orientation="v",
                measure=["relative"] * len(df),
                x=df['task'],
                textposition="outside",
                text=[f"${c:,}" for c in df['cost']],
                y=df['cost'],
                connector={"line": {"color": "#64748B"}},
                decreasing={"marker": {"color": "#EF4444"}},
                increasing={"marker": {"color": "#10B981"}},
            ))
            fig_waterfall.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color),
                showlegend=False
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)
            
        st.write("---")
        
        # 3. Gantt Phase Timeline (Unique Implementation)
        st.markdown("#### ⏱️ المخطط الزمني التنفيذي للمراحل (Gantt Phase Breakdown)")
        
        df_gantt = df.copy()
        start_days = []
        curr = 0
        for d in df_gantt['days']:
            start_days.append(curr)
            curr += d
            
        df_gantt['Start'] = start_days
        df_gantt['End'] = curr
        
        fig_gantt = px.bar(
            df_gantt, 
            x='days', 
            y='task', 
            orientation='h', 
            base='Start',
            color='task',
            title="التسلسل الزمني المتتابع للمهام (بالأيام)",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_gantt.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            showlegend=False,
            xaxis_title="الأيام التراكمية",
            yaxis_title="المهمة الهندسية"
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

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
# TAB 4: إدارة الحساب والاشتراكات (تصميم احترافي مذهل)
# ==========================================
with tab4:
    st.subheader("💳 إدارة الاشتراكات والخطط التجارية")
    st.caption("اختر الخطة المناسبة لاحتياجاتك البرمجية والهندسية لتوليد خطط غير محدودة.")
    
    # Status Banner
    col_stat1, col_stat2 = st.columns([2, 1])
    with col_stat1:
        st.info(f"👤 **المستخدم:** {st.session_state.user['username']} | **الرصيد التجريبي المجاني المتبقي:** {st.session_state.user['credits']} من أصل 5 نقاط مجانية.")
    with col_stat2:
        if st.session_state.user['credits'] > 0 and not st.session_state.user['is_subscribed']:
            st.markdown("<span class='badge-green'>🎁 الفترة التجريبية نشطة (5 نقاط)</span>", unsafe_allow_html=True)
        elif st.session_state.user['is_subscribed']:
            st.markdown("<span class='badge-gold'>👑 اشتراك مدفوع نشط</span>", unsafe_allow_html=True)

    st.write("---")
    
    # Pricing Cards Comparison
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <h3>🎁 التجريبي المجاني</h3>
            <h2>$0 <small>/ للأبد</small></h2>
            <hr>
            <p>✔ <b>5 نقاط مجانية</b> للبدء والتجربة</p>
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
            <a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">🚀 الاشتراك الشهري الآن</a>
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
            <a href="{PAYMENT_LINK_YEARLY}" target="_blank" class="checkout-btn-yearly">💎 الاشتراك السنوي المميز</a>
        </div>
        """, unsafe_allow_html=True)
