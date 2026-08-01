#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX PRO HYBRID ENTERPRISE ARCHITECTURE. ALL RIGHTS RESERVED.
دمج المحرك الأمني والهندسي (OOP) مع بوابات الدفع والإشعارات والنشر السحابي
===============================================================================
"""

import os
import re
import json
import uuid
import hashlib
import hmac
import time
import secrets
import logging
import requests
import datetime
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# ----------------- Optional Heavy Dependencies -----------------
try:
    import pymysql
    import pymysql.cursors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =====================================================================
# 1. SYSTEM SECURITY & INTEGRITY ENGINE
# =====================================================================
class VaultSecurity:
    HMAC_KEY = os.getenv("HMAC_KEY", secrets.token_hex(32))

    @classmethod
    def get_fingerprint(cls) -> str:
        seed = f"{os.getenv('HOSTNAME', 'cloud_node')}-{datetime.datetime.now().isoformat()}-{uuid.uuid4()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:24]

    @classmethod
    def sign_payload(cls, payload: dict) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(cls.HMAC_KEY.encode(), payload_str.encode(), hashlib.sha512).hexdigest()[:32]

# =====================================================================
# 2. NOTIFICATION & BILLING ENGINE
# =====================================================================
class CommercialEngine:
    @staticmethod
    def send_telegram(plan: dict) -> bool:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "597154321")
        if not bot_token: return False
        
        msg = f"🚀 *مشروع جديد PHOENIX PRO*\n\n👤 *العميل:* {plan.get('client')}\n💰 *الميزانية:* {plan.get('budget_str')}\n📅 *المدة:* {plan.get('timeline')}\n🔑 *التوقيع:* `{plan.get('signature', 'N/A')}`"
        try:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                          json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=4)
            return True
        except Exception:
            return False

    @staticmethod
    def get_checkout_url(email: str) -> str:
        store_slug = os.getenv("LEMONSQUEEZY_STORE_SLUG", "mihna")
        return f"https://{store_slug}.lemonsqueezy.com/buy?checkout[email]={email.strip()}"

# =====================================================================
# 3. AI ENGINE
# =====================================================================
class PhoenixAI:
    @staticmethod
    def generate_architecture(api_key: str, req: dict) -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        أنت مستشار وحاكم معماري في PHOENIX PRO. قم بتحليل هذا المشروع:
        - العميل: {req['client']}
        - الوصف والنطاق: {req['desc']}
        - الميزانية: {req['budget']}
        - الجدول الزمني: {req['timeline']}
        - التقنيات المفضلة: {req['tech']}

        أخرج البيانات بتنسيق JSON حصرياً بالهيكل التالي:
        {{
            "client": "{req['client']}",
            "executive_summary": "ملخص معماري وشامل",
            "tech_stack": ["Tech 1", "Tech 2"],
            "budget_str": "{req['budget']}",
            "timeline": "{req['timeline']}",
            "risk_score": 15,
            "confidence_score": 90,
            "tasks": [
                {{"title": "المهمة 1", "days": 5, "cost": 1200, "priority": "عالية"}},
                {{"title": "المهمة 2", "days": 10, "cost": 2400, "priority": "متوسطة"}}
            ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            data = json.loads(match.group() if match else response.text)
            data["signature"] = VaultSecurity.sign_payload(data)
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            return data
        except Exception as e:
            raise ValueError(f"فشل التحليل المعماري: {str(e)}")

# =====================================================================
# 4. EXPORT ENGINE
# =====================================================================
class ExportEngine:
    @staticmethod
    def build_pdf(data: dict) -> bytes:
        if not REPORTLAB_AVAILABLE: return b""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>Enterprise Architecture Document: {data.get('client')}</b>", styles['Title']), Spacer(1, 12)]
        
        table_data = [["Task", "Days", "Cost ($)", "Priority"]]
        for t in data.get("tasks", []):
            table_data.append([t.get('title'), str(t.get('days')), f"${t.get('cost')}", t.get('priority')])
            
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
        ]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()

    @staticmethod
    def build_excel(tasks: list) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Architecture_Plan")
        return buffer.getvalue()

# =====================================================================
# 5. STREAMLIT APPLICATION UI
# =====================================================================
def init_session():
    if "user_name" not in st.session_state: st.session_state.user_name = "AYAD FAISAL ABDO MOHAMMED"
    if "remaining_credits" not in st.session_state: st.session_state.remaining_credits = 5
    if "plans_history" not in st.session_state: st.session_state.plans_history = []
    if "selected_plan" not in st.session_state: st.session_state.selected_plan = None

def main():
    st.set_page_config(page_title="PHOENIX PRO | Hybrid Enterprise", page_icon="🚀", layout="wide")
    init_session()
    
    st.markdown("""
    <style>
        .stApp { background-color: #0b0f19; color: #f1f5f9; }
        .hero-header { font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
        .pay-btn { display: block; background: #2563eb; color: white; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ PHOENIX COMMAND")
        st.caption(f"👤 المستخدم: {st.session_state.user_name}")
        st.markdown(f"**⚡ التحويلات المتبقية:** `{st.session_state.remaining_credits}`")
        
        st.divider()
        api_key = st.text_input("🔑 مفتاح Gemini API", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        
        st.divider()
        st.subheader("💳 الاشتراك والتفعيل")
        pay_email = st.text_input("البريد الإلكتروني", value="eng.alhiadri2020@gmail.com")
        st.markdown(f'<a href="{CommercialEngine.get_checkout_url(pay_email)}" target="_blank" class="pay-btn">💳 الشراء عبر Lemon Squeezy</a>', unsafe_allow_html=True)
        
        act_code = st.text_input("رمز التفعيل", type="password")
        if st.button("تفعيل الكود", use_container_width=True):
            if act_code == "PRO2026":
                st.session_state.remaining_credits = 999
                st.success("تم تفعيل الباقة المفتوحة!")
                st.rerun()

    # Main Dashboard
    st.markdown('<div class="hero-header">🔥 PHOENIX PRO ENTERPRISE HYBRID</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🚀 توليد المعمارية", "📊 التحليلات والأرشيف", "📦 التصدير والتوثيق"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            client = st.text_input("اسم العميل / الشركة", value="مؤسسة أفق")
            budget = st.text_input("الميزانية التقديرية", value="8000 - 12000 $")
        with c2:
            timeline = st.text_input("المدة الزمنية", value="6 أسابيع")
            tech = st.text_input("التقنيات التفضيلية", value="Flutter, Node.js, PostgreSQL")
            
        desc = st.text_area("نطاق المشروع والمتطلبات التفصيلية", value="تطوير منصة سحابية لإدارة العقود وتتبع الصيانة مع بوابات دفع متكاملة.")
        
        if st.button("⚡ بدء التوليد والتوقيع المشفر", use_container_width=True):
            if not api_key:
                st.error("يرجى إدخال مفتاح API أولاً.")
            elif st.session_state.remaining_credits <= 0:
                st.error("استنفذت رصيدك المجاني.")
            else:
                with st.spinner("جاري التحليل المعماري وإرسال التنبيهات..."):
                    req_payload = {"client": client, "budget": budget, "timeline": timeline, "tech": tech, "desc": desc}
                    plan = PhoenixAI.generate_architecture(api_key, req_payload)
                    
                    st.session_state.plans_history.append(plan)
                    st.session_state.selected_plan = plan
                    st.session_state.remaining_credits -= 1
                    
                    CommercialEngine.send_telegram(plan)
                    st.success("✅ تم بناء وتوقيع المعمارية بنجاح!")

    with t2:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            st.subheader(f"📊 تحليل المعمارية: {p.get('client')}")
            
            k1, k2, k3 = st.columns(3)
            k1.metric("درجة المخاطرة", f"{p.get('risk_score')}%")
            k2.metric("نسبة الدقة والاعتماد", f"{p.get('confidence_score')}%")
            k3.metric("توقيع النظام", p.get('signature')[:12] + "...")
            
            tasks = p.get("tasks", [])
            if tasks:
                df = pd.DataFrame(tasks)
                fig = px.bar(df, x="title", y="days", color="priority", title="توزيع الأيام على المهمات", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("قم بتوليد خطة من التبويب الأول للبدء.")

    with t3:
        if st.session_state.selected_plan:
            p = st.session_state.selected_plan
            st.subheader("📦 تصدير المستندات المعتمدة")
            st.code(f"Digital HMAC Signature: {p.get('signature')}", language="json")
            
            ec1, ec2, ec3 = st.columns(3)
            ec1.download_button("📦 تصدير JSON المشفر", json.dumps(p, ensure_ascii=False, indent=2), "plan.json", "application/json", use_container_width=True)
            ec2.download_button("📊 تصدير جدول Excel", ExportEngine.build_excel(p.get("tasks", [])), "plan.xlsx", use_container_width=True)
            if REPORTLAB_AVAILABLE:
                ec3.download_button("📄 تصدير تقرير PDF", ExportEngine.build_pdf(p), "plan.pdf", "application/pdf", use_container_width=True)
        else:
            st.info("لا توجد خطة جاهزة للتصدير.")

if __name__ == "__main__":
    main()
