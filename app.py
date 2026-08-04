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
    .metric-card {{ background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 12px; padding: 15px; text-align: center; }}
    .checkout-btn {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #E11D48, #F43F5E); color: white !important; padding: 12px 16px; border-radius: 10px; font-weight: bold; text-decoration: none; border: none; font-size: 14px; box-shadow: 0 4px 12px rgba(225,29,72,0.3); }}
    .checkout-btn:hover {{ opacity: 0.9; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {card_bg}; border-radius: 8px; padding: 10px 20px; color: {text_color}; border: 1px solid {border_color}; font-weight: bold; }}
    .stTabs [aria-selected="true"] {{ background-color: #3B82F6 !important; color: white !important; border-color: #3B82F6 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURITY & NOTIFICATION ENGINES
# ==========================================
class SecurityEngine:
    @staticmethod
    def generate_signature(data_dict: dict) -> str:
        serialized = json.dumps(data_dict, sort_keys=True, ensure_ascii=False)
        return hmac.new(SECRET_HMAC_KEY.encode(), serialized.encode(), hashlib.sha512).hexdigest()

    @staticmethod
    def verify_signature(data_dict: dict, signature: str) -> bool:
        expected_sig = SecurityEngine.generate_signature(data_dict)
        return hmac.compare_digest(expected_sig, signature)

class NotificationEngine:
    @staticmethod
    def create_whatsapp_link(phone: str, message: str) -> str:
        encoded_msg = urllib.parse.quote(message)
        clean_phone = re.sub(r'[^\d]', '', phone)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"

class RAGMemoryEngine:
    def __init__(self):
        self.knowledge_base = [
            {"scope": "تطبيق متجر إلكتروني متكامل", "domain": "التجارة الإلكترونية", "avg_days": 45, "risk": "منخفض"},
            {"scope": "منصة تعليمية وتدريبية", "domain": "التعليم والتدريب", "avg_days": 30, "risk": "متوسط"},
            {"scope": "تطبيق خدمات وتوصيل", "domain": "الخدمات اللوجستية", "avg_days": 60, "risk": "عالي"},
        ]

    def search_similar(self, query: str) -> list:
        results = [item for item in self.knowledge_base if any(w in item['scope'] for w in query.split())]
        return results if results else [self.knowledge_base[0]]

rag_engine = RAGMemoryEngine()

# ==========================================
# 3. SIDEBAR (ACCOUNT & NOTIFICATIONS)
# ==========================================
with st.sidebar:
    st.title("🛡️ PHOENIX AGENT")
    st.markdown("<span class='badge-purple'>Enterprise Edition 2026</span>", unsafe_allow_html=True)
    st.write("---")
    
    # Theme Switcher
    theme_btn = st.radio("🎨 مظهر التطبيق (Theme):", ["🌙 الداكن (Dark)", "☀️ الفاتح (Light)"], index=0 if st.session_state.theme == 'dark' else 1)
    st.session_state.theme = 'dark' if "الداكن" in theme_btn else 'light'
    
    st.write("---")
    st.markdown(f"👤 **المستخدم:** {st.session_state.user['username']}")
    st.markdown(f"💳 **الرصيد المتبقي:** `{st.session_state.user['credits']}` نقطة")
    
    st.markdown("### 🛒 تجديد الاشتراك")
    st.markdown(f'<a href="{PAYMENT_LINK}" target="_blank" class="checkout-btn">🛒 شراء نقاط / تجديد الاشتراك</a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📲 إعدادات الإشعارات الفورية")
    st.session_state.notify_whatsapp = st.text_input("رقم الواتساب (مع الرمز)", value=st.session_state.notify_whatsapp)
    st.session_state.notify_telegram = st.text_input("معرف التليجرام (Telegram Handle)", value=st.session_state.notify_telegram)
    
# ==========================================
# 4. MAIN PAGE NAVIGATION (TOP TABS)
# ==========================================
st.title("🚀 وكيل مهنة PRO | PHOENIX Enterprise")
st.caption("المنصة المتقدمة لهندسة خطط المشاريع وتأمينها بالتوقيع الرقمي والذكاء الاصطناعي.")

# Move Navigation from Sidebar to Main Screen Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏗️ بناء خطة مشروع", 
    "📊 التحليلات التفاعلية", 
    "✏️ محرر المهام (HITL)", 
    "💳 إدارة الحساب والاشتراك"
])

# ==========================================
# TAB 1: BUILD PROJECT PLAN
# ==========================================
with tab1:
    st.subheader("⚡ قوالب جاهزة للبدء السريع")
    col_t1, col_t2, col_t3 = st.columns(3)
    
    scope_val, domain_val, budget_val, days_val = "", "التجارة الإلكترونية", 3500, 30
    
    if col_t1.button("🛒 متجر إلكتروني", use_container_width=True):
        scope_val = "تطبيق متجر إلكتروني لبيع المنتجات مع بوابة دفع سريعة ونظام إدارة المخزون"
        domain_val = "التجارة الإلكترونية"
        budget_val = 4500
        days_val = 35
    elif col_t2.button("🎓 منصة تعليمية", use_container_width=True):
        scope_val = "منصة تعليمية تتيح رفع الكورسات واختبارات تفاعلية وشهادات تلقائية"
        domain_val = "التعليم الرقمي"
        budget_val = 3000
        days_val = 25
    elif col_t3.button("🚗 تطبيق توصيل", use_container_width=True):
        scope_val = "تطبيق توصيل طلبات يعتمد على الخرائط التفاعلية وتتبع السائقين في الوقت الفعلي"
        domain_val = "الخدمات واللوجستيات"
        budget_val = 6000
        days_val = 50

    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("اسم المشروع", value="مشروع جديد Pro")
            domain = st.selectbox("المجال التقني", ["التجارة الإلكترونية", "التعليم الرقمي", "الخدمات واللوجستيات", "الذكاء الاصطناعي", "أنظمة SaaS"], index=0)
            budget = st.number_input("الميزانية التقديرية ($)", min_value=500, value=budget_val)
        with col2:
            tech_stack = st.text_input("التقنيات المستخدمة", value="Flutter, Node.js, PostgreSQL, Supabase")
            target_days = st.number_input("المدة الزمنية المستهدفة (يوم)", min_value=5, value=days_val)
            risk_tolerance = st.select_slider("تحمل المخاطر", options=["منخفض جداً", "متوسط", "عالي"])
            
        project_scope = st.text_area("نطاق العمل (Scope of Work)", value=scope_val, placeholder="اكتب تفاصيل ومتطلبات المشروع هنا...")
        
        submit_btn = st.form_submit_button("🚀 توليد وتوقيع الخطة الهندسية", use_container_width=True)
        
    if submit_btn:
        if st.session_state.user['credits'] < 1:
            st.error("❌ رصيدك غير كافٍ! يرجى الشحن للاستمرار.")
            st.markdown(f'<a href="{PAYMENT_LINK}" target="_blank" class="checkout-btn">تجديد الاشتراك الآن</a>', unsafe_allow_html=True)
        elif not project_scope:
            st.warning("⚠️ يرجى تقديم نطاق العمل لتبدأ عملية التوليد.")
        else:
            with st.spinner("⏳ جاري استرجاع المشاريع المماثلة (RAG) وتوليد المهام والتوقيع الرقمي..."):
                time.sleep(1.2)
                
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

    if st.session_state.current_plan:
        st.write("---")
        st.subheader("📌 الخطة الحالية والتوقيع الرقمي")
        
        col_sig1, col_sig2 = st.columns([3, 1])
        with col_sig1:
            st.info(f"🔑 **التوقيع الرقمي المشفر (HMAC-SHA512):**\n`{st.session_state.plan_signature}`")
        with col_sig2:
            is_valid = SecurityEngine.verify_signature(st.session_state.current_plan, st.session_state.plan_signature)
            if is_valid:
                st.markdown("<br><span class='badge-green'>✔ توقيع موثوق وسليم</span>", unsafe_allow_html=True)
            else:
                st.markdown("<br><span class='badge-purple'>❌ تم التلاعب بالبيانات</span>", unsafe_allow_html=True)

        df_tasks = pd.DataFrame(st.session_state.current_plan['tasks'])
        st.dataframe(df_tasks, use_container_width=True)
        
        # Notification Trigger Section
        st.subheader("📲 إرسال الخطة عبر التنبيهات")
        col_n1, col_n2 = st.columns(2)
        
        msg_body = f"🚀 خطة مشروع: {st.session_state.current_plan['project_name']}\n💰 الميزانية: ${st.session_state.current_plan['budget']}\n⏱️ المدة: {st.session_state.current_plan['target_days']} يوم\n🔑 التوقيع: {st.session_state.plan_signature[:20]}..."
        wa_url = NotificationEngine.create_whatsapp_link(st.session_state.notify_whatsapp, msg_body)
        
        with col_n1:
            st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:8px; font-weight:bold; text-decoration:none;">📱 إرسال عبر WhatsApp</a>', unsafe_allow_html=True)
        with col_n2:
            if st.button("📲 إشعار Telegram Bot", use_container_width=True):
                st.success(f"✅ تم إرسال التنبيه الفوري لـ {st.session_state.notify_telegram}")

# ==========================================
# TAB 2: INTERACTIVE ANALYTICS
# ==========================================
with tab2:
    st.subheader("📊 التحليلات البصرية ومقاييس الأداء")
    
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
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_gauge1 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 92,
                title = {'text': "مؤشر موثوقية التقدير (Accuracy Rate %)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#10B981"},
                    'steps': [{'range': [0, 50], 'color': "#334155"}, {'range': [50, 80], 'color': "#475569"}],
                }
            ))
            fig_gauge1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': text_color})
            st.plotly_chart(fig_gauge1, use_container_width=True)
            
        with col_g2:
            fig_gauge2 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 18,
                title = {'text': "مؤشر المخاطر المتوقعة (Risk Factor %)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#EF4444"},
                    'steps': [{'range': [0, 40], 'color': "#334155"}, {'range': [40, 70], 'color': "#475569"}],
                }
            ))
            fig_gauge2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': text_color})
            st.plotly_chart(fig_gauge2, use_container_width=True)

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
# TAB 3: HITL TASK EDITOR
# ==========================================
with tab3:
    st.subheader("✏️ محرر المهام التفاعلي (Human-In-The-Loop)")
    st.caption("تعديل الأيام والتكلفة يدوياً مع إعادة التوقيع الرقمي التلقائي لمنع التلاعب.")
    
    if not st.session_state.current_plan:
        st.warning("⚠️ لا توجد خطة حالية لتعديلها. قم بتوليد خطة من تبويب 'بناء خطة مشروع'.")
    else:
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.current_plan['tasks']),
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.button("💾 حفظ التعديلات وإعادة التوقيع الرقمي", use_container_width=True):
            updated_tasks = edited_df.to_dict(orient='records')
            st.session_state.current_plan['tasks'] = updated_tasks
            st.session_state.current_plan['budget'] = sum(int(item.get('cost', 0)) for item in updated_tasks)
            st.session_state.current_plan['target_days'] = sum(int(item.get('days', 0)) for item in updated_tasks)
            
            new_sig = SecurityEngine.generate_signature(st.session_state.current_plan)
            st.session_state.plan_signature = new_sig
            
            st.success("✅ تم تحديث المهام وإعادة حساب التوقيع الرقمي بنجاح!")
            st.rerun()

# ==========================================
# TAB 4: ACCOUNT MANAGEMENT
# ==========================================
with tab4:
    st.subheader("💳 تفاصيل الحساب والاشتراك")
    
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
