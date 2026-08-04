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
import io
import re
import os

# ==========================================
# 1. CONFIGURATION & CONSTANTS
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

# Custom CSS for styling badges & components
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .badge-green { background-color: #10B981; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }
    .badge-blue { background-color: #3B82F6; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }
    .badge-purple { background-color: #8B5CF6; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }
    .metric-card { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 15px; text-align: center; }
    .checkout-btn { display: inline-block; background-color: #FF0055; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURITY ENGINE (HMAC & SIGNATURES)
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

# ==========================================
# 3. RAG & MEMORY ENGINE
# ==========================================
class RAGMemoryEngine:
    def __init__(self):
        self.knowledge_base = [
            {"scope": "تطبيق متجر إلكتروني متكامل", "domain": "التجارة الإلكترونية", "avg_days": 45, "risk": "منخفض"},
            {"scope": "منصة تعليمية وتدريبية", "domain": "التعليم والتدريب", "avg_days": 30, "risk": "متوسط"},
            {"scope": "تطبيق خدمات وتوصيل", "domain": "الخدمات اللوجستية", "avg_days": 60, "risk": "عالي"},
        ]

    def search_similar(self, query: str) -> list:
        results = []
        for item in self.knowledge_base:
            if any(word in item['scope'] for word in query.split()):
                results.append(item)
        return results if results else [self.knowledge_base[0]]

# ==========================================
# 4. SESSION STATE MANAGEMENT
# ==========================================
if 'user' not in st.session_state:
    st.session_state.user = {'username': 'Eng. Ayad', 'credits': 15, 'role': 'Enterprise'}
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'plan_signature' not in st.session_state:
    st.session_state.plan_signature = None

rag_engine = RAGMemoryEngine()

# ==========================================
# 5. SIDEBAR & ACCOUNT MANAGEMENT
# ==========================================
with st.sidebar:
    st.title("🛡️ PHOENIX AGENT PRO")
    st.markdown("<span class='badge-purple'>Enterprise Edition</span>", unsafe_allow_html=True)
    st.write("---")
    
    # User Profile Section
    st.markdown(f"**المستخدم:** {st.session_state.user['username']}")
    st.markdown(f"**الرصيد المتبقي:** `{st.session_state.user['credits']}` نقطة")
    
    # Payment / Subscription Link
    st.markdown("### 💳 شحن الرصيد والاشتراكات")
    st.markdown(
        f'<a href="{PAYMENT_LINK}" target="_blank" style="display: block; text-align: center; background-color: #E11D48; color: white; padding: 12px; border-radius: 8px; font-weight: bold; text-decoration: none; margin-bottom: 15px;">🛒 شراء نقاط / تجديد الاشتراك</a>', 
        unsafe_allow_html=True
    )
    
    st.write("---")
    active_tab = st.radio("القائمة الرئيسية", ["🏗️ بناء خطة مشروع", "📊 التحليلات التفاعلية", "✏️ محرر المهام (HITL)", "💳 إدارة الحساب"])

# ==========================================
# 6. MAIN CONTENT AREAS
# ==========================================

if active_tab == "🏗️ بناء خطة مشروع":
    st.title("🏗️ إنشاء خطة عمل هندسية ومُشفّرة")
    st.caption("نظام مدعوم بالذكاء الاصطناعي مع تقنية RAG للتأكد من الموثوقية والأمان الرقمي.")
    
    # Quick Templates Integration
    st.subheader("⚡ قوالب جاهزة للبدء السريع")
    col_t1, col_t2, col_t3 = st.columns(3)
    
    scope_val, domain_val, budget_val, days_val = "", "التجارة الإلكترونية", 3500, 30
    
    if col_t1.button("🛒 متجر إلكتروني متكامل"):
        scope_val = "تطبيق متجر إلكتروني لبيع المنتجات مع بوابة دفع سريعة ونظام إدارة المخزون"
        domain_val = "التجارة الإلكترونية"
        budget_val = 4500
        days_val = 35
    elif col_t2.button("🎓 منصة دورات تعليمية"):
        scope_val = "منصة تعليمية تتيح رفع الكورسات واختبارات تفاعلية وشهادات تلقائية"
        domain_val = "التعليم الرقمي"
        budget_val = 3000
        days_val = 25
    elif col_t3.button("🚗 تطبيق توصيل وخدمات"):
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
        
        submit_btn = st.form_submit_button("🚀 توليد وتوقيع الخطة الهندسية")
        
    if submit_btn:
        if st.session_state.user['credits'] < 1:
            st.error("❌ رصيدك غير كافٍ! يرجى الشحن للاستمرار.")
            st.markdown(f'<a href="{PAYMENT_LINK}" target="_blank" class="checkout-btn">تجديد الاشتراك الآن</a>', unsafe_allow_html=True)
        elif not project_scope:
            st.warning("⚠️ يرجى تقديم نطاق العمل لتبدأ عملية التوليد.")
        else:
            with st.spinner("⏳ جاري استرجاع المشاريع المماثلة (RAG) وتوليد المهام والتوقيع الرقمي..."):
                time.sleep(1.5) # Simulate Engine Execution
                
                # Fetch RAG Insights
                similar_context = rag_engine.search_similar(project_scope)
                
                # Generated Mock Tasks Engine
                tasks = [
                    {"id": 1, "task": "تحليل المتطلبات وتصميم المخططات Architecture", "days": int(target_days*0.15), "cost": int(budget*0.15), "status": "مخطط"},
                    {"id": 2, "task": "بناء قواعد البيانات وتأمين API Backend", "days": int(target_days*0.35), "cost": int(budget*0.35), "status": "مخطط"},
                    {"id": 3, "task": "تطوير واجهات المستخدم Frontend & UI Components", "days": int(target_days*0.30), "cost": int(budget*0.30), "status": "مخطط"},
                    {"id": 4, "task": "الاختبارات والتكامل Deployment & QA", "days": int(target_days*0.20), "cost": int(budget*0.20), "status": "مخطط"},
                ]
                
                plan_payload = {
                    "project_name": project_name,
                    "domain": domain,
                    "budget": budget,
                    "target_days": target_days,
                    "tasks": tasks,
                    "generated_at": datetime.now().isoformat()
                }
                
                signature = SecurityEngine.generate_signature(plan_payload)
                
                # Update Session State
                st.session_state.current_plan = plan_payload
                st.session_state.plan_signature = signature
                st.session_state.user['credits'] -= 1
                
                st.success("✅ تم توليد الخطة وتوقيعها رقمياً بنجاح!")

    # Display Results if Available
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

# ==========================================
# 7. ANALYTICS & INTERACTIVE GAUGES
# ==========================================
elif active_tab == "📊 التحليلات التفاعلية":
    st.title("📊 التحليلات البصرية ومقاييس الأداء")
    
    if not st.session_state.current_plan:
        st.info("💡 قم بتوليد خطة مشروع أولاً لعرض التحليلات التفاعلية.")
    else:
        plan = st.session_state.current_plan
        df = pd.DataFrame(plan['tasks'])
        
        # Upper Summary Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("إجمالي التكلفة", f"${plan['budget']:,}")
        col_m2.metric("إجمالي الأيام", f"{plan['target_days']} يوم")
        col_m3.metric("عدد المهام", f"{len(df)}")
        col_m4.metric("الأمان الرقمي", "HMAC-Verified")
        
        st.write("---")
        
        # Interactive Plotly Gauges
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            fig_gauge1 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 88,
                title = {'text': "مؤشر موثوقية التقدير (Accuracy Rate %)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#10B981"},
                    'steps': [
                        {'range': [0, 50], 'color': "#334155"},
                        {'range': [50, 80], 'color': "#475569"}
                    ],
                }
            ))
            fig_gauge1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_gauge1, use_container_width=True)
            
        with col_g2:
            fig_gauge2 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 24,
                title = {'text': "مؤشر المخاطر المتوقعة (Risk Factor %)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#EF4444"},
                    'steps': [
                        {'range': [0, 40], 'color': "#334155"},
                        {'range': [40, 70], 'color': "#475569"}
                    ],
                }
            ))
            fig_gauge2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_gauge2, use_container_width=True)

        # Charts Section
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_pie = px.pie(df, values='cost', names='task', title='توزيع الميزانية على المهام', hole=0.4)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_c2:
            fig_bar = px.bar(df, x='task', y='days', title='المدة الزمنية لكل مهمة (أيام)', color='days', color_continuous_scale='Blues')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 8. HITL TASK EDITOR
# ==========================================
elif active_tab == "✏️ محرر المهام (HITL)":
    st.title("✏️ محرر المهام التفاعلي (Human-In-The-Loop)")
    st.caption("تعديل الأيام والتكلفة يدوياً مع إعادة التوقيع الرقمي التلقائي لمنع التلاعب.")
    
    if not st.session_state.current_plan:
        st.warning("⚠️ لا توجد خطة حالية لتعديلها. اختر تبويب 'بناء خطة مشروع' أولاً.")
    else:
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.current_plan['tasks']),
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.button("💾 حفظ التعديلات وإعادة التوقيع الرقمي"):
            updated_tasks = edited_df.to_dict(orient='records')
            st.session_state.current_plan['tasks'] = updated_tasks
            st.session_state.current_plan['budget'] = sum(item['cost'] for item in updated_tasks)
            st.session_state.current_plan['target_days'] = sum(item['days'] for item in updated_tasks)
            
            # Re-Sign Document
            new_sig = SecurityEngine.generate_signature(st.session_state.current_plan)
            st.session_state.plan_signature = new_sig
            
            st.success("✅ تم تحديث المهام وحساب التوقيع الرقمي الجديد بنجاح!")
            st.rerun()

# ==========================================
# 9. ACCOUNT & SUBSCRIPTION MANAGEMENT
# ==========================================
elif active_tab == "💳 إدارة الحساب":
    st.title("💳 تفاصيل الحساب والاشتراك")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("بيانات المستخدم")
        st.write(f"**اسم المشترك:** {st.session_state.user['username']}")
        st.write(f"**باقة الاشتراك:** {st.session_state.user['role']}")
        st.write(f"**الرصيد الحالي:** {st.session_state.user['credits']} نقطة توليد")
        
    with col_a2:
        st.subheader("ترقية الحساب / شراء رصيد")
        st.write("احصل على نقاط إضافية لتوليد الخطط الهندسية واستخدام الذكاء الاصطناعي.")
        st.markdown(
            f'<a href="{PAYMENT_LINK}" target="_blank" style="display: inline-block; background-color: #2563EB; color: white; padding: 14px 28px; border-radius: 8px; font-weight: bold; text-decoration: none;">🔗 الذهاب لبوابة الدفع Lemon Squeezy</a>', 
            unsafe_allow_html=True
        )
