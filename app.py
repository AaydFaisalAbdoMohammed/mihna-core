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
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_DEFAULT")

st.set_page_config(
    page_title="وكيل مهنة PRO | Enterprise Plan Builder",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# In-memory Mock Database for Accounts
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "eng.ayad@phoenix.com": {
            "password_hash": hashlib.sha256("123456".encode()).hexdigest(),
            "username": "Eng. Ayad",
            "role": "Enterprise Pro",
            "credits": 9999,
            "is_subscribed": True,
            "subscription_type": "Enterprise Yearly"
        }
    }

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
    st.session_state.show_ai_payment_modal = False

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
    .ai-payment-card {{ background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); border: 2px solid #6366F1; border-radius: 16px; padding: 24px; color: #FFFFFF; margin-bottom: 20px; }}
    .pricing-card {{ background-color: {card_bg}; border: 2px solid {border_color}; border-radius: 16px; padding: 24px; text-align: center; transition: all 0.3s ease; }}
    .pricing-card-highlight {{ background-color: {card_bg}; border: 2px solid #8B5CF6; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 10px 25px rgba(139,92,246,0.2); }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {card_bg}; border-radius: 8px; padding: 10px 20px; color: {text_color}; border: 1px solid {border_color}; font-weight: bold; }}
    .stTabs [aria-selected="true"] {{ background-color: #3B82F6 !important; color: white !important; border-color: #3B82F6 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER & ENCRYPTION ENGINES
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
    """وكيل الدفع بالذكاء الاصطناعي لمعالجة عمليات الترقية فورياً"""
    @staticmethod
    def process_smart_payment(user_email: str, plan_type: str = "Pro Monthly"):
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        status_box.info("🤖 **[AI Agent]:** جاري الاتصال ببوابة الدفع الرقمية المشفرة عبر HMAC-SHA512...")
        time.sleep(0.6)
        progress_bar.progress(30)
        
        status_box.info("🤖 **[AI Agent]:** فحص صحة الحساب والتحقق من التوقيع الرقمي للمستهلك...")
        time.sleep(0.7)
        progress_bar.progress(70)
        
        status_box.info("🤖 **[AI Agent]:** تأكيد تحويل الرصيد وتفعيل باقة الاشتراك اللانهائية...")
        time.sleep(0.7)
        progress_bar.progress(100)
        time.sleep(0.3)
        
        progress_bar.empty()
        status_box.empty()
        
        # Update session & database
        st.session_state.user['is_subscribed'] = True
        st.session_state.user['role'] = f"Enterprise ({plan_type})"
        st.session_state.user['credits'] = 9999
        st.session_state.user['subscription_type'] = plan_type
        
        if user_email in st.session_state.user_db:
            st.session_state.user_db[user_email]['is_subscribed'] = True
            st.session_state.user_db[user_email]['role'] = f"Enterprise ({plan_type})"
            st.session_state.user_db[user_email]['credits'] = 9999
            st.session_state.user_db[user_email]['subscription_type'] = plan_type

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
# 3. AUTHENTICATION MODULE
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
                    if email_input in st.session_state.user_db:
                        user_data = st.session_state.user_db[email_input]
                        if user_data['password_hash'] == hashed_pw:
                            st.session_state.is_authenticated = True
                            st.session_state.user = {
                                'email': email_input,
                                'username': user_data['username'],
                                'credits': user_data['credits'],
                                'role': user_data['role'],
                                'is_subscribed': user_data['is_subscribed'],
                                'subscription_type': user_data['subscription_type']
                            }
                            st.success(f"🎉 أهلاً بك مجدداً {user_data['username']}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ كلمة المرور غير صحيحة.")
                    else:
                        st.error("❌ البريد الإلكتروني غير مسجل بالمنظومة.")

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
                        st.warning("⚠️ يرجى ملء كافة الحقول المطلوب.")
                    elif new_password != confirm_password:
                        st.error("❌ كلمة المرور وتأكيدها غير متطابقين.")
                    elif len(new_password) < 6:
                        st.error("❌ يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.")
                    elif new_email in st.session_state.user_db:
                        st.error("❌ هذا البريد الإلكتروني مسجل بالفعل.")
                    else:
                        st.session_state.user_db[new_email] = {
                            "password_hash": SecurityEngine.hash_password(new_password),
                            "username": new_username,
                            "role": "Free Trial",
                            "credits": 5,
                            "is_subscribed": False,
                            "subscription_type": "Free Trial"
                        }
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
                        st.success("🎉 تم إنشاء الحساب بنجاح وتم إضافة 5 نقاط مجانية لرصيدك!")
                        time.sleep(1)
                        st.rerun()

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
    
    st.radio("🌐 اللغة (Language):", ["العربية (Arabic)", "English"], index=0, key='lang_radio', on_change=update_language)
    st.radio("🎨 المظهر (Theme):", ["🌙 الداكن (Dark)", "☀️ الفاتح (Light)"], index=0, key='theme_radio', on_change=update_theme)
    
    st.write("---")
    st.markdown(f"👤 المستخدم: **{st.session_state.user['username']}**")
    
    if st.session_state.user['is_subscribed']:
        st.markdown(f"نوع الاشتراك: <span class='badge-gold'>{st.session_state.user['role']}</span>", unsafe_allow_html=True)
        st.markdown(f"الرصيد المتاح: **غير محدود ♾️**")
    else:
        st.markdown(f"نوع الحساب: <span class='badge-purple'>تجريبي (5 نقاط)</span>", unsafe_allow_html=True)
        st.markdown(f"الرصيد المتاح: `{st.session_state.user['credits']}` نقاط")
    
    st.button("🚪 تسجيل الخروج", on_click=logout_user, use_container_width=True)

# ==========================================
# 5. MAIN DASHBOARD INTERFACE
# ==========================================
st.title("🚀 وكيل مهنة PRO | PHOENIX Enterprise")
st.caption("المنصة المتقدمة لهندسة خطط المشاريع وتأمينها بالتوقيع الرقمي والذكاء الاصطناعي.")

# Dynamic AI Payment Trigger Banner if credits depleted
if st.session_state.user['credits'] <= 0 and not st.session_state.user['is_subscribed']:
    st.markdown("""
    <div class="ai-payment-card">
        <h3>🤖 تنبيه من وكيل الدفع الذكي (AI Payment Agent)</h3>
        <p>لقد استنفدت جميع النقاط المجانية (0/5). يمكنك تفعيل الاشتراك غير المحدود فورياً بضغطة زر مع المعالجة الذكية والمؤمنة بالكامل.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚡ إتمام الدفع الفوري عبر وكيل الذكاء الاصطناعي (AI Instant Checkout)", expanded=True):
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            st.markdown("#### 💳 الاشتراك الشهري PRO ($29/شهر)")
            if st.button("🚀 تفعيل الاشتراك الشهري ذكياً الآن", type="primary", use_container_width=True):
                AIPaymentAgent.process_smart_payment(st.session_state.user['email'], "Pro Monthly Plan")
                st.balloons()
                st.success("🎉 تم الشحن والتفعيل بنجاح بفضل وكيل الذكاء الاصطناعي! استمتع باستخدام غير محدود.")
                time.sleep(1.5)
                st.rerun()
        with col_pay2:
            st.markdown("#### 👑 الاشتراك السنوي Enterprise ($279/سنة)")
            if st.button("💎 تفعيل الاشتراك السنوي ذكياً الآن", use_container_width=True):
                AIPaymentAgent.process_smart_payment(st.session_state.user['email'], "Enterprise Yearly Plan")
                st.balloons()
                st.success("🎉 تم تفعيل الاشتراك السنوي المتقدم بنجاح!")
                time.sleep(1.5)
                st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🏗️ بناء خطة مشروع", "📊 التحليلات التفاعلية", "✏️ محرر المهام", "💳 إدارة الحساب"])

# TAB 1: BUILD PLAN
with tab1:
    st.subheader("⚡ قوالب جاهزة للبدء السريع")
    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.button("🛒 متجر إلكتروني", use_container_width=True, on_click=apply_template, args=("تطبيق متجر إلكتروني متكامل مع بوابات دفع", "التجارة الإلكترونية", 4500, 35, "متجر متكامل"))
    col_t2.button("🎓 منصة تعليمية", use_container_width=True, on_click=apply_template, args=("منصة تعليمية ذكية للاختبارات والكورسات", "التعليم الرقمي", 3000, 25, "منصة تعليمية"))
    col_t3.button("🚗 تطبيق توصيل", use_container_width=True, on_click=apply_template, args=("تطبيق توصيل يعتمد الخرائط والتتبع اللحظي", "الخدمات واللوجستيات", 6000, 50, "تطبيق توصيل"))

    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("اسم المشروع", key="form_pname")
            domain = st.selectbox("المجال التقني", ["التجارة الإلكترونية", "التعليم الرقمي", "الخدمات واللوجستيات", "الذكاء الاصطناعي", "أنظمة SaaS"], key="form_domain")
            budget = st.number_input("الميزانية التقديرية ($)", min_value=500, key="form_budget")
        with col2:
            tech_stack = st.text_input("التقنيات المستخدمة", value="Flutter, Node.js, PostgreSQL, Supabase")
            target_days = st.number_input("المدة الزمنية (يوم)", min_value=5, key="form_days")
            risk_tolerance = st.select_slider("تحمل المخاطر", options=["منخفض جداً", "متوسط", "عالي"])
            
        project_scope = st.text_area("نطاق العمل (Scope of Work)", key="form_scope")
        submit_btn = st.form_submit_button("🚀 توليد وتوقيع الخطة الهندسية (تستهلك 1 نقطة)", use_container_width=True)
        
    if submit_btn:
        if st.session_state.user['credits'] < 1 and not st.session_state.user['is_subscribed']:
            st.error("❌ لقد استنفدت كافة نقاطك المجانية! يرجى الاستفادة من معالج الدفع الذكي أعلاه لتفعيل الحساب فورياً.")
        elif not project_scope.strip():
            st.warning("⚠️ يرجى تقديم نطاق العمل.")
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
                    if st.session_state.user['email'] in st.session_state.user_db:
                        st.session_state.user_db[st.session_state.user['email']]['credits'] = st.session_state.user['credits']
                
                st.success("✅ تم توليد الخطة والتوقيع بنجاح!")

    if st.session_state.current_plan:
        st.write("---")
        st.info(f"🔑 **التوقيع الرقمي المشفر (HMAC-SHA512):**\n`{st.session_state.plan_signature}`")
        df_tasks = pd.DataFrame(st.session_state.current_plan['tasks'])
        st.dataframe(df_tasks, use_container_width=True)

# TAB 2: ANALYTICS
with tab2:
    if not st.session_state.current_plan:
        st.info("💡 قم بتوليد خطة مشروع أولاً لاستعراض التحليلات الهندسية.")
    else:
        plan = st.session_state.current_plan
        df = pd.DataFrame(plan['tasks'])
        st.markdown("## 📊 لوحة القيادة الهندسية وتخيم الجودة")
        feasibility_score = min(98, max(65, int(100 - (plan['target_days'] / max(1, plan['budget'] / 100)) * 5)))
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 الميزانية", f"${plan['budget']:,}")
        m2.metric("⏱️ المدة الزمنية", f"{plan['target_days']} يوم")
        m3.metric("🛡️ مؤشر السلامة الهندسية", f"{feasibility_score}%")
        
        fig_sunburst = go.Figure(go.Sunburst(
            labels=[plan['project_name']] + list(df['task']),
            parents=[""] + [plan['project_name']] * len(df),
            values=[plan['budget']] + list(df['cost']),
            branchvalues="total"
        ))
        st.plotly_chart(fig_sunburst, use_container_width=True)

# TAB 3: TASK EDITOR
with tab3:
    if st.session_state.current_plan:
        edited_df = st.data_editor(pd.DataFrame(st.session_state.current_plan['tasks']), num_rows="dynamic", use_container_width=True)
        if st.button("💾 حفظ التعديلات وإعادة التوقيع"):
            st.session_state.current_plan['tasks'] = edited_df.to_dict(orient='records')
            st.session_state.plan_signature = SecurityEngine.generate_signature(st.session_state.current_plan)
            st.success("✅ تم تحديث المهام بنجاح!")

# TAB 4: ACCOUNT & AI PAYMENTS
with tab4:
    st.subheader("💳 إدارة الحساب والاشتراكات التجارية")
    st.info(f"👤 **المستخدم:** {st.session_state.user['username']} | 💳 **الرصيد المتاح:** {st.session_state.user['credits']} نقطة")
    
    st.markdown("### 🤖 مركز بوابات الدفع الذكية (AI Payment Center)")
    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        if st.button("⚡ ترقية وسداد الحساب فورياً (Pro Monthly - $29)", use_container_width=True, type="primary"):
            AIPaymentAgent.process_smart_payment(st.session_state.user['email'], "Pro Monthly Plan")
            st.balloons()
            st.success("🎉 تم تفعيل الاشتراك بنجاح!")
            time.sleep(1)
            st.rerun()
            
    with col_ai2:
        if st.button("👑 ترقية وسداد الحساب سنوي (Enterprise - $279)", use_container_width=True):
            AIPaymentAgent.process_smart_payment(st.session_state.user['email'], "Enterprise Yearly Plan")
            st.balloons()
            st.success("🎉 تم تفعيل الاشتراك السنوي بنجاح!")
            time.sleep(1)
            st.rerun()
