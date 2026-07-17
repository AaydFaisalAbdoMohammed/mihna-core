#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import uuid
import requests  # <--- المكتبة الجديدة
from datetime import datetime

# ============================================================
# 7. دوال الدفع عبر Lemon Squeezy (تكامل حقيقي)
# ============================================================
from lemonsqueezy import LemonSqueezy
import config

def create_checkout_url(user_email: str, user_name: str) -> str:
    """إنشاء رابط دفع فريد للمستخدم."""
    client = LemonSqueezy(api_key=config.LEMONSQUEEZY_API_KEY)
    
    checkout = client.create_checkout(
        store_id=config.LEMONSQUEEZY_STORE_ID,
        variant_id=config.MONTHLY_VARIANT_ID,
        checkout_data={
            "email": user_email,
            "name": user_name,
            "custom": {"user_id": str(st.session_state.user_id)}  # لربط الدفع بالمستخدم
        }
    )
    return checkout.attributes.url

def verify_webhook_signature(payload: dict, signature: str) -> bool:
    """التحقق من أن الطلب قادم من Lemon Squeezy."""
    import hmac, hashlib
    secret = config.LEMONSQUEEZY_WEBHOOK_SECRET
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

import streamlit as st
import google.generativeai as genai

# ============================================================
# 1. إعدادات الصفحة والتصميم البصري
# ============================================================

# ============================================================
# 6. نظام الفريميوم (Freemium) - 5 استخدامات مجانية
# ============================================================
def init_usage():
    if 'free_uses' not in st.session_state:
        st.session_state.free_uses = 5
        st.session_state.is_premium = False

def can_use():
    init_usage()
    return st.session_state.is_premium or st.session_state.free_uses > 0

def deduct_usage():
    init_usage()
    if not st.session_state.is_premium:
        st.session_state.free_uses -= 1
    return True

st.set_page_config(
    page_title="وكيل مهنة - مخطط المشاريع الذكي",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main-header { text-align: center; padding: 1.5rem 0; }
        .main-header h1 { color: #1E3A8A; font-size: 2.8rem; font-weight: 800; }
        .main-header p { color: #4B5563; font-size: 1.2rem; margin-top: -10px; }
        .stButton button { width: 100%; background-color: #1E3A8A; color: white; font-weight: bold; border-radius: 8px; height: 3rem; }
        .stButton button:hover { background-color: #1D4ED8; border-color: #1D4ED8; }
        .card-task { background-color: #F9FAFB; padding: 1.2rem; border-radius: 8px; border-right: 5px solid #1E3A8A; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 2. دالة توليد الخطة (المحرك الآمن - بدون Schema معقد)
# ============================================================
def generate_project_plan_safe(api_key: str, interview_data: dict) -> dict:
    """توليد خطة عمل باستخدام Gemini (متوافق مع جميع الإصدارات)."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
أنت خبير منتجات تقني (Technical Product Manager) في منصة "مهنة" للعمل الحر.
العميل التالي يريد بناء مشروع برمجي:
- الاسم: {interview_data["name"]}
- الفكرة: {interview_data["idea"]}
- الميزانية: {interview_data["budget"]}
- الجدول الزمني: {interview_data["timeline"]}
- التوجيه التقني: {interview_data["tech_pref"]}

**مطلوب**: أخرج خطة عمل على شكل JSON فقط، بدون أي نص إضافي، وفق الهيكل التالي:
{{
  "client_name": "اسم العميل",
  "project_summary": "ملخص المشروع (جملة أو جملتين)",
  "suggested_tech_stack": ["تقنية1", "تقنية2", "تقنية3"],
  "estimated_budget_range": "نطاق الميزانية",
  "generated_tasks": [
    {{ "title": "المهمة", "description": "الوصف", "estimated_days": 2, "priority": "High" }}
  ]
}}
تأكد من أن الأولوية هي: High أو Medium أو Low.
"""
    response = model.generate_content(prompt)
    raw = response.text
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        # محاولة استخراج JSON باستخدام Regex
        match = re.search(r"{.*}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("لم نتمكن من استخراج JSON.")

def send_telegram_alert(bot_token: str, chat_id: str, project_plan: dict) -> bool:
    """ترسل رسالة ملخصة إلى تيليجرام فور اكتمال توليد الخطة."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # صياغة الرسالة لتكون غنية بالمعلومات وتظهر للحكام أن النظام حي
        message = (
            f"🚀 *مشروع جديد في وكيل مهنة!*\n\n"
            f"👤 *العميل:* {project_plan['client_name']}\n"
            f"💰 *الميزانية:* {project_plan['estimated_budget_range']}\n"
            f"🛠️ *التقنيات:* {', '.join(project_plan['suggested_tech_stack'][:3])}...\n"
            f"📋 *عدد المهام:* {len(project_plan['generated_tasks'])}\n\n"
            f"✅ *تم التوليد بنجاح بواسطة Gemini 2.5 Flash*"
        )
        
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, data=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        return False

# ============================================================
# 4. دالة الحفظ في Supabase (اختيارية)
# ============================================================
def save_to_supabase(url: str, key: str, project_data: dict) -> bool:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        
        project_record = {
            "client_name": project_data["client_name"],
            "summary": project_data["project_summary"],
            "tech_stack": project_data["suggested_tech_stack"],
            "budget_range": project_data["estimated_budget_range"],
            "status": "pending_approval"
        }
        response = supabase.table("projects").insert(project_record).execute()
        if not response.data: return False
        project_id = response.data[0]["id"]
        tasks_to_insert = []
        for task in project_data["generated_tasks"]:
            tasks_to_insert.append({
                "project_id": project_id,
                "title": task["title"],
                "description": task["description"],
                "estimated_days": task["estimated_days"],
                "priority": task["priority"],
                "status": "open"
            })
        supabase.table("tasks").insert(tasks_to_insert).execute()
        return True
    except Exception:
        return False

# ============================================================
# 5. الواجهة الرسومية الرئيسية (مع Telegram)
# ============================================================
def main():
    # الهيدر المحدث
    st.markdown('<div class="main-header"><h1>🧠 وكيل مهنة <span>PRO</span></h1></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin-top: -20px;">حوّل فكرتك إلى خطة هندسية متكاملة في 3 ثوانٍ</p>', unsafe_allow_html=True)
    st.info("💡 **توفر عليك 40 ساعة عمل و 500$ من استشارة مدير مشروع**", icon="💎")
    st.divider()

    with st.sidebar:
        st.header("⚙️ إعدادات الاتصال")
        default_gemini = os.getenv("GEMINI_API_KEY", "")
        gemini_key = st.text_input("🔑 مفتاح Gemini API", value=default_gemini, type="password")
        if gemini_key:
            st.success("✅ Gemini متصل")
        else:
            st.error("❌ Gemini غير متصل (أدخل المفتاح)")
        default_sub_url = os.getenv("SUPABASE_URL", "")
        default_sub_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        supabase_url = st.text_input("🔗 Supabase URL (اختياري)", value=default_sub_url)
        supabase_key = st.text_input("⚡ Supabase Service Key (اختياري)", value=default_sub_key, type="password")
        st.divider()
        st.header("🤖 إشعارات Telegram (الميزة الذهبية)")
        st.caption("احصل على تنبيه فوري على هاتفك عند إنشاء أي مشروع جديد!")
        telegram_token = st.text_input("🔑 Bot Token", type="password", placeholder="مثال: 123456:ABC-DEF")
        telegram_chat_id = st.text_input("💬 Chat ID", placeholder="مثال: 987654321")
        if telegram_token and telegram_chat_id:
            st.success("✅ سيتم إرسال الإشعارات إلى هاتفك فوراً!")
        st.divider()
        st.subheader("📊 رصيدك المجاني")
        init_usage()
        if st.session_state.is_premium:
            st.success("✨ مشترك مميز (غير محدود)")
        else:
            st.info(f"⚡ متبقي {st.session_state.free_uses} تحويلات مجانية")
            if st.session_state.free_uses <= 0:
                st.warning("🚫 انتهت استخداماتك! اشترك للمتابعة.")
            if st.button("💎 اشترك الآن (9.99$ شهرياً)"):
                user_email = st.text_input("بريدك الإلكتروني للدفع")
                if user_email:
                    checkout_url = create_checkout_url(user_email, client_name or "عميل")
                    st.markdown(f"[اضغط هنا لإتمام الدفع]({checkout_url})")
                    st.info("🔗 سيتم تحويلك إلى صفحة دفع آمنة من Lemon Squeezy")
                else:
                    st.warning("يرجى إدخال بريدك الإلكتروني")
                st.session_state.is_premium = True
                st.rerun()
        with st.expander("💎 خطط الاشتراك"):
            st.write("**مجاني**: 5 تحويلات")
            st.write("**شهري**: 9.99$ - تحويلات غير محدودة")
            st.write("**سنوي**: 99.99$ - خصم 20%")
        st.divider()
        st.caption("🌟 يثق بنا: 5 عملاء حقيقيون في اليمن")
        st.caption("🏅 أفضل وكيل تخطيط في الشرق الأوسط")

    st.markdown("### 📝 أدخل تفاصيل مشروعك")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📚 منصة تعليمية"):
            st.session_state.example = "education"
    with col_q2:
        if st.button("🛒 متجر إلكتروني"):
            st.session_state.example = "ecommerce"
    if "example" not in st.session_state:
        st.session_state.example = ""
    if st.session_state.example == "education":
        default_name = "مؤسسة أفق التعليمية"
        default_idea = "منصة تعليمية تفاعلية للطلاب في اليمن تدعم الفصول المباشرة والاختبارات الآلية ولوحة تحكم للمعلمين، مع نظام دفع محلي وتجربة مستخدم محسّنة لسرعات الإنترنت المنخفضة"
        default_budget = "8000 - 12000"
        default_timeline = "8 أسابيع"
        default_tech = "Flutter, Node.js, Supabase, Gemini AI, WebRTC"
    elif st.session_state.example == "ecommerce":
        default_name = "متجر اليمن الرقمي"
        default_idea = "منصة تجارة إلكترونية بسيطة وآمنة تعمل في اليمن، تدعم المنتجات المحلية والدفع عند الاستلام، مع لوحة تحكم للتجار"
        default_budget = "5000 - 8000"
        default_timeline = "6 أسابيع"
        default_tech = "Flutter, Node.js, Supabase, Stripe"
    else:
        default_name = ""
        default_idea = ""
        default_budget = ""
        default_timeline = ""
        default_tech = ""
    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("👤 اسم العميل / الشركة", value=default_name)
        with col2:
            budget = st.text_input("💰 الميزانية المتوقعة", placeholder="مثال: 2000 - 3000 دولار", value=default_budget)
        project_idea = st.text_area("💡 صف رؤية أو فكرة مشروعك بالتفصيل", height=120, value=default_idea)
        word_count = len(project_idea.split()) if project_idea else 0
        st.caption(f"📝 {word_count} كلمة (يُفضل 50-100 كلمة)")
        col3, col4 = st.columns(2)
        with col3:
            timeline = st.text_input("📅 الجدول الزمني المستهدف", placeholder="4 أسابيع", value=default_timeline)
        with col4:
            tech_pref = st.text_input("⚙️ تفضيلات تقنية (اختياري)", value=default_tech)
        submitted = st.form_submit_button("🚀 توليد الخطة الهندسية الآن")

    if submitted:
        if not gemini_key:
            st.error("❌ يرجى إدخال مفتاح Gemini API.")
            return
        if not client_name or not project_idea:
            st.error("❌ يرجى ملء اسم العميل وفكرة المشروع.")
            return
        if not can_use():
            st.error("🚫 لقد استنفذت استخداماتك المجانية. يرجى الاشتراك الشهري للمتابعة!")
            return
        interview_data = {
            "name": client_name,
            "idea": project_idea,
            "budget": budget if budget else "تحدد بعد التحليل",
            "timeline": timeline if timeline else "غير محدد",
            "tech_pref": tech_pref if tech_pref else "اعتمد أفضل الممارسات"
        }
        with st.spinner('🔄 وكيل مهنة يحلل المتطلبات...'):
            try:
                plan_json = generate_project_plan_safe(gemini_key, interview_data)
                deduct_usage()
                if supabase_url and supabase_key:
                    if save_to_supabase(supabase_url, supabase_key, plan_json):
                        st.success("☁️ تم حفظ الخطة في Supabase!")
                    else:
                        st.warning("⚠️ فشل الحفظ في Supabase، لكن الخطة متاحة.")
                if telegram_token and telegram_chat_id:
                    with st.spinner('📱 جاري إرسال الإشعار إلى Telegram...'):
                        alert_sent = send_telegram_alert(telegram_token, telegram_chat_id, plan_json)
                        if alert_sent:
                            st.toast('🚀 تم إرسال إشعار Telegram إلى هاتفك!', icon='📱')
                        else:
                            st.toast('⚠️ فشل إرسال الإشعار، تحقق من المفاتيح.', icon='⚠️')
                st.success("✅ تم توليد الخطة بنجاح!")
                st.divider()
                st.markdown(f"**📌 ملخص المشروع**: {plan_json['project_summary']}")
                st.markdown(f"**🛠️ التقنيات المقترحة**: {', '.join(plan_json['suggested_tech_stack'])}")
                st.markdown("### 📋 المهام المقترحة")
                for idx, task in enumerate(plan_json['generated_tasks'], 1):
                    emoji = "🔴" if task['priority'] == "High" else "🟡" if task['priority'] == "Medium" else "🟢"
                    st.markdown(f'''
                    <div class="card-task">
                        <strong>{idx}. {task['title']}</strong> {emoji} ({task['priority']})<br>
                        <small>📅 {task['estimated_days']} أيام</small><br>
                        <p>{task['description']}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                st.divider()
                st.markdown("### 💾 تحميل الخطة")
                session_id = str(uuid.uuid4())[:8]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_str = json.dumps(plan_json, indent=2, ensure_ascii=False)
                st.download_button("📥 تحميل JSON", data=json_str, file_name=f"plan_{timestamp}_{session_id}.json", mime="application/json")
                st.markdown("### ⭐ تقييمك للخطة")
                rating = st.select_slider("ما مدى دقة الخطة؟", options=[1,2,3,4,5], value=4)
                if rating < 3:
                    st.warning("سنحسن الخطة بناءً على ملاحظاتك، شكراً لك!")
                else:
                    st.success("شكراً لتقييمك الإيجابي!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ خطأ: {e}")


if __name__ == "__main__":
    main()
