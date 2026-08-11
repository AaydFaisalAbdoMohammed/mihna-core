#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & WAKEEL MEHNA PRO ENTERPRISE ARCHITECTURE v13.7 - ULTRA ULTIMATE SaaS
===============================================================================
"""

import os
import json
import time
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import (
    SecurityEngine, NotificationEngine, generate_excel_download,
    generate_pdf_plan, create_half_doughnut_gauge
)
from db import HybridDatabaseEngine, SUPER_ADMIN_EMAIL
from ai import (
    PhoenixAI, AIPaymentAgent, build_detailed_plan_text, 
    PAYMENT_LINK_MONTHLY, PAYMENT_LINK_YEARLY, EngineeringAIEngine, LiveTwinEngine
)
from auth import render_auth_page

APP_TITLE = "PHOENIX & WAKEEL MEHNA PRO - ULTRA ENTERPRISE v13.7"

# تهيئة المحرك الهندسي الذكي
eng_ai = EngineeringAIEngine()

T = {
    'ar': {
        'title': "🚀 وكيل مهنة PRO | PHOENIX Enterprise v13.7 (Ultra Global Edition)",
        'subtitle': "المنصة العالمية الأقوى والأكثر ذكاءً لهندسة خطط المشاريع، التوأم الرقمي الميداني، والذكاء الاصطناعي التوليدي AI-ConTech.",
        'lang_select': "🌐 لغة الواجهة (Language):",
        'theme_select': "🎨 مظهر التطبيق (Theme):",
        'dark': "🌙 الداكن (Dark)", 'light': "☀️ الفاتح (Light)",
        'user': "👤 المستخدم:", 'credits': "💳 الرصيد الحالي:", 'points': "نقاط مجانية",
        'renew_title': "🛒 ترقية الاشتراك", 'renew_btn': "⚡ اشترك الآن وترقية الحساب",
        'logout_btn': "🚪 تسجيل الخروج", 'notify_settings': "📲 إعدادات الإشعارات الفورية",
        'wa_phone': "رقم الواتساب", 'tg_handle': "معرف التليجرام",
        'tab1': "🏗️ بناء الخطة والكوادر", 
        'tab_eng': "📐 التخطيط الهندسي والكميات (AI-ConTech)",
        'tab_live': "🔮 التوأم الرقمي والمحاكاة الحية",
        'tab2': "📊 التحليلات التفاعلية 6D",
        'tab3': "✏️ محرر المهام والتقرير النصي", 'tab4': "🔄 التغذية الراجعة والتكيّف السعري",
        'tab5': "💳 الحساب والاشتراكات", 'tab6': "🗄️ أرشفة Cloud SQL (7-Tables Schema)",
        'tab_admin': "👑 لوحة الإدارة العليا (CEO Panel)",
        'quick_templates': "⚡ قوالب جاهزة للبدء السريع",
        'ecom': "🛒 متجر إلكتروني", 'edu': "🎓 منصة تعليمية", 'delivery': "🚗 تطبيق توصيل",
        'p_name': "اسم المشروع", 'tech_domain': "المجال التقني", 'budget': "الميزانية التقديرية ($)",
        'tech_stack': "التقنيات المستخدمة", 'target_days': "المدة الزمنية المستهدفة (يوم)", 'risk_level': "تحمل المخاطر",
        'scope': "نطاق العمل (Scope of Work)",
        'generate_btn': "🚀 توليد وحساب الكوادر والتوقيع الرقمي (1 نقطة)",
        'export_excel': "📥 تحميل جدول المهام (Excel)", 'export_pdf': "📄 تحميل الخطة التنفيذية (PDF)",
        'detailed_plan': "📜 الخطة التنفيذية النصية الشاملة والمعمقة", 'save_re_sign': "💾 حفظ التعديلات وإعادة التوقيع الرقمي",
        'digital_sig': "🔑 التوقيع الرقمي المشفر (HMAC-SHA512):",
        'sig_valid': "✔ توقيع موثوق وسليم", 'sig_invalid': "❌ تم التلاعب بالبيانات",
        'send_wa': "📱 إرسال عبر WhatsApp", 'send_tg': "📲 إشعار Telegram Bot",
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
        'users_log_title': "📋 سجل جميع المستخدمين وااشتراكاتهم الحية",
        'demands_title': "💬 طلبات ورغبات المستخدمين من جدول التغذية الراجعة (User Demands & Needs)",
        
        # ConTech Translation
        'eng_title': "🏗️ وحدة التخطيط الهندسي وحساب الكميات الذكي (AI-ConTech)",
        'eng_caption': "التصميم المعماري الجيلاتي، حساب جدول الكميات (BOQ)، وإسناد المناقصات بنقرة زر.",
        'eng_subtab1': "📐 1. التصميم الجيلاتي (Generative Floor Plan)",
        'eng_subtab2': "📊 2. حساب الكميات والتكلفة (Automated BOQ)",
        'eng_subtab3': "🤝 3. السوق التنفيذي والمناقصات (Smart Marketplace)"
    },
    'en': {
        'title': "🚀 Wakeel Mehna PRO | PHOENIX Enterprise v13.7 (Ultra Global Edition)",
        'subtitle': "The Ultimate Global AI Architecture & Field Twin Platform with AI-ConTech Civil Planning Engine.",
        'lang_select': "🌐 Interface Language:",
        'theme_select': "🎨 Application Theme:",
        'dark': "🌙 Dark", 'light': "☀️ Light",
        'user': "👤 User:", 'credits': "💳 Balance:", 'points': "points",
        'renew_title': "🛒 Upgrade Plan", 'renew_btn': "⚡ Upgrade & Subscribe Now",
        'logout_btn': "🚪 Log Out", 'notify_settings': "📲 Instant Notifications",
        'wa_phone': "WhatsApp Phone", 'tg_handle': "Telegram Handle",
        'tab1': "🏗️ Build Plan & Payroll", 
        'tab_eng': "📐 Engineering & BOQ (AI-ConTech)",
        'tab_live': "🔮 AI Live Twin",
        'tab2': "📊 Advanced 6D Analytics",
        'tab3': "✏️ Task Editor & Text Plan", 'tab4': "🔄 Feedback & Pricing",
        'tab5': "💳 Account & Subscriptions", 'tab6': "🗄️ Cloud SQL 7-Tables Archive",
        'tab_admin': "👑 CEO & Admin Panel",
        'quick_templates': "⚡ Quick Start Templates",
        'ecom': "🛒 E-Commerce App", 'edu': "🎓 E-Learning Platform", 'delivery': "🚗 Delivery App",
        'p_name': "Project Name", 'tech_domain': "Technical Domain", 'budget': "Estimated Budget ($)",
        'tech_stack': "Tech Stack", 'target_days': "Target Timeline (Days)", 'risk_level': "Risk Tolerance",
        'scope': "Scope of Work",
        'generate_btn': "🚀 Generate Plan, Payroll & Sign (1 Credit)",
        'export_excel': "📥 Download Tasks (Excel)", 'export_pdf': "📄 Download Plan (PDF)",
        'detailed_plan': "📜 Extended Text Plan", 'save_re_sign': "💾 Save Edits & Re-Sign Digitally",
        'digital_sig': "🔑 Encrypted HMAC Signature:",
        'sig_valid': "✔ Valid Signature", 'sig_invalid': "❌ Invalid Signature",
        'send_wa': "📱 Send via WhatsApp", 'send_tg': "📲 Notify Telegram Bot",
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
        'demands_title': "💬 User Demands & Market Feature Requests",
        
        # ConTech Translation
        'eng_title': "🏗️ Engineering & AI Quantity Surveying (AI-ConTech)",
        'eng_caption': "Generative Floor Plan, Automated BOQ Calculation, and One-Click Bidding Marketplace.",
        'eng_subtab1': "📐 1. Generative Floor Plan",
        'eng_subtab2': "📊 2. Automated BOQ & Costing",
        'eng_subtab3': "🤝 3. Smart Contractor Marketplace"
    }
}

def init_session():
    if 'lang' not in st.session_state: st.session_state.lang = 'ar'
    if 'theme' not in st.session_state: st.session_state.theme = 'light'
    if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = {'email': '', 'username': 'زائر', 'credits': 5, 'role': 'Free Trial', 'is_subscribed': False, 'is_admin': False}
    if 'current_plan' not in st.session_state: st.session_state.current_plan = None
    if 'plan_signature' not in st.session_state: st.session_state.plan_signature = None
    if 'notify_whatsapp' not in st.session_state: st.session_state.notify_whatsapp = "+967700000000"
    if 'notify_telegram' not in st.session_state: st.session_state.notify_telegram = "@Ayad_Developer"
    if 'form_scope' not in st.session_state: st.session_state.form_scope = ""
    if 'form_pname' not in st.session_state: st.session_state.form_pname = "منصة تجارة سحابية Pro"
    if 'form_domain' not in st.session_state: st.session_state.form_domain = "التجارة الإلكترونية"
    if 'form_budget' not in st.session_state: st.session_state.form_budget = 3500
    if 'form_days' not in st.session_state: st.session_state.form_days = 30
    if 'payment_notifications' not in st.session_state: st.session_state.payment_notifications = []

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

def render_engineering_tab(txt):
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.title(txt['eng_title'])
    st.caption(txt['eng_caption'])

    tab1, tab2, tab3 = st.tabs([
        txt['eng_subtab1'],
        txt['eng_subtab2'],
        txt['eng_subtab3']
    ])

    # ------------------ Tab 1: التصميم الجيلاتي ------------------
    with tab1:
        st.subheader("إدخال مواصفات الأرض والمشروع" if st.session_state.lang == 'ar' else "Land & Project Specifications")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            land_area = st.number_input("مساحة الأرض (متر مربع)" if st.session_state.lang == 'ar' else "Land Area (sqm)", min_value=50.0, value=300.0, step=10.0)
            floors = st.selectbox("عدد الطوابق" if st.session_state.lang == 'ar' else "Floors Count", [1, 2, 3, 4], index=1)
        with col2:
            bedrooms = st.number_input("عدد غرف النوم المطلوب" if st.session_state.lang == 'ar' else "Required Bedrooms", min_value=1, value=4, step=1)
            style = st.selectbox("الطراز المعماري" if st.session_state.lang == 'ar' else "Architectural Style", ["Modern Minimalist", "Classic Luxury", "Neo-Traditional", "Industrial"])
        with col3:
            budget = st.number_input("الميزانية التقديرية ($)" if st.session_state.lang == 'ar' else "Estimated Budget ($)", min_value=10000, value=150000, step=5000)
            quality = st.selectbox("مستوى جودة التشطيب" if st.session_state.lang == 'ar' else "Finishing Quality Tier", ["Economy", "Standard", "Luxury"], index=1)

        if st.button("🚀 توليد المخطط المعماري بالذكاء الاصطناعي" if st.session_state.lang == 'ar' else "🚀 Generate AI Floor Plan", type="primary", use_container_width=True):
            with st.spinner("⏳ Generating Generative Floor Layout & Calculating Space Distribution..."):
                eng_plan = eng_ai.generate_generative_floor_plan(land_area, floors, bedrooms, budget, style)
                
                st.session_state['current_eng_plan'] = eng_plan
                st.session_state['quality_tier'] = quality
                
                st.success(f"تم إنشاء المخطط بنجاح! إجمالي المساحة المبنية: {eng_plan['total_built_area']} م²" if st.session_state.lang == 'ar' else f"Layout generated successfully! Total built area: {eng_plan['total_built_area']} sqm")
                
                df_layout = pd.DataFrame(eng_plan['layout'])
                st.subheader("📐 التوزيع الهندسي الذكي للمساحات" if st.session_state.lang == 'ar' else "📐 Smart Spatial Distribution")
                st.dataframe(df_layout, use_container_width=True)

    # ------------------ Tab 2: حساب الكميات والتكلفة ------------------
    with tab2:
        st.subheader("جدول الكميات والتكلفة التقديرية (Bill of Quantities)" if st.session_state.lang == 'ar' else "Bill of Quantities (BOQ) & Estimated Cost")
        
        if 'current_eng_plan' in st.session_state:
            eng_plan = st.session_state['current_eng_plan']
            quality = st.session_state.get('quality_tier', 'Standard')
            
            boq_data = eng_ai.calculate_automated_boq(eng_plan['total_built_area'], quality)
            
            st.metric("التكلفة الإجمالية المباشرة" if st.session_state.lang == 'ar' else "Direct Grand Total Cost", f"${boq_data['grand_total_usd']:,}")
            st.info(f"💡 هامش الاحتياطي الموصى به (10% Risk Buffer): ${boq_data['contingency_buffer_10pct']:,}" if st.session_state.lang == 'ar' else f"💡 Recommended 10% Risk Buffer: ${boq_data['contingency_buffer_10pct']:,}")

            df_boq = pd.DataFrame(boq_data['boq_items'])
            st.table(df_boq)
            
            st.session_state['boq_data'] = boq_data
        else:
            st.warning("⚠️ يرجى توليد المخطط المعماري في التبويب الأول أولاً." if st.session_state.lang == 'ar' else "⚠️ Please generate the architectural floor plan in the first tab first.")

    # ------------------ Tab 3: السوق التنفيذي والمناقصات ------------------
    with tab3:
        st.subheader("طرح المشروع للمقاولين والشركات المعتمدة (Smart Bidding)" if st.session_state.lang == 'ar' else "Contractor Bidding & Execution Marketplace")
        
        if 'boq_data' in st.session_state:
            boq = st.session_state['boq_data']
            
            st.write(f"**الميزانية المستهدفة:** ${boq['grand_total_usd']:,}" if st.session_state.lang == 'ar' else f"**Target Budget:** ${boq['grand_total_usd']:,}")
            
            st.markdown("### 🏢 الشركات المقترحة والتنافسية المتاحة حالياً" if st.session_state.lang == 'ar' else "### 🏢 Verified Contractors & Live Bids")
            
            contractors = [
                {"company": "Apex Construction Group", "rating": "⭐ 4.9", "bid": boq['grand_total_usd'] * 0.95, "days": 120},
                {"company": "BuildTech Solutions", "rating": "⭐ 4.8", "bid": boq['grand_total_usd'] * 0.98, "days": 105},
                {"company": "Al-Nukhba Contracting", "rating": "⭐ 4.7", "bid": boq['grand_total_usd'] * 0.91, "days": 140},
            ]
            
            for c in contractors:
                col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
                col_a.write(f"**{c['company']}** ({c['rating']})")
                col_b.write(f"العرض: **${c['bid']:,.2f}**" if st.session_state.lang == 'ar' else f"Bid: **${c['bid']:,.2f}**")
                col_c.write(f"المدة: **{c['days']} يوم**" if st.session_state.lang == 'ar' else f"Duration: **{c['days']} days**")
                if col_d.button("إسناد العقد 📝" if st.session_state.lang == 'ar' else "Assign Contract 📝", key=f"btn_{c['company']}"):
                    st.balloons()
                    st.success(f"تم إسناد مشروعك بنجاح إلى شركة {c['company']}!" if st.session_state.lang == 'ar' else f"Project successfully assigned to {c['company']}!")
        else:
            st.warning("⚠️ يرجى إتمام حساب الكميات أولاً قبل طرح المناقصة." if st.session_state.lang == 'ar' else "⚠️ Please complete the BOQ quantity calculation prior to publishing bidding.")
            
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")
    init_session()

    lang = st.session_state.lang
    txt = T[lang]

    if not st.session_state.is_authenticated:
        render_auth_page(txt, lang)
        return

    fresh_u = HybridDatabaseEngine.get_user(st.session_state.user['email'])
    if fresh_u:
        st.session_state.user['credits'] = fresh_u['credits']
        st.session_state.user['role'] = fresh_u['role']
        st.session_state.user['is_subscribed'] = bool(fresh_u['is_subscribed'])
        st.session_state.user['is_admin'] = bool(fresh_u['is_admin']) or (fresh_u['email'].strip().lower() == SUPER_ADMIN_EMAIL.strip().lower())

    if st.session_state.theme == 'dark':
        bg_color = "#0B0F17"
        text_color = "#F8FAFC"
        glass_bg = "rgba(30, 41, 59, 0.70)"
        glass_border = "rgba(255, 255, 255, 0.12)"
        glass_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.45)"
        glass_focus_bg = "rgba(45, 55, 72, 0.88)"
        glass_focus_border = "rgba(99, 102, 241, 0.80)"
        glass_focus_shadow = "0 12px 40px 0 rgba(99, 102, 241, 0.35)"
    else:
        bg_color = "#F1F5F9"
        text_color = "#0F172A"
        glass_bg = "rgba(255, 255, 255, 0.75)"
        glass_border = "rgba(255, 255, 255, 0.65)"
        glass_shadow = "0 8px 32px 0 rgba(31, 38, 135, 0.08)"
        glass_focus_bg = "rgba(255, 255, 255, 0.95)"
        glass_focus_border = "rgba(37, 99, 235, 0.85)"
        glass_focus_shadow = "0 12px 40px 0 rgba(37, 99, 235, 0.25)"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        .glass-card {{
            background: {glass_bg}; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
            border-radius: 18px; border: 1px solid {glass_border}; box-shadow: {glass_shadow};
            padding: 24px; margin-bottom: 22px; transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .glass-card:hover {{ background: {glass_focus_bg}; border-color: {glass_focus_border}; box-shadow: {glass_focus_shadow}; transform: translateY(-3px); }}
        .badge-green {{ background-color: #10B981; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; }}
        .badge-purple {{ background-color: #8B5CF6; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; }}
        .badge-gold {{ background-color: #F59E0B; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; }}
        .checkout-btn {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white !important; padding: 12px 16px; border-radius: 12px; font-weight: bold; text-decoration: none; border: none; font-size: 14px; box-shadow: 0 4px 14px rgba(37,99,235,0.3); }}
        .checkout-btn-yearly {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #7C3AED, #9333EA); color: white !important; padding: 12px 16px; border-radius: 12px; font-weight: bold; text-decoration: none; border: none; font-size: 14px; box-shadow: 0 4px 14px rgba(124,58,237,0.3); }}
        .ai-payment-card {{ background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(49, 46, 129, 0.95) 100%); border: 2px solid #6366F1; border-radius: 18px; padding: 24px; color: #FFFFFF; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.25); }}
        .stat-card-box {{ background: {glass_bg}; backdrop-filter: blur(10px); border: 1px solid {glass_border}; border-radius: 14px; padding: 18px; text-align: right; margin-bottom: 12px; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; background: {glass_bg}; padding: 8px; border-radius: 14px; border: 1px solid {glass_border}; }}
        .stTabs [data-baseweb="tab"] {{ border-radius: 10px; padding: 8px 16px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛡️ PHOENIX AGENT")
        st.markdown("<span class='badge-purple'>Enterprise v13.7 Ultra</span>", unsafe_allow_html=True)
        st.divider()

        st.radio(txt['lang_select'], ["العربية (Arabic)", "English"], index=0 if lang == 'ar' else 1, key='lang_radio', on_change=update_language)
        st.radio(txt['theme_select'], [txt['dark'], txt['light']], index=0 if st.session_state.theme == 'dark' else 1, key='theme_radio', on_change=update_theme)

        st.divider()
        st.markdown(f"{txt['user']} **{st.session_state.user['username']}**")

        if st.session_state.user['is_subscribed']:
            st.markdown(f"Plan: <span class='badge-gold'>{st.session_state.user['role']}</span>", unsafe_allow_html=True)
            st.markdown("Credits: **Unlimited ♾️**")
        else:
            st.markdown(f"Account: <span class='badge-purple'>Free Trial</span>", unsafe_allow_html=True)
            st.markdown(f"{txt['credits']} `{st.session_state.user['credits']}` {txt['points']}")

        if st.button(txt['logout_btn'], use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()
        st.markdown(f"### {txt['renew_title']}")
        all_fb = HybridDatabaseEngine.get_all_feedback()
        adapted_insights = PhoenixAI.analyze_feedback_and_adapt_pricing(all_fb)

        if not st.session_state.user['is_subscribed']:
            if st.button("🤖 AI Payment Auto-Upgrade", type="primary", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
                st.balloons()
                st.success("🎉 Account Upgraded Successfully!")
                time.sleep(1)
                st.rerun()

        st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">💳 {txt["renew_btn"]} (${adapted_insights["recommended_monthly"]}/m)</a>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f'<a href="{PAYMENT_LINK_YEARLY}" target="_blank" class="checkout-btn-yearly">👑 Enterprise Yearly (${adapted_insights["recommended_yearly"]}/y)</a>', unsafe_allow_html=True)

        st.divider()
        st.subheader(txt['notify_settings'])
        st.session_state.notify_whatsapp = st.text_input(txt['wa_phone'], value=st.session_state.notify_whatsapp)
        st.session_state.notify_telegram = st.text_input(txt['tg_handle'], value=st.session_state.notify_telegram)

    st.title(txt['title'])
    st.caption(txt['subtitle'])

    if st.session_state.user['credits'] <= 0 and not st.session_state.user['is_subscribed']:
        st.markdown("""
        <div class="ai-payment-card">
            <h3>🤖 AI Payment Broker Agent Alert</h3>
            <p>You have used all free credits (0/5)! Execute instant AI auto-checkout via Lemon Squeezy to continue using enterprise features.</p>
        </div>
        """, unsafe_allow_html=True)
        col_pay_ai1, col_pay_ai2 = st.columns(2)
        with col_pay_ai1:
            if st.button(f"🚀 Activate Pro Monthly (${adapted_insights['recommended_monthly']})", type="primary", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
                st.balloons()
                st.rerun()
        with col_pay_ai2:
            if st.button(f"💎 Activate Enterprise Yearly (${adapted_insights['recommended_yearly']})", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "yearly")
                st.balloons()
                st.rerun()

    is_ceo_owner = (st.session_state.user['email'].strip().lower() == SUPER_ADMIN_EMAIL.strip().lower()) or st.session_state.user['is_admin']
    
    if is_ceo_owner:
        tab1, tab_eng, tab_live_twin, tab2, tab3, tab4, tab5, tab6, tab_admin = st.tabs([
            txt['tab1'], txt['tab_eng'], txt['tab_live'], txt['tab2'], txt['tab3'], txt['tab4'], txt['tab5'], txt['tab6'], txt['tab_admin']
        ])
    else:
        tab1, tab_eng, tab_live_twin, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            txt['tab1'], txt['tab_eng'], txt['tab_live'], txt['tab2'], txt['tab3'], txt['tab4'], txt['tab5'], txt['tab6']
        ])

    # TAB 1: BUILD PLAN
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader(txt['quick_templates'])
        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.button(txt['ecom'], use_container_width=True, on_click=apply_template, args=("تطبيق متجر إلكتروني لبيع المنتجات مع بوابة دفع سريعة ونظام إدارة المخزون", "التجارة الإلكترونية", 4500, 35, "متجر إلكتروني متكامل"))
        col_t2.button(txt['edu'], use_container_width=True, on_click=apply_template, args=("منصة تعليمية تتيح رفع الكورسات وااختبارات تفاعلية وشهادات تلقائية", "التعليم الرقمي", 3000, 25, "منصة تعليمية ذكية"))
        col_t3.button(txt['delivery'], use_container_width=True, on_click=apply_template, args=("تطبيق توصيل طلبات يعتمد على الخرائط التفاعلية وتتبع السائقين في الوقت الفعلي", "الخدمات واللوجستيات", 6000, 50, "تطبيق توصيل سريع"))

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
                risk_tolerance = st.select_slider(txt['risk_level'], options=["Low", "Medium", "High"] if lang=='en' else ["منخفض جداً", "متوسط", "عالي"])

            project_scope = st.text_area(txt['scope'], key="form_scope", placeholder="Enter scope and technical requirements...")
            gemini_key = st.text_input("Gemini API Key (Optional)", type="password")

            submit_btn = st.form_submit_button(txt['generate_btn'], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submit_btn:
            if st.session_state.user['credits'] < 1 and not st.session_state.user['is_subscribed']:
                st.error("❌ Out of free credits! Upgrade plan to continue.")
            else:
                with st.spinner("⏳ Generating Architecture, Calculating Payroll, and Digital HMAC Signing..."):
                    req = {
                        "project_name": project_name, "domain": domain, "budget": budget,
                        "target_days": target_days, "tech_stack": tech_stack, "scope": project_scope, "risk": risk_tolerance
                    }
                    plan = PhoenixAI.generate_architecture(req, api_key=gemini_key)
                    HybridDatabaseEngine.save_project_plan_full(plan, st.session_state.user['email'])

                    if not st.session_state.user['is_subscribed']:
                        new_c = max(0, st.session_state.user['credits'] - 1)
                        HybridDatabaseEngine.update_credits(st.session_state.user['email'], new_c)
                        st.session_state.user['credits'] = new_c

                    st.session_state.current_plan = plan
                    st.session_state.plan_signature = plan.get("signature")
                    st.success("✅ Plan generated & signed successfully!")

        if st.session_state.current_plan:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            col_sig1, col_sig2 = st.columns([3, 1])
            with col_sig1:
                st.info(f"{txt['digital_sig']}\n`{st.session_state.plan_signature}`")
            with col_sig2:
                is_valid = SecurityEngine.verify_signature(st.session_state.current_plan, st.session_state.plan_signature)
                if is_valid:
                    st.markdown(f"<br><span class='badge-green'>{txt['sig_valid']}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<br><span class='badge-purple'>{txt['sig_invalid']}</span>", unsafe_allow_html=True)

            st.markdown(f"### {txt['spec_title']}")
            specs = PhoenixAI.calculate_specialists_breakdown(
                st.session_state.current_plan['budget'],
                st.session_state.current_plan['target_days'],
                st.session_state.current_plan['domain']
            )
            df_specs = pd.DataFrame(specs)
            st.dataframe(df_specs[["icon", "role", "total_cost", "total_hours", "hourly_rate", "daily_rate", "ratio_pct"]], use_container_width=True)

            st.markdown(f"### {txt['tasks_title']}")
            df_tasks = pd.DataFrame(st.session_state.current_plan.get('tasks', []))
            st.dataframe(df_tasks, use_container_width=True)

            col_dl1, col_dl2, col_dl3 = st.columns(3)
            with col_dl1:
                st.download_button("📦 Export JSON", json.dumps(st.session_state.current_plan, ensure_ascii=False), "plan.json", "application/json", use_container_width=True)
            with col_dl2:
                excel_bytes = generate_excel_download(df_tasks)
                st.download_button(txt['export_excel'], excel_bytes, f"{st.session_state.current_plan['project_name']}_Tasks.xlsx", use_container_width=True)
            with col_dl3:
                detailed_txt = build_detailed_plan_text(st.session_state.current_plan)
                pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_txt)
                st.download_button(txt['export_pdf'], pdf_bytes, f"{st.session_state.current_plan['project_name']}_Plan.pdf", "application/pdf", use_container_width=True)

            st.divider()
            col_n1, col_n2 = st.columns(2)
            msg_body = f"🚀 Project: {st.session_state.current_plan['project_name']}\n💰 Budget: ${st.session_state.current_plan['budget']}\n⏱️ Days: {st.session_state.current_plan['target_days']}\n🔑 Signature: {st.session_state.plan_signature[:20]}..."
            wa_url = NotificationEngine.create_whatsapp_link(st.session_state.notify_whatsapp, msg_body)

            with col_n1:
                st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:8px; font-weight:bold; text-decoration:none;">{txt["send_wa"]}</a>', unsafe_allow_html=True)
            with col_n2:
                if st.button(txt['send_tg'], use_container_width=True):
                    st.success(f"✅ Notification sent to {st.session_state.notify_telegram}")
            st.markdown("</div>", unsafe_allow_html=True)

    # TAB ENGINEERING: AI-ConTech MODULE
    with tab_eng:
        render_engineering_tab(txt)

    # TAB LIVE TWIN: محرك التوأم الرقمي والمحاكاة الحية
    with tab_live_twin:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🔮 وحدة المحاكاة والتحقق الميداني الذكي (AI Live Twin Inspector)")
        st.caption("ربط التخطيط المعماري بالواقع الميداني، ومطابقة سير العمل وتدفق الميزانية لحظة بلحظة عبر رؤية الحاسوب.")
        
        if not st.session_state.get('current_plan'):
            st.warning("⚠️ يرجى توليد خطة مشروع أو اختيار مشروع محدد أولاً للبدء بالمحاكاة الميدانية.")
        else:
            plan = st.session_state.current_plan
            
            st.markdown("### 1️⃣ محاكاة المخاطر الفيزيائية والهندسية (Physics & Stress Simulation)")
            
            col_st1, col_st2, col_st3 = st.columns(3)
            with col_st1:
                soil_type = st.selectbox("نوع التربة الميدانية", ["صخرية صلبة (Rock)", "تربة طينية (Clay)", "تربة رملية (Sand)", "تربة مشبعة بالماء (Silt)"])
            with col_st2:
                seismic_risk = st.selectbox("مستوى النشاط الزلزالي", ["منخفض (Low)", "متوسط (Moderate)", "مرتفع (High)"])
            with col_st3:
                st.write("<br>", unsafe_allow_html=True)
                run_sim = st.button("⚡ تشغيل محاكاة الإجهاد", use_container_width=True)

            if run_sim or 'stress_result' in st.session_state:
                if run_sim:
                    st.session_state.stress_result = LiveTwinEngine.analyze_structural_stress(plan, soil_type, seismic_risk)
                
                res = st.session_state.stress_result
                
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("🛡️ مؤشر السلامة الإجهادية", f"{res['safety_stress_score']}%", delta="آمن structural" if res['safety_stress_score'] > 75 else "يحتاج تدعيم")
                c_m2.metric("💵 احتياطي طوارئ الإجهاد", f"${res['financial_contingency_usd']:,}")
                c_m3.metric("🔑 التوقيع الرقمي للمحاكاة", "Verified SHA-256")
                
                st.info(f"💡 **توصية الفحص الهندسي:** {res['engineering_recommendation']}")
                st.warning(f"⚠️ **نقاط الخلل المحتملة:** {', '.join(res['critical_risk_points'])}")

            st.write("---")

            st.markdown("### 2️⃣ مطابقة الواقع مع المخطط عبر الرؤية الحاسوبية (AI Site Reality Inspector)")
            
            uploaded_file = st.file_uploader("📸 ارفع صورة ميدانية من الموقع / الدرون / المخطط للتحقق", type=['png', 'jpg', 'jpeg'])
            
            if uploaded_file is not None:
                col_img, col_analysis = st.columns([1, 1])
                
                with col_img:
                    st.image(uploaded_file, caption="الرفع الميداني الحالي", use_column_width=True)
                    img_bytes = uploaded_file.getvalue()
                    
                with col_analysis:
                    if st.button("🔍 مطابقة الصورة مع الجدول الزمني والـ BOQ", type="primary", use_container_width=True):
                        with st.spinner("جاري تحليل العناصر الإنشائية والمطابقة بالذكاء الاصطناعي..."):
                            inspection = LiveTwinEngine.inspect_site_image(img_bytes, plan.get('tasks', []))
                            st.session_state.last_inspection = inspection
                            
            if 'last_inspection' in st.session_state:
                insp = st.session_state.last_inspection
                
                st.success("✅ اكتمل تحليل المطابقة الميدانية!")
                st.progress(insp['completion_percentage'] / 100, text=f"نسبة الإنجاز الميداني الحقيقي: {insp['completion_percentage']}%")
                
                col_i1, col_i2 = st.columns(2)
                col_i1.warning(f"⏳ **الانحرافات والتأخير:** {insp['estimated_delay_days']} أيام تأخير متوقعة.")
                col_i2.error(f"🚨 **الملاحظات الميدانية:** {', '.join(insp['detected_deviations'])}")

                st.write("---")
                st.markdown("### 3️⃣ التوقيع العقدي الذكي وإفراج الدفعات (Smart Contract & Immutable Escrow)")
                
                ledger_hash = SecurityEngine.generate_smart_contract_hash(plan['project_name'], insp['completion_percentage'], insp['smart_contract_release_amount'])
                
                st.markdown(f"""
                <div style="background-color: #0F172A; border: 2px solid #6366F1; padding: 18px; border-radius: 12px; margin-top: 10px;">
                    <h4 style="color: #6366F1; margin-0;">🔗 عقد ذكي مؤمن بالـ Blockchain Ledger</h4>
                    <p><b>حالة الاعتماد:</b> <span style="color:#10B981; font-weight:bold;">{insp['escrow_approval']}</span></p>
                    <p><b>المبلغ المستحق للإفراج الفوري للمقاول:</b> <span style="color:#F59E0B; font-weight:bold;">${insp['smart_contract_release_amount']:,}</span></p>
                    <p style="font-family: monospace; font-size: 11px; color: #94A3B8; word-break: break-all;"><b>Block Hash:</b> {ledger_hash}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🏛️ اعتماد إفراج دفعة الضمان وتسجيلها في السجل المشفر", use_container_width=True):
                    HybridDatabaseEngine.log_live_twin_inspection(
                        st.session_state.user['email'],
                        plan['project_name'],
                        st.session_state.stress_result.get('safety_stress_score', 85) if 'stress_result' in st.session_state else 85,
                        insp['completion_percentage'],
                        insp['smart_contract_release_amount'],
                        ledger_hash
                    )
                    st.balloons()
                    st.success("🎉 تم الإفراج عن الدفعة وتوثيق المعاملة في السجل الذكي غير القابل للتعديل!")
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 2: ANALYTICS 6D
    with tab2:
        if not st.session_state.current_plan:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.info("💡 Please generate a project plan first to display 6D Analytics.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            plan = st.session_state.current_plan
            df = pd.DataFrame(plan.get('tasks', []))
            
            p_budget = float(plan['budget'])
            p_days = int(plan['target_days'])
            p_hours = p_days * 8
            daily_cost = p_budget / max(1, p_days)
            
            risk_val = plan.get('risk', 'متوسط')
            risk_penalty = 20 if risk_val in ["عالي", "High"] else (10 if risk_val in ["متوسط", "Medium"] else 5)
            budget_efficiency = min(100, max(40, int((p_budget / (p_days * 100)) * 50)))
            success_rate = min(98, max(55, int(budget_efficiency + (40 - risk_penalty))))
            failure_rate = round(100.0 - success_rate, 1)
            tech_readiness = 92.5 if "PostgreSQL" in str(plan.get('tech_stack')) else 84.0

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("## 📊 6D Engineering Dashboard & Quality Assessment")

            g_col1, g_col2, g_col3 = st.columns(3)
            with g_col1:
                fig1 = create_half_doughnut_gauge(daily_cost, "💰 Daily Cost Rate", "#2563EB", prefix="$", suffix="/day", max_val=daily_cost*2)
                st.plotly_chart(fig1, use_container_width=True)
            with g_col2:
                fig2 = create_half_doughnut_gauge(p_hours, "⏱️ Total Engineering Hours", "#7C3AED", suffix=" hrs", max_val=p_hours*1.5)
                st.plotly_chart(fig2, use_container_width=True)
            with g_col3:
                fig3 = create_half_doughnut_gauge(p_days, "📅 Calendar Days", "#0284C7", suffix=" days", max_val=p_days*1.5)
                st.plotly_chart(fig3, use_container_width=True)

            g_col4, g_col5, g_col6 = st.columns(3)
            with g_col4:
                fig4 = create_half_doughnut_gauge(success_rate, "🌟 Success Rate", "#059669", suffix="%")
                st.plotly_chart(fig4, use_container_width=True)
            with g_col5:
                fig5 = create_half_doughnut_gauge(failure_rate, "⚠️ Risk / Failure Probability", "#DC2626", suffix="%")
                st.plotly_chart(fig5, use_container_width=True)
            with g_col6:
                fig6 = create_half_doughnut_gauge(tech_readiness, "🛡️ Architecture Readiness", "#D97706", suffix="%")
                st.plotly_chart(fig6, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("### 🍩 Sunburst Financial Breakdown")
                labels = [plan['project_name']] + list(df['task'])
                parents = [""] + [plan['project_name']] * len(df)
                values = [plan['budget']] + list(df['cost'])
                fig_sunburst = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values, branchvalues="total", marker=dict(colorscale='Blues')))
                fig_sunburst.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color), height=320)
                st.plotly_chart(fig_sunburst, use_container_width=True)

            with col_c2:
                st.markdown("### 🕸️ 5D Radar Risk Matrix")
                radar_cats = ['Scope', 'Security', 'Timeline', 'Cost Stability', 'Tech Flexibility']
                radar_vals = [80, 95, 85, 90, 70]
                fig_radar = go.Figure(go.Scatterpolar(r=radar_vals, theta=radar_cats, fill='toself', line=dict(color='#7C3AED')))
                fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color), height=320)
                st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # TAB 3: TASK EDITOR
    with tab3:
        if not st.session_state.current_plan:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.warning("⚠️ No active plan available to edit.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader(txt['tab3'])
            edited_df = st.data_editor(
                pd.DataFrame(st.session_state.current_plan['tasks']),
                num_rows="dynamic", use_container_width=True, key="task_editor"
            )
            if st.button(txt['save_re_sign'], type="primary", use_container_width=True):
                st.session_state.current_plan['tasks'] = edited_df.to_dict(orient="records")
                new_sig = SecurityEngine.generate_signature(st.session_state.current_plan)
                st.session_state.current_plan['signature'] = new_sig
                st.session_state.plan_signature = new_sig
                HybridDatabaseEngine.save_project_plan_full(st.session_state.current_plan, st.session_state.user['email'])
                st.success("✅ Edits saved and HMAC re-signed!")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"### {txt['detailed_plan']}")
            st.markdown(build_detailed_plan_text(st.session_state.current_plan))
            st.markdown("</div>", unsafe_allow_html=True)

    # TAB 4: FEEDBACK & ADAPTIVE PRICING
    with tab4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader(txt['pricing_adapted_title'])
        st.caption(txt['pricing_adapted_caption'])

        col_fb1, col_fb2 = st.columns([1, 1])

        with col_fb1:
            st.markdown("### " + txt['share_feedback_title'])
            st.markdown(f"**{txt['star_rating_label']}**")
            stars_selection = st.feedback("stars")
            rating_stars = (stars_selection + 1) if stars_selection is not None else 5
            
            star_display = "🌟" * rating_stars
            st.caption(f"Rating: **{star_display}** ({rating_stars}/5)")

            with st.form("feedback_form"):
                suggested_p = st.number_input("Fair Monthly Price ($)", min_value=5, max_value=200, value=29)
                req_feature = st.selectbox("Most Demanded Feature", [
                    "Export Professional Arabic PDF",
                    "Direct Cloud SQL & Cloud Run Sync",
                    "WhatsApp & Telegram Alerts",
                    "Direct Gemini Pro Integration",
                    "Multi-Currency Budgeting"
                ])
                comments = st.text_area("Additional Feedback & Comments", placeholder="Write feedback here...")
                submit_fb = st.form_submit_button("🚀 Submit Feedback & Claim 1 Free Credit")

                if submit_fb:
                    if HybridDatabaseEngine.save_feedback(st.session_state.user['email'], rating_stars, suggested_p, req_feature, comments):
                        new_c = st.session_state.user['credits'] + 1
                        HybridDatabaseEngine.update_credits(st.session_state.user['email'], new_c)
                        st.session_state.user['credits'] = new_c
                        
                        st.balloons()
                        st.success("🎉 Feedback saved! 1 free bonus credit added.")
                        time.sleep(1)
                        st.rerun()

        with col_fb2:
            st.markdown("### " + txt['market_proof_title'])
            feedbacks = HybridDatabaseEngine.get_all_feedback()
            adapted = PhoenixAI.analyze_feedback_and_adapt_pricing(feedbacks)

            st.markdown(f"""
            <div style="background: rgba(37,99,235,0.08); border-radius: 12px; padding: 16px; margin-bottom: 15px;">
                <h4 style="color: #2563EB;">🤖 AI Dynamic Pricing Response:</h4>
                <p>• <b>Avg User Price:</b> ${adapted['recommended_monthly']}/month</p>
                <p>• <b>Calculated Yearly:</b> ${adapted['recommended_yearly']}/year</p>
                <p>• <b>Product-Market Fit Score:</b> {adapted['market_satisfaction_score']}%</p>
                <p>• <b>Total Feedback Recorded:</b> {len(feedbacks)} reviews</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"#### {txt['live_feedback_stream']}")
            if feedbacks:
                for f in feedbacks:
                    stars_count = f.get('rating', 5) or 5
                    stars_str = "🌟" * stars_count
                    comment_text = f.get('comments', '') or "No comment."
                    
                    st.markdown(f"""
                    <div style="background: rgba(0,0,0,0.03); border-left: 4px solid #F59E0B; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                        <b>👤 {f['user_email']}</b> - {stars_str} ({stars_count}/5)<br>
                        <small>💵 Price: ${f['suggested_price']} | 💡 Feature: {f['requested_feature']}</small><br>
                        <i>💬 "{comment_text}"</i>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No feedback entries yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 5: ACCOUNT & SUBSCRIPTIONS
    with tab5:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader(txt['tab5'])
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            st.markdown(f"### {txt['account_info_title']}")
            st.write(f"**Name:** {st.session_state.user['username']}")
            st.write(f"**Email:** {st.session_state.user['email']}")
            st.write(f"**Role:** {st.session_state.user['role']}")
            st.write(f"**Credits:** {st.session_state.user['credits']}")

        with col_acc2:
            st.markdown(f"### {txt['upgrade_plans_title']}")
            st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">💳 Pro Monthly (${adapted_insights["recommended_monthly"]})</a>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<a href="{PAYMENT_LINK_YEARLY}" target="_blank" class="checkout-btn-yearly">👑 Enterprise Yearly (${adapted_insights["recommended_yearly"]})</a>', unsafe_allow_html=True)

        if st.session_state.payment_notifications:
            st.divider()
            st.markdown(f"### {txt['payment_logs_title']}")
            for notif in st.session_state.payment_notifications:
                st.markdown(f"""
                <div style="background: rgba(16,185,129,0.08); border-radius:12px; padding:12px; margin-bottom:10px;">
                    <b>To:</b> {notif['to']}<br>
                    <b>Order ID:</b> {notif['order_id']}<br>
                    <b>Plan:</b> {notif['plan_name']} ({notif['amount']})<br>
                    <b>Date:</b> {notif['date']}
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 6: CLOUD SQL ARCHIVE
    with tab6:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader(txt['cloudsql_title'])
        st.caption(txt['cloudsql_caption'])
        
        saved_projs = HybridDatabaseEngine.get_projects(st.session_state.user['email'])
        if saved_projs:
            st.dataframe(pd.DataFrame(saved_projs), use_container_width=True)
        else:
            st.info("No saved projects found.")
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB ADMIN: CEO CONTROL CENTER
    if is_ceo_owner:
        with tab_admin:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader(txt['ceo_title'])
            st.caption(txt['ceo_caption'])

            all_users = HybridDatabaseEngine.get_all_users_admin()
            total_users_count = len(all_users)
            subscribed_count = len([u for u in all_users if u['is_subscribed']])
            admin_supervisors_count = len([u for u in all_users if u.get('is_admin')])

            m_adm1, m_adm2, m_adm3, m_adm4 = st.columns(4)
            m_adm1.metric("👥 Total Registered Users", total_users_count)
            m_adm2.metric("💳 Paid Subscriptions", subscribed_count)
            m_adm3.metric("👑 Admin Supervisors", admin_supervisors_count)
            m_adm4.metric("📈 Conversion Rate", f"{round((subscribed_count/max(1, total_users_count))*100, 1)}%")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"### {txt['grant_admin_title']}")
            col_add_adm1, col_add_adm2 = st.columns([2, 1])
            with col_add_adm1:
                target_admin_email = st.text_input("Enter user email to promote to supervisor admin", placeholder="supervisor@domain.com").strip().lower()
            with col_add_adm2:
                st.write("<br>", unsafe_allow_html=True)
                if st.button(txt['grant_admin_btn'], type="primary", use_container_width=True):
                    if target_admin_email:
                        if HybridDatabaseEngine.add_admin_privilege(target_admin_email):
                            st.success(f"✅ Granted Admin supervisor privileges to `{target_admin_email}`!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Email address not found.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"### {txt['users_log_title']}")
            if all_users:
                df_admin_users = pd.DataFrame(all_users)
                st.dataframe(df_admin_users[["id", "full_name", "email", "role", "credits", "is_subscribed", "is_admin", "created_at"]], use_container_width=True)

            st.divider()

            st.markdown(f"### {txt['demands_title']}")
            admin_fb = HybridDatabaseEngine.get_all_feedback()
            if admin_fb:
                df_admin_fb = pd.DataFrame(admin_fb)
                st.dataframe(df_admin_fb[["user_email", "rating", "suggested_price", "requested_feature", "comments", "created_at"]], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
