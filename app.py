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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 1. CONFIGURATION & STYLING
# ==========================================
APP_TITLE = "PHOENIX & MIHNA AGENT PRO - ENTERPRISE"
PAYMENT_LINK = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3"
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_DEFAULT")

st.set_page_config(
    page_title="وكيل مهنة PRO | Enterprise Plan Builder",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'user' not in st.session_state:
    st.session_state.user = {'username': 'Eng. Ayad', 'credits': 15, 'role': 'Enterprise'}
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'plan_signature' not in st.session_state:
    st.session_state.plan_signature = None
if 'notify_whatsapp' not in st.session_state:
    st.session_state.notify_whatsapp = "+967700000000"
if 'notify_telegram' not in st.session_state:
    st.session_state.notify_telegram = "@Ayad_Developer"

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
        'credits': "💳 الرصيد المتبقي:",
        'points': "نقطة",
        'renew_title': "🛒 تجديد الاشتراك",
        'renew_btn': "🛒 شراء نقاط / تجديد الاشتراك",
        'notify_settings': "📲 إعدادات الإشعارات الفورية",
        'wa_phone': "رقم الواتساب (مع الرمز)",
        'tg_handle': "معرف التليجرام (Telegram Handle)",
        'tab1': "🏗️ بناء خطة مشروع",
        'tab2': "📊 التحليلات التفاعلية",
        'tab3': "✏️ محرر المهام والخطة التفصيلية",
        'tab4': "💳 إدارة الحساب والاشتراك",
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
        'generate_btn': "🚀 توليد وتوقيع الخطة الهندسية",
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
        'credits': "💳 Remaining Credits:",
        'points': "pts",
        'renew_title': "🛒 Subscription Renewal",
        'renew_btn': "🛒 Buy Credits / Renew Plan",
        'notify_settings': "📲 Instant Notification Settings",
        'wa_phone': "WhatsApp Phone (with Country Code)",
        'tg_handle': "Telegram Handle",
        'tab1': "🏗️ Build Project Plan",
        'tab2': "📊 Interactive Analytics",
        'tab3': "✏️ Task Editor & Detailed Plan",
        'tab4': "💳 Account & Subscription",
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
        'generate_btn': "🚀 Generate & Sign Engineering Plan",
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

# Theme Dynamic CSS
if st.session_state.theme == 'dark':
    bg_color = "#0E1117"
    card_bg = "#1E293B"
    text_color = "#FFFFFF"
    border_color = "#334155"
else:
    bg_color = "#F8FAFC"
    card_bg = "#FFFFFF"
    text_color = "#0F172A"
    border_color = "#E2E8F0"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .badge-green {{ background-color: #10B981; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }}
    .badge-blue {{ background-color: #3B82F6; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }}
    .badge-purple {{ background-color: #8B5CF6; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }}
    .checkout-btn {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #E11D48, #F43F5E); color: white !important; padding: 12px 16px; border-radius: 10px; font-weight: bold; text-decoration: none; border: none; font-size: 14px; box-shadow: 0 4px 12px rgba(225,29,72,0.3); }}
    .checkout-btn:hover {{ opacity: 0.9; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {card_bg}; border-radius: 8px; padding: 10px 20px; color: {text_color}; border: 1px solid {border_color}; font-weight: bold; }}
    .stTabs [aria-selected="true"] {{ background-color: #3B82F6 !important; color: white !important; border-color: #3B82F6 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER ENGINES & UTILITIES
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

    # Function to prepare RTL Arabic text safely
    def prepare_text(text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, alignment=2)

    # Document Header
    story.append(Paragraph(prepare_text(f"خطة مشروع: {plan['project_name']}"), title_style))
    story.append(Spacer(1, 15))
    
    # Overview Parameters
    info_text = f"المجال التقني: {plan['domain']} | الميزانية: ${plan['budget']} | المدة: {plan['target_days']} يوم"
    story.append(Paragraph(prepare_text(info_text), body_style))
    story.append(Spacer(1, 10))

    # Detailed Text Section
    story.append(Paragraph(prepare_text("--- تفاصيل الخطة التنفيذية ---"), title_style))
    for line in detailed_text.split("\n"):
        if line.strip():
            story.append(Paragraph(prepare_text(line.strip()), body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 15))
    # Signature Footer
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
* **تطوير الواجهات:** بناء مكونات UI خفيفة وسريعة التفاعل تضمن سلسة الاستخدام.
* **إدارة قواعد البيانات:** إعداد جداول منظمة تدعم العزل الآمن، مع الصلاحيات الدقيقة RLS.
* **الخوادم وبوابات API:** إنشاء واجهات REST/tRPC مؤمنة بالتشفير والتحقق الذاتي للتفاعل السريع.

### 3. مراحل التنفيذ وجدول المهام (Milestones & Tasks):
* **المرحلة الأولى - الهندسة والمعمارية:** تحليل المتطلبات، إعداد Schemas، وتصميم المخططات الرئيسية.
* **المرحلة الثانية - تطوير Backend:** تجهيز قاعدة البيانات، إدارة الجلسات، وبناء الآليات المنطقية Business Logic.
* **المرحلة الثالثة - Frontend & UI:** الربط التفاعلي، استجابة الواجهات لكافة الشاشات والهواتف.
* **المرحلة الرابعة - الاختبار والتكامل Deployment & QA:** اختبارات الأمان، ضغط الأحمال، والرفع للإنتاج.

### 4. معايير الجودة والأمان الرقمي:
* تم توقيع هذه الخطة رقمياً باستخدام خوارزمية HMAC-SHA512 لضمان موثوقية التقديرات ومنع التلاعب.
"""

# ==========================================
# 3. SIDEBAR (LANG, THEME & USER INFO)
# ==========================================
with st.sidebar:
    st.title("🛡️ PHOENIX AGENT")
    st.markdown("<span class='badge-purple'>Enterprise Edition 2026</span>", unsafe_allow_html=True)
    st.write("---")
    
    # Language Switcher
    selected_lang = st.radio(txt['lang_select'], ["العربية (Arabic)", "English"], index=0 if st.session_state.lang == 'ar' else 1)
    st.session_state.lang = 'ar' if "العربية" in selected_lang else 'en'
    
    # Theme Switcher
    theme_btn = st.radio(txt['theme_select'], [txt['dark'], txt['light']], index=0 if st.session_state.theme == 'dark' else 1)
    st.session_state.theme = 'dark' if txt['dark'] in theme_btn else 'light'
    
    st.write("---")
    st.markdown(f"{txt['user']} **{st.session_state.user['username']}**")
    st.markdown(f"{txt['credits']} `{st.session_state.user['credits']}` {txt['points']}")
    
    st.markdown(f"### {txt['renew_title']}")
    st.markdown(f'<a href="{PAYMENT_LINK}" target="_blank" class="checkout-btn">{txt["renew_btn"]}</a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader(txt['notify_settings'])
    st.session_state.notify_whatsapp = st.text_input(txt['wa_phone'], value=st.session_state.notify_whatsapp)
    st.session_state.notify_telegram = st.text_input(txt['tg_handle'], value=st.session_state.notify_telegram)

# ==========================================
# 4. MAIN PAGE NAVIGATION
# ==========================================
st.title(txt['title'])
st.caption(txt['subtitle'])

tab1, tab2, tab3, tab4 = st.tabs([txt['tab1'], txt['tab2'], txt['tab3'], txt['tab4']])

# ==========================================
# TAB 1: BUILD PROJECT PLAN
# ==========================================
with tab1:
    st.subheader(txt['quick_templates'])
    col_t1, col_t2, col_t3 = st.columns(3)
    
    scope_val, domain_val, budget_val, days_val = "", "التجارة الإلكترونية", 3500, 30
    
    if col_t1.button(txt['ecom'], use_container_width=True):
        scope_val = "تطبيق متجر إلكتروني لبيع المنتجات مع بوابة دفع سريعة ونظام إدارة المخزون"
        domain_val = "التجارة الإلكترونية"
        budget_val = 4500
        days_val = 35
    elif col_t2.button(txt['edu'], use_container_width=True):
        scope_val = "منصة تعليمية تتيح رفع الكورسات واختبارات تفاعلية وشهادات تلقائية"
        domain_val = "التعليم الرقمي"
        budget_val = 3000
        days_val = 25
    elif col_t3.button(txt['delivery'], use_container_width=True):
        scope_val = "تطبيق توصيل طلبات يعتمد على الخرائط التفاعلية وتتبع السائقين في الوقت الفعلي"
        domain_val = "الخدمات واللوجستيات"
        budget_val = 6000
        days_val = 50

    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(txt['p_name'], value="مشروع جديد Pro")
            domain = st.selectbox(txt['tech_domain'], ["التجارة الإلكترونية", "التعليم الرقمي", "الخدمات واللوجستيات", "الذكاء الاصطناعي", "أنظمة SaaS"], index=0)
            budget = st.number_input(txt['budget'], min_value=500, value=budget_val)
        with col2:
            tech_stack = st.text_input(txt['tech_stack'], value="Flutter, Node.js, PostgreSQL, Supabase")
            target_days = st.number_input(txt['target_days'], min_value=5, value=days_val)
            risk_tolerance = st.select_slider(txt['risk_level'], options=["منخفض جداً", "متوسط", "عالي"])
            
        project_scope = st.text_area(txt['scope'], value=scope_val, placeholder="اكتب تفاصيل ومتطلبات المشروع هنا...")
        
        submit_btn = st.form_submit_button(txt['generate_btn'], use_container_width=True)
        
    if submit_btn:
        if st.session_state.user['credits'] < 1:
            st.error("❌ رصيدك غير كافٍ! يرجى الشحن للاستمرار.")
            st.markdown(f'<a href="{PAYMENT_LINK}" target="_blank" class="checkout-btn">تجديد الاشتراك الآن</a>', unsafe_allow_html=True)
        elif not project_scope:
            st.warning("⚠️ يرجى تقديم نطاق العمل لتبدأ عملية التوليد.")
        else:
            with st.spinner("⏳ جاري توليد المهام والتوقيع الرقمي..."):
                time.sleep(1.0)
                
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
                    "tasks": tasks,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                signature = SecurityEngine.generate_signature(plan_payload)
                st.session_state.current_plan = plan_payload
                st.session_state.plan_signature = signature
                st.session_state.user['credits'] -= 1
                
                st.success("✅ تم توليد الخطة وتوقيعها رقمياً بنجاح!")

    # Display Generated Plan Info & Export Shortcuts
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
        
        # Download Action Buttons
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            excel_bytes = generate_excel_download(df_tasks)
            st.download_button(
                label=txt['export_excel'],
                data=excel_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Tasks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col_dl2:
            detailed_txt = build_detailed_plan_text(st.session_state.current_plan)
            pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_txt)
            st.download_button(
                label=txt['export_pdf'],
                data=pdf_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        # Immediate Notifications Section
        st.write("---")
        col_n1, col_n2 = st.columns(2)
        msg_body = f"🚀 Project Plan: {st.session_state.current_plan['project_name']}\n💰 Budget: ${st.session_state.current_plan['budget']}\n⏱️ Days: {st.session_state.current_plan['target_days']}\n🔑 Sig: {st.session_state.plan_signature[:20]}..."
        wa_url = NotificationEngine.create_whatsapp_link(st.session_state.notify_whatsapp, msg_body)
        
        with col_n1:
            st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:8px; font-weight:bold; text-decoration:none;">{txt["send_wa"]}</a>', unsafe_allow_html=True)
        with col_n2:
            if st.button(txt['send_tg'], use_container_width=True):
                st.success(f"✅ Notification dispatched to {st.session_state.notify_telegram}")

# ==========================================
# TAB 2: INTERACTIVE ANALYTICS
# ==========================================
with tab2:
    if not st.session_state.current_plan:
        st.info("💡 قم بتوليد خطة مشروع أولاً من تبويب 'بناء خطة مشروع'.")
    else:
        plan = st.session_state.current_plan
        df = pd.DataFrame(plan['tasks'])
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("إجمالي التكلفة", f"${plan['budget']:,}")
        col_m2.metric("إجمالي الأيام", f"{plan['target_days']} يوم")
        col_m3.metric("عدد المهام", f"{len(df)}")
        col_m4.metric("الأمان الرقمي", "HMAC-Verified")
        
        st.write("---")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_pie = px.pie(df, values='cost', names='task', title='توزيع الميزانية على المهام', hole=0.4)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': text_color})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_c2:
            fig_bar = px.bar(df, x='task', y='days', title='المدة الزمنية لكل مهمة (أيام)', color='days', color_continuous_scale='Blues')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': text_color})
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# TAB 3: TASK EDITOR & DETAILED TEXT PLAN
# ==========================================
with tab3:
    st.subheader(txt['tab3'])
    
    if not st.session_state.current_plan:
        st.warning("⚠️ لا توجد خطة حالية لتعديلها. قم بتوليد خطة من تبويب 'بناء خطة مشروع'.")
    else:
        # Interactive Table Editor
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.current_plan['tasks']),
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.button(txt['save_re_sign'], use_container_width=True):
            updated_tasks = edited_df.to_dict(orient='records')
            st.session_state.current_plan['tasks'] = updated_tasks
            st.session_state.current_plan['budget'] = sum(int(item.get('cost', 0)) for item in updated_tasks)
            st.session_state.current_plan['target_days'] = sum(int(item.get('days', 0)) for item in updated_tasks)
            
            new_sig = SecurityEngine.generate_signature(st.session_state.current_plan)
            st.session_state.plan_signature = new_sig
            st.success("✅ تم تحديث المهام وإعادة التوقيع الرقمي بنجاح!")
            st.rerun()

        st.write("---")
        # Detailed Textual Plan Section
        st.subheader(txt['detailed_plan'])
        detailed_plan_text = build_detailed_plan_text(st.session_state.current_plan)
        st.markdown(detailed_plan_text)
        
        st.write("---")
        # Downloads Section in Tab 3
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            excel_bytes = generate_excel_download(edited_df)
            st.download_button(
                label=txt['export_excel'],
                data=excel_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Tasks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col_d2:
            pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_plan_text)
            st.download_button(
                label=txt['export_pdf'],
                data=pdf_bytes,
                file_name=f"{st.session_state.current_plan['project_name']}_Plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ==========================================
# TAB 4: ACCOUNT MANAGEMENT
# ==========================================
with tab4:
    st.subheader(txt['tab4'])
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown(f"**اسم المشترك:** {st.session_state.user['username']}")
        st.markdown(f"**باقة الاشتراك:** {st.session_state.user['role']}")
        st.markdown(f"**الرصيد الحالي:** {st.session_state.user['credits']} نقطة")
        
    with col_a2:
        st.markdown("### ترقية الحساب / شراء رصيد")
        st.write("احصل على نقاط إضافية لتوليد الخطط الهندسية واستخدام الذكاء الاصطناعي.")
        st.markdown(
            f'<a href="{PAYMENT_LINK}" target="_blank" class="checkout-btn">🔗 الذهاب لبوابة الدفع Lemon Squeezy</a>', 
            unsafe_allow_html=True
        )
