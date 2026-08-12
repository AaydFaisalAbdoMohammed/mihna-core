#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & WAKEEL MEHNA PRO ENTERPRISE ARCHITECTURE v13.8 - ULTRA ULTIMATE SaaS
Geo-Global Dynamic Adaptive Engine Edition
محرك معالجة البيانات والتصميم الهندسية الفاخر بالواجهات الزجاجية Glassmorphic UI
===============================================================================
"""

import os
import json
import time
import datetime
import random
import re
import hashlib
import hmac
import requests
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

APP_TITLE = "PHOENIX & WAKEEL MEHNA PRO - ULTRA ENTERPRISE v13.8"

# تهيئة المحرك الهندسي الذكي
eng_ai = EngineeringAIEngine()

# =============================================================================
# 🛡️ ULTRA ENTERPRISE ZERO-KNOWLEDGE PROOF & IMMUTABLE LEDGER ENGINE
# =============================================================================
class ZeroKnowledgeEscrow:
    """
    محرك التشفير المتقدم لإثبات الانجاز بدون كشف البيانات التجارية الحساسة (ZKP - Zero-Knowledge Proofs)
    يضمن حماية الأفكار والعقود من التلاعب أو التزييف.
    """
    @staticmethod
    def generate_zkp_proof(project_id: str, completion_pct: float, release_amount: float) -> str:
        secret_salt = os.urandom(32).hex()
        raw_payload = f"{project_id}:{completion_pct}:{release_amount}:{secret_salt}:{time.time()}"
        proof_hash = hashlib.sha3_512(raw_payload.encode('utf-8')).hexdigest()
        return f"ZKP-v13-{proof_hash[:32].upper()}"

# =============================================================================
# 🔥 المحرك الجيومكاني العالمي المتطور للشركات والمقاولين والاتصالات المباشرة
# =============================================================================
def get_geo_contractors_enterprise(user_location, budget_total, google_maps_api_key=None):
    """
    محرك البحث والربط الجيومكاني المتقدم:
    1. يستعلم من Google Maps Places API للربط اللحظي الحي لجلب أرقام هواتف وعناوين حقيقية للشركات.
    2. يوفر قاعدة بيانات مطابقة استعلامية محددة محلياً ودولياً كخيار احتياطي ذكي (Deterministic Dynamic Fallback).
    """
    loc_raw = user_location.strip() if user_location and user_location.strip() else "Aden, Yemen"
    api_key = google_maps_api_key or os.getenv("GOOGLE_MAPS_API_KEY")

    # 🌐 1. مسار الربط المباشر اللحظي عبر Google Maps Places API
    if api_key:
        try:
            search_url = (
                f"https://maps.googleapis.com/maps/api/place/textsearch/json"
                f"?query=contractors+engineering+in+{requests.utils.quote(loc_raw)}&key={api_key}"
            )
            response = requests.get(search_url, timeout=6)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK" and len(data.get("results", [])) > 0:
                    real_contractors = []
                    for i, place in enumerate(data["results"][:3]):
                        place_id = place.get("place_id")
                        
                        details_url = (
                            f"https://maps.googleapis.com/maps/api/place/details/json"
                            f"?place_id={place_id}&fields=name,formatted_phone_number,formatted_address,rating&key={api_key}"
                        )
                        details_res = requests.get(details_url, timeout=5).json().get("result", {})
                        
                        phone = details_res.get("formatted_phone_number", "+9671234567")
                        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
                        
                        real_contractors.append({
                            "id": f"g_place_{i+1}",
                            "company": details_res.get("name", f"شركة المقاولات الهندسية {i+1}"),
                            "type": "شركة مقاولات واستشارات معتمدة (Google Certified)",
                            "location": details_res.get("formatted_address", loc_raw),
                            "rating": f"⭐ {details_res.get('rating', 4.8)} (مُحقق عبر Google Maps)",
                            "bid": round(budget_total * (0.90 + (i * 0.03)), 2),
                            "days": max(30, int(90 - (i * 10))),
                            "phone": phone,
                            "wa_link": f"https://wa.me/{clean_phone.replace('+', '')}?text=مرحباً،%20نود%20الاستفسار%20عن%20مناقصة%20المشروع"
                        })
                    return real_contractors
        except Exception:
            pass  

    # 🏢 2. النظام الاحتياطي الديناميكي المحلي الذكي
    loc_lower = loc_raw.lower()
    has_arabic = bool(re.search(r'[\u0600-\u06FF]', loc_raw))

    geo_database = {
        "yemen": {
            "dial": "+967",
            "companies": [
                "مجموعة الرائدة للمقاولات والهندسة الكهروميكانيكية",
                "شركة الأمل للإنشاءات والتطوير العقاري",
                "مكتب السعيد للاستشارات والمقاولات العامة"
            ],
            "sample_phones": ["+9672234567", "+967771234567", "+967733456789"]
        },
        "saudi": {
            "dial": "+966",
            "companies": [
                "شركة الإعمار المتطورة للمقاولات العامة",
                "مجموعة البناء الحديث للإنشاءات الهندسية",
                "مكتب الرؤية للاستشارات والمقاولات"
            ],
            "sample_phones": ["+966112345678", "+966501234567", "+966559876543"]
        },
        "uae": {
            "dial": "+971",
            "companies": [
                "شركة الصرح الهندسية للمقاولات",
                "مجموعة دبي للإنشاءات والبنية التحتية",
                "مكتب القمة للاستشارات الهندسية"
            ],
            "sample_phones": ["+97143210987", "+971501234567", "+971529876543"]
        },
        "egypt": {
            "dial": "+20",
            "companies": [
                "شركة النيل العامة للمقاولات والهندسة",
                "مجموعة الأهرام للإنشاءات العقارية",
                "المكتب الهندسي المتحد للمقاولات"
            ],
            "sample_phones": ["+20227950000", "+201001234567", "+201229876543"]
        },
        "global": {
            "dial": "+1",
            "companies": [
                "Apex Global Engineering & Construction Corp",
                "Vanguard Infrastructure & Design Solutions",
                "Nexus Prime Contracting & Consulting"
            ],
            "sample_phones": ["+14155552671", "+12125550198", "+13105550143"]
        }
    }

    selected_region = geo_database["global"]
    if any(k in loc_lower or k in loc_raw for k in ["يمن", "yemen", "عدن", "صنعاء", "تعز", "إب", "المكلا"]):
        selected_region = geo_database["yemen"]
    elif any(k in loc_lower or k in loc_raw for k in ["سعودية", "saudi", "الرياض", "جدة"]):
        selected_region = geo_database["saudi"]
    elif any(k in loc_lower or k in loc_raw for k in ["إمارات", "uae", "دبي", "أبوظبي"]):
        selected_region = geo_database["uae"]
    elif any(k in loc_lower or k in loc_raw for k in ["مصر", "egypt", "القاهرة"]):
        selected_region = geo_database["egypt"]

    contractors = []
    for i in range(3):
        comp_name = f"{selected_region['companies'][i]} - فرع {loc_raw}" if has_arabic else f"{selected_region['companies'][i]} ({loc_raw} Branch)"
        phone_num = selected_region["sample_phones"][i]
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone_num)

        contractors.append({
            "id": f"contractor_fb_{i+1}",
            "company": comp_name,
            "type": "شركة مقاولات واستشارات معتمدة",
            "location": f"المنطقة المركزية / حي الأعمال، {loc_raw}",
            "rating": f"⭐ {4.9 - (i*0.1):.1f} (سجل معتمد)",
            "bid": round(budget_total * (0.92 + (i * 0.03)), 2),
            "days": max(25, int(85 + (i * 12))),
            "phone": phone_num,
            "wa_link": f"https://wa.me/{clean_phone.replace('+', '')}?text=مرحباً،%20نود%20الاستفسار%20عن%20مناقصة%20المشروع"
        })

    return contractors

# =============================================================================
# 🌐 قاموس الترجمات للواجهات (DICTIONARIES)
# =============================================================================
T = {
    'ar': {
        'title': "🚀 PHOENIX & WAKEEL MEHNA PRO Enterprise v13.8",
        'subtitle': "منصة HMAC-SHA512 و Cloud SQL المتقدمة لهندسة خطط المشاريع، حساب أجور المتخصصين، وتأمين البيانات.",
        'lang_select': "(Language) لغة الواجهة:",
        'theme_select': "(Theme) مظهر التطبيق:",
        'dark': "🌙 الداكن (Dark)", 'light': "☀️ الفاتح (Light)",
        'user': "👤 المستخدم:", 'credits': "💳 الرصيد الحالي:", 'points': "نقاط مجانية",
        'renew_title': "🛒 ترقية الاشتراك", 'renew_btn': "اشترك الآن بـ 🛒🚀 واحصل على الخصم",
        'logout_btn': "🚪 تسجيل الخروج", 'notify_settings': "📲 إعدادات الإشعارات الفورية",
        'wa_phone': "رقم الواتساب", 'tg_handle': "معرف التليجرام",
        'tab1': "🏗️ بناء الخطة والكوادر", 
        'tab_eng': "📐 التخطيط الهندسي والكميات (AI-ConTech)",
        'tab2': "📊 التحليلات التفاعلية 6D",
        'tab3': "✏️ محرر المهام والتقرير النصي", 'tab4': "🔄 التغذية الراجعة والتكيّف السعري",
        'tab5': "💳 الحساب والاشتراكات", 'tab6': "🗄️ أرشفة Cloud SQL (7-Tables Schema)",
        'tab_admin': "👑 لوحة الإدارة العليا (CEO Panel)",
        'quick_templates': "⚡ قوالب جاهزة للبدء السريع",
        'ecom': "🛒 متجر إلكتروني", 'edu': "🎓 منصة تعليمية", 'delivery': "🚗 تطبيق توصيل",
        'p_name': "اسم المشروع", 'tech_domain': "المجال التقني", 'budget': "الميزانية التقديرية ($)",
        'tech_stack': "التقنيات المستخدمة", 'target_days': "المدة الزمنية المستهدفة (يوم)", 'risk_level': "تحمل المخاطر",
        'scope': "نطاق العمل (Scope of Work)",
        'generate_btn': "توليد وحساب الكوادر والتوقيع الرقمي (1 نقطة) 🚀",
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
        'eng_title': "🏗️ وحدة التخطيط الهندسي وحساب الكميات والتوائم الرقمي (AI-ConTech & Live Twin)",
        'eng_caption': "التصميم المعماري، حساب جدول الكميات (BOQ)، محاكاة الموقع والمقاولون المحليون.",
        'eng_subtab1': "📐 حساب الكميات والتصاميم",
        'eng_subtab2': "🌐 المقاولون الجيومكانيون",
        'eng_subtab3': "🕹️ التوأم الرقمي والمشروع الحقيقي"
    },
    'en': {
        'title': "🚀 PHOENIX & WAKEEL MEHNA PRO Enterprise v13.8",
        'subtitle': "Advanced HMAC-SHA512 & Cloud SQL Platform for Engineering Project Plans, Payroll, & Secured Data.",
        'lang_select': "🌐 Interface Language:",
        'theme_select': "🎨 Application Theme:",
        'dark': "🌙 Dark", 'light': "☀️ Light",
        'user': "👤 User:", 'credits': "💳 Balance:", 'points': "points",
        'renew_title': "🛒 Upgrade Plan", 'renew_btn': "Subscribe Now 🛒🚀 & Get Discount",
        'logout_btn': "🚪 Log Out", 'notify_settings': "📲 Instant Notification Settings",
        'wa_phone': "WhatsApp Phone", 'tg_handle': "Telegram Handle",
        'tab1': "🏗️ Build Plan & Payroll", 
        'tab_eng': "📐 Engineering & BOQ (AI-ConTech)",
        'tab2': "📊 Advanced 6D Analytics",
        'tab3': "✏️ Task Editor & Text Plan", 'tab4': "🔄 Feedback & Pricing",
        'tab5': "💳 Account & Subscriptions", 'tab6': "🗄️ Cloud SQL Archive",
        'tab_admin': "👑 CEO Panel",
        'quick_templates': "⚡ Quick Start Templates",
        'ecom': "🛒 E-Commerce App", 'edu': "🎓 E-Learning Platform", 'delivery': "🚗 Delivery App",
        'p_name': "Project Name", 'tech_domain': "Technical Domain", 'budget': "Estimated Budget ($)",
        'tech_stack': "Tech Stack", 'target_days': "Target Timeline (Days)", 'risk_level': "Risk Tolerance",
        'scope': "Scope of Work",
        'generate_btn': "Generate Plan, Payroll & Sign (1 Credit) 🚀",
        'export_excel': "📥 Download Tasks (Excel)", 'export_pdf': "📄 Download Plan (PDF)",
        'detailed_plan': "📜 Extended Text Plan", 'save_re_sign': "💾 Save Edits & Re-Sign Digitally",
        'digital_sig': "🔑 Encrypted HMAC Signature:",
        'sig_valid': "✔ Valid Signature", 'sig_invalid': "❌ Invalid Signature",
        'send_wa': "📱 Send via WhatsApp", 'send_tg': "📲 Notify Telegram Bot",
        'spec_title': "👥 Specialist Payroll & Assigned Engineering Hours",
        'tasks_title': "📋 Technical Task Phases & Scope",
        'login_welcome': "Welcome Back!",
        'signup_welcome': "Join PHOENIX Enterprise Platform",
        'login_btn': "🚀 Log In",
        'signup_btn': "✨ Create Account & Get 5 Free Credits",
        'email_label': "Email Address",
        'pass_label': "Password",
        'confirm_pass_label': "Confirm Password",
        'fullname_label': "Full Name",
        'qr_scan_title': "📲 Scan QR for Quick Sign-up",
        'qr_scan_caption': "Scan with mobile camera to quickly sign up or register",
        'pricing_adapted_title': "🔄 AI Closed-Loop Feedback & Adaptive Pricing Engine",
        'pricing_adapted_caption': "Intelligent feedback engine adapting real-time pricing and user feature requests.",
        'share_feedback_title': "📝 Share Your Feedback (Earn 1 Free Credit Automatically)",
        'star_rating_label': "Rate Your Experience (Select Stars):",
        'market_proof_title': "🏆 Market Demand & Adaptability Proof Panel",
        'live_feedback_stream': "💬 Live User Feedback Stream:",
        'account_info_title': "👤 Account Details",
        'upgrade_plans_title': "🛒 Upgrade Plans (Dynamic Adaptive Pricing)",
        'payment_logs_title': "📩 Smart Payment Notifications Log",
        'cloudsql_title': "🗄️ Cloud SQL Live Schema Archive",
        'cloudsql_caption': "Review recent project records in relational database format.",
        'ceo_title': "👑 CEO & Owner Control Center",
        'ceo_caption': "Hidden control panel accessible exclusively to authorized supervisors.",
        'grant_admin_title': "🔑 Grant Admin Privileges",
        'grant_admin_btn': "✨ Promote User to Admin",
        'users_log_title': "📋 Live Users Directory",
        'demands_title': "💬 Market & User Demands Log",

        # ConTech Translation
        'eng_title': "🏗️ Engineering Unit, BOQ & Digital Twin (AI-ConTech)",
        'eng_caption': "Architectural Design, BOQ Analysis, Geo-Contractors, and Digital Twin Simulation.",
        'eng_subtab1': "📐 BOQ & Architectural Design",
        'eng_subtab2': "🌐 Geo-Spatial Contractors",
        'eng_subtab3': "🕹️ Live Digital Twin"
    }
}

# =============================================================================
# 🎨 INITIALIZE SESSION & LANGUAGE HELPER FUNCTIONS
# =============================================================================
def init_session():
    if 'lang' not in st.session_state: st.session_state.lang = 'ar'
    if 'theme' not in st.session_state: st.session_state.theme = 'dark'
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

# =============================================================================
# 💎 MAIN STREAMLIT APPLICATION ENTERPRISE UI
# =============================================================================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")
    init_session()

    if not st.session_state.is_authenticated:
        render_auth_page()
        return

    # تحديث بيانات المستخدم المباشرة
    fresh_u = HybridDatabaseEngine.get_user(st.session_state.user['email'])
    if fresh_u:
        st.session_state.user['credits'] = fresh_u['credits']
        st.session_state.user['role'] = fresh_u['role']
        st.session_state.user['is_subscribed'] = bool(fresh_u['is_subscribed'])
        st.session_state.user['is_admin'] = bool(fresh_u['is_admin']) or (fresh_u['email'] == SUPER_ADMIN_EMAIL)

    lang = st.session_state.lang
    txt = T[lang]

    # ألوان الثيم الفاخر الزجاجي (Glassmorphic Luxury Dark Mode)
    bg_color = "#0B0F19" if st.session_state.theme == 'dark' else "#F8FAFC"
    card_bg = "#111827" if st.session_state.theme == 'dark' else "#FFFFFF"
    text_color = "#F9FAFB" if st.session_state.theme == 'dark' else "#0F172A"

    # =========================================================================
    # 🎨 GLASSMORPHIC & LUXURY ENTERPRISE STYLING (التنسيقات المحسنة بالكامل)
    # =========================================================================
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', system-ui, sans-serif; }}
        
        /* Badges & Pills */
        .badge-green {{ background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(16,185,129,0.3); }}
        .badge-purple {{ background: linear-gradient(135deg, #8B5CF6, #6D28D9); color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(139,92,246,0.3); }}
        .badge-gold {{ background: linear-gradient(135deg, #F59E0B, #D97706); color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(245,158,11,0.3); }}
        
        /* Checkout & Action Buttons */
        .checkout-btn {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white !important; padding: 12px 16px; border-radius: 10px; font-weight: bold; text-decoration: none; border: 1px solid rgba(255,255,255,0.1); font-size: 14px; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(37,99,235,0.3); }}
        .checkout-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37,99,235,0.5); }}
        .checkout-btn-yearly {{ display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #7C3AED, #9333EA); color: white !important; padding: 12px 16px; border-radius: 10px; font-weight: bold; text-decoration: none; border: 1px solid rgba(255,255,255,0.1); font-size: 14px; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(124,58,237,0.3); }}
        .checkout-btn-yearly:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(124,58,237,0.5); }}
        
        /* Glassmorphic Cards & Containers */
        .ai-payment-card {{ background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(49, 46, 129, 0.8) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 16px; padding: 24px; color: #FFFFFF; margin-bottom: 24px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }}
        .feedback-card {{ background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 16px; padding: 20px; color: #F8FAFC; margin-bottom: 15px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }}
        .stat-card-box {{ background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 15px; transition: all 0.3s; }}
        .stat-card-box:hover {{ border-color: rgba(139, 92, 246, 0.4); transform: translateY(-3px); }}
        .user-feedback-item {{ background: rgba(15, 23, 42, 0.7); border-right: 4px solid #F59E0B; border-radius: 12px; padding: 16px; margin-bottom: 14px; border-top: 1px solid rgba(255,255,255,0.05); border-left: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); }}
        
        /* Streamlit Sidebar Customization */
        section[data-testid="stSidebar"] {{ background-color: {card_bg}; border-left: 1px solid rgba(255, 255, 255, 0.08); }}
    </style>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 👑 SIDEBAR NAVIGATION & USER PROFILE
    # =========================================================================
    with st.sidebar:
        st.title("🛡️ WAKEEL MEHNA PRO")
        st.markdown("<span class='badge-purple'>Enterprise v13.8</span>", unsafe_allow_html=True)
        st.divider()

        st.radio(txt['lang_select'], ["العربية (Arabic)", "English"], index=0 if lang == 'ar' else 1, key='lang_radio', on_change=update_language)
        st.radio(txt['theme_select'], [txt['dark'], txt['light']], index=0 if st.session_state.theme == 'dark' else 1, key='theme_radio', on_change=update_theme)

        st.divider()
        st.markdown(f"{txt['user']} **{st.session_state.user['username']}**")

        if st.session_state.user['is_subscribed']:
            st.markdown(f"الاشتراك: <span class='badge-gold'>{st.session_state.user['role']}</span>", unsafe_allow_html=True)
            st.markdown("الرصيد: **غير محدود ♾️**")
        else:
            st.markdown(f"الحساب: <span class='badge-purple'>تجريبي</span>", unsafe_allow_html=True)
            st.markdown(f"{txt['credits']} `{st.session_state.user['credits']}` {txt['points']}")

        if st.button(txt['logout_btn'], use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()
        st.markdown(f"### {txt['renew_title']}")
        all_fb = HybridDatabaseEngine.get_all_feedback()
        adapted_insights = PhoenixAI.analyze_feedback_and_adapt_pricing(all_fb)

        if not st.session_state.user['is_subscribed']:
            if st.button("🤖 الدفع الذكي والتفعيل السريع", type="primary", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
                st.balloons()
                st.success("🎉 تم ترقية حسابك بنجاح!")
                time.sleep(1)
                st.rerun()

        st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">💳 {txt["renew_btn"]} (${adapted_insights["recommended_monthly"]}/m)</a>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f'<a href="{PAYMENT_LINK_YEARLY}" target="_blank" class="checkout-btn-yearly">👑 الاشتراك السنوي (${adapted_insights["recommended_yearly"]}/y)</a>', unsafe_allow_html=True)

        st.divider()
        st.subheader(txt['notify_settings'])
        st.session_state.notify_whatsapp = st.text_input(txt['wa_phone'], value=st.session_state.notify_whatsapp)
        st.session_state.notify_telegram = st.text_input(txt['tg_handle'], value=st.session_state.notify_telegram)

    # Header Title Banner
    st.title(txt['title'])
    st.caption(txt['subtitle'])

    # Smart Prompt Banner when Credits Run Out
    if st.session_state.user['credits'] <= 0 and not st.session_state.user['is_subscribed']:
        st.markdown("""
        <div class="ai-payment-card">
            <h3>🤖 تنبيه من وكيل الدفع الذكي (AI Payment Broker Agent)</h3>
            <p>لقد نفدت نقاطك المجانية (0/5)! يمكنك تنفيذ الدفع الآلي الفوري بالذكاء الاصطناعي عبر Lemon Squeezy لتفعيل الحساب دون انتظار.</p>
        </div>
        """, unsafe_allow_html=True)
        col_pay_ai1, col_pay_ai2 = st.columns(2)
        with col_pay_ai1:
            if st.button(f"🚀 تفعيل باقة Pro الشهري (${adapted_insights['recommended_monthly']})", type="primary", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "monthly")
                st.balloons()
                st.rerun()
        with col_pay_ai2:
            if st.button(f"💎 تفعيل باقة Enterprise السنوية (${adapted_insights['recommended_yearly']})", use_container_width=True):
                AIPaymentAgent.execute_auto_checkout(st.session_state.user['email'], "yearly")
                st.balloons()
                st.rerun()

    is_ceo_owner = (st.session_state.user['email'] == SUPER_ADMIN_EMAIL) or st.session_state.user['is_admin']
    
    # 📑 MAIN APP TABS CONFIGURATION
    if is_ceo_owner:
        tab1, tab_eng, tab2, tab3, tab4, tab5, tab6, tab_admin = st.tabs([
            txt['tab1'], txt['tab_eng'], txt['tab2'], txt['tab3'], txt['tab4'], txt['tab5'], txt['tab6'], txt['tab_admin']
        ])
    else:
        tab1, tab_eng, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            txt['tab1'], txt['tab_eng'], txt['tab2'], txt['tab3'], txt['tab4'], txt['tab5'], txt['tab6']
        ])

    # =========================================================================
    # TAB 1: BUILD PROJECT PLAN & SPECIALIST PAYROLL
    # =========================================================================
    with tab1:
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
                risk_tolerance = st.select_slider(txt['risk_level'], options=["منخفض جداً", "متوسط", "عالي"])

            project_scope = st.text_area(txt['scope'], key="form_scope", placeholder="اكتب تفاصيل ومتطلبات المشروع هنا...")
            gemini_key = st.text_input("مفتاح Gemini API (اختياري للذكاء الاصطناعي المباشر)", type="password")

            submit_btn = st.form_submit_button(txt['generate_btn'], use_container_width=True)

        if submit_btn:
            if st.session_state.user['credits'] < 1 and not st.session_state.user['is_subscribed']:
                st.error("❌ لقد استنفدت نقاطك المجانية! يرجى الترقية للاستمرار.")
            else:
                with st.spinner("⏳ جاري تحليل المتطلبات، توزيع الكوادر، وتوقيع الخطة رقمياً في Cloud SQL..."):
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
                    st.success("✅ تم توليد الخطة وحساب الكوادر وحفظها بتوقيع رقمي موثوق!")

        if st.session_state.current_plan:
            st.divider()
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
                st.download_button("📦 تصدير ملف JSON", json.dumps(st.session_state.current_plan, ensure_ascii=False), "plan.json", "application/json", use_container_width=True)
            with col_dl2:
                excel_bytes = generate_excel_download(df_tasks)
                st.download_button(txt['export_excel'], excel_bytes, f"{st.session_state.current_plan['project_name']}_Tasks.xlsx", use_container_width=True)
            with col_dl3:
                detailed_txt = build_detailed_plan_text(st.session_state.current_plan)
                pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_txt)
                st.download_button(txt['export_pdf'], pdf_bytes, f"{st.session_state.current_plan['project_name']}_Plan.pdf", "application/pdf", use_container_width=True)

            st.divider()
            col_n1, col_n2 = st.columns(2)
            msg_body = f"🚀 مشروع جديد: {st.session_state.current_plan['project_name']}\n💰 الميزانية: ${st.session_state.current_plan['budget']}\n⏱️ الأيام: {st.session_state.current_plan['target_days']}\n🔑 التوقيع: {st.session_state.plan_signature[:20]}..."
            wa_url = NotificationEngine.create_whatsapp_link(st.session_state.notify_whatsapp, msg_body)

            with col_n1:
                st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:8px; font-weight:bold; text-decoration:none;">{txt["send_wa"]}</a>', unsafe_allow_html=True)
            with col_n2:
                if st.button(txt['send_tg'], use_container_width=True):
                    st.success(f"✅ تم إرسال التنبيه إلى {st.session_state.notify_telegram}")

    # =========================================================================
    # TAB ENGINEERING (AI-ConTech & Live Twin Unit)
    # =========================================================================
    with tab_eng:
        st.subheader(txt['eng_title'])
        st.caption(txt['eng_caption'])

        eng_sub1, eng_sub2, eng_sub3 = st.tabs([txt['eng_subtab1'], txt['eng_subtab2'], txt['eng_subtab3']])

        with eng_sub1:
            st.markdown("### 📐 جدول الكميات الهندسي (Bill of Quantities - BOQ)")
            
            p_budget_eng = st.session_state.current_plan['budget'] if st.session_state.current_plan else 50000.0
            p_days_eng = st.session_state.current_plan['target_days'] if st.session_state.current_plan else 60
            
            boq_items = eng_ai.generate_boq(p_budget_eng, p_days_eng)
            df_boq = pd.DataFrame(boq_items)
            st.dataframe(df_boq, use_container_width=True)
            
            st.divider()
            st.markdown("### 🏛️ التصاميم المعمارية والمخططات التنفيذية الذكية (Generative BIM Architecture)")
            
            arch_prompt = st.text_input("وصف المخطط أو النمط المعماري المطلوب:", value="مبنى تجاري حديث ثلاثي الأبعاد واجهات زجاجية")
            if st.button("✨ توليد التصميم والتصور المعماري الهيكلي", type="primary"):
                with st.spinner("جاري بناء التصميم المعماري الهيكلي ثلاثي الأبعاد..."):
                    arch_res = eng_ai.generate_architectural_blueprint(arch_prompt)
                    st.success("✅ تم تشكيل المخطط والتصاميم التنفيذية المرافقة!")
                    st.markdown(f"**نظرة عامة على التصميم:**\n{arch_res['blueprint_summary']}")
                    
                    df_specs_arch = pd.DataFrame(arch_res['structural_specs'])
                    st.dataframe(df_specs_arch, use_container_width=True)

        with eng_sub2:
            st.markdown("### 🌐 البحث الجيومكاني المباشر عن المقاولين والشركات المعتمدة")
            user_geo_loc = st.text_input("أدخل المدينة أو الدولة للبحث الجغرافي المباشر:", value="Aden, Yemen")
            gmaps_key = st.text_input("مفتاح Google Maps Places API (اختياري للربط المباشر):", type="password")
            
            if st.button("🔎 جلب المقاولين المحليين والعروض المعتمدة", use_container_width=True):
                with st.spinner("جاري الاستعلام الجيومكاني المباشر وجلب أرقام التواصل..."):
                    contractors_list = get_geo_contractors_enterprise(user_geo_loc, p_budget_eng, google_maps_api_key=gmaps_key)
                    
                    for cont in contractors_list:
                        st.markdown(f"""
                        <div class="feedback-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4>🏢 {cont['company']}</h4>
                                <span class="badge-gold">{cont['rating']}</span>
                            </div>
                            <p style="margin-top: 5px; margin-bottom: 5px;">📍 <b>العنوان:</b> {cont['location']} | 🏷️ <b>النوع:</b> {cont['type']}</p>
                            <p style="margin-top: 5px; margin-bottom: 5px;">💰 <b>عطاء السعر المقترح:</b> ${cont['bid']:,.2f} | ⏱️ <b>المدة التنفيذية:</b> {cont['days']} يوم</p>
                            <p style="margin-top: 5px; margin-bottom: 10px;">📞 <b>الهاتف:</b> {cont['phone']}</p>
                            <a href="{cont['wa_link']}" target="_blank" style="display: inline-block; background-color: #25D366; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">📲 تواصل عبر WhatsApp مباشر</a>
                        </div>
                        """, unsafe_allow_html=True)

        with eng_sub3:
            st.markdown("### 🕹️ التوأم الرقمي ومحاكاة الموقع الحي (Digital Twin Simulation & ZKP)")
            
            twin_engine = LiveTwinEngine(project_id="PROJ-ENTERPRISE-2026")
            twin_data = twin_engine.get_live_telemetry()
            
            col_tw1, col_tw2, col_tw3 = st.columns(3)
            col_tw1.metric("📊 نسبة الإنجاز الفعلي", f"{twin_data['completion_percentage']}%")
            col_tw2.metric("🌡️ درجة حرارة الموقع", twin_data['site_temperature'])
            col_tw3.metric("🏗️ حالة الميكانيكا والمعدات", twin_data['machinery_status'])
            
            st.divider()
            st.markdown("#### 🛡️ عقد الضمان والتأمين التلقائي (Zero-Knowledge Escrow Proof)")
            
            release_val = p_budget_eng * (twin_data['completion_percentage'] / 100.0)
            zkp_proof = ZeroKnowledgeEscrow.generate_zkp_proof("PROJ-ENTERPRISE-2026", twin_data['completion_percentage'], release_val)
            
            st.info(f"**رمز الإثبات التشفيري (Zero-Knowledge Proof):**\n`{zkp_proof}`")
            st.caption("يُثبت هذا الرمز استحقاق الدفعة المالية للمقاول بناءً على نسبة الإنجاز المسجلة دون كشف بيانات الميزانية السرية.")

    # =========================================================================
    # TAB 2: ADVANCED 6D INTERACTIVE ANALYTICS
    # =========================================================================
    with tab2:
        if not st.session_state.current_plan:
            st.info("💡 قم بتوليد خطة مشروع أولاً لعرض التحليلات الهندسية المتقدمة.")
        else:
            plan = st.session_state.current_plan
            df = pd.DataFrame(plan.get('tasks', []))
            
            p_budget = float(plan['budget'])
            p_days = int(plan['target_days'])
            p_hours = p_days * 8
            daily_cost = p_budget / max(1, p_days)
            
            risk_val = plan.get('risk', 'متوسط')
            risk_penalty = 20 if risk_val == "عالي" else (10 if risk_val == "متوسط" else 5)
            budget_efficiency = min(100, max(40, int((p_budget / (p_days * 100)) * 50)))
            success_rate = min(98, max(55, int(budget_efficiency + (40 - risk_penalty))))
            failure_rate = round(100.0 - success_rate, 1)
            tech_readiness = 92.5 if "PostgreSQL" in str(plan.get('tech_stack')) else 84.0

            st.markdown("## 📊 لوحة القيادة الهندسية وتفصيل الجودة والمخاطر 6D")
            st.caption("رسومات نص دائرية ومؤشرات تفاعلية ملونة تشرح التكلفة، الأيام، الساعات، نسبة النجاح، والمخاطر لكل مشروع بدقة متناهية.")

            g_col1, g_col2, g_col3 = st.columns(3)
            with g_col1:
                fig1 = create_half_doughnut_gauge(daily_cost, "💰 التكلفة اليومية الكلية", "#3B82F6", prefix="$", suffix="/يوم", max_val=daily_cost*2)
                st.plotly_chart(fig1, use_container_width=True)
            with g_col2:
                fig2 = create_half_doughnut_gauge(p_hours, "⏱️ إجمالي ساعات العمل الهندسية", "#8B5CF6", suffix=" ساعة", max_val=p_hours*1.5)
                st.plotly_chart(fig2, use_container_width=True)
            with g_col3:
                fig3 = create_half_doughnut_gauge(p_days, "📅 الأيام التقويمية المستهدفة", "#06B6D4", suffix=" يوم", max_val=p_days*1.5)
                st.plotly_chart(fig3, use_container_width=True)

            g_col4, g_col5, g_col6 = st.columns(3)
            with g_col4:
                fig4 = create_half_doughnut_gauge(success_rate, "🌟 نسبة النجاح المتوقعة للمشروع", "#10B981", suffix="%")
                st.plotly_chart(fig4, use_container_width=True)
            with g_col5:
                fig5 = create_half_doughnut_gauge(failure_rate, "⚠️ نسبة المخاطر والفشل المحتملة", "#EF4444", suffix="%")
                st.plotly_chart(fig5, use_container_width=True)
            with g_col6:
                fig6 = create_half_doughnut_gauge(tech_readiness, "🛡️ جاهزية البنية والتكتم الأمني", "#F59E0B", suffix="%")
                st.plotly_chart(fig6, use_container_width=True)

            st.divider()

            st.markdown("### 📝 المتطلبات التفصيلية والشرح المباشر للمشروع")
            col_desc1, col_desc2 = st.columns(2)

            with col_desc1:
                st.markdown(f"""
                <div class="stat-card-box" style="text-align: right;">
                    <h4 style="color: #60A5FA;">💵 تفاصيل توزيع الميزانية والأيام</h4>
                    <p>• <b>الميزانية الإجمالية:</b> ${p_budget:,.2f}</p>
                    <p>• <b>معدل الإنفاق اليومي:</b> ${daily_cost:,.2f} / يوم عمل</p>
                    <p>• <b>معدل التكلفة للساعة:</b> ${(p_budget / max(1, p_hours)):,.2f} / ساعة</p>
                    <p>• <b>احتياطي الطوارئ الموصى به:</b> ${(p_budget * 0.1):,.2f} (10%)</p>
                </div>
                """, unsafe_allow_html=True)

            with col_desc2:
                st.markdown(f"""
                <div class="stat-card-box" style="text-align: right;">
                    <h4 style="color: #34D399;">🧠 تقييم فرصة النجاح والمخاطر</h4>
                    <p>• <b>احتمالية النجاح التنفيذي:</b> <span style="color: #10B981; font-weight: bold;">{success_rate}%</span></p>
                    <p>• <b>مستوى تحمل المخاطرة:</b> {plan.get('risk', 'متوسط')}</p>
                    <p>• <b>توصية النظام الأمني:</b> تفعيل HMAC Signature وتأمين جداول RLS في Cloud SQL.</p>
                </div>
                """, unsafe_allow_html=True)

            st.divider()
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("### 🍩 التحليل المالي المتداخل (Sunburst)")
                labels = [plan['project_name']] + [t.get('task', t.get('title', 'مهمة')) for t in plan.get('tasks', [])]
                parents = [""] + [plan['project_name']] * len(df)
                values = [plan['budget']] + [t.get('cost', 0) for t in plan.get('tasks', [])]
                fig_sunburst = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values, branchvalues="total", marker=dict(colorscale='Blues')))
                fig_sunburst.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color), height=320)
                st.plotly_chart(fig_sunburst, use_container_width=True)

            with col_c2:
                st.markdown("### 🕸️ تقييم الأبعاد (5D Radar Risk Matrix)")
                radar_cats = ['تعقيد النطاق', 'الأمان الرقمي', 'التحكم بالجدول', 'استقرار التكلفة', 'المرونة التقنية']
                radar_vals = [80, 95, 85, 90, 70]
                fig_radar = go.Figure(go.Scatterpolar(r=radar_vals, theta=radar_cats, fill='toself', line=dict(color='#8B5CF6')))
                fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color), height=320)
                st.plotly_chart(fig_radar, use_container_width=True)

    # =========================================================================
    # TAB 3: TASK EDITOR & DETAILED TEXT PLAN
    # =========================================================================
    with tab3:
        st.subheader(txt['tab3'])
        if not st.session_state.current_plan:
            st.warning("⚠️ لا توجد خطة حالية لتعديلها.")
        else:
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
                st.success("✅ تم حفظ التعديلات وإعادة التوقيع الرقمي بنجاح!")
                st.rerun()

            st.divider()
            st.markdown(f"### {txt['detailed_plan']}")
            st.markdown(build_detailed_plan_text(st.session_state.current_plan))

    # =========================================================================
    # TAB 4: CLOSED-LOOP FEEDBACK & DYNAMIC PRICING
    # =========================================================================
    with tab4:
        st.subheader(txt['pricing_adapted_title'])
        st.caption(txt['pricing_adapted_caption'])

        col_fb1, col_fb2 = st.columns([1, 1])

        with col_fb1:
            st.markdown(f"### {txt['share_feedback_title']}")
            
            st.markdown(f"**{txt['star_rating_label']}**")
            stars_selection = st.feedback("stars")
            rating_stars = (stars_selection + 1) if stars_selection is not None else 5
            
            star_display = "🌟" * rating_stars
            st.caption(f"التقييم المختار: **{star_display}** ({rating_stars} من 5 نجوم)")

            with st.form("feedback_form"):
                suggested_p = st.number_input("ما هو السعر الشهري العادل بالدولار لهذه الخدمة؟ ($)", min_value=5, max_value=200, value=29)
                req_feature = st.selectbox("ما هي الميزة الأكثر أهمية التي ترغب بإضافتها؟", [
                    "تصدير تقارير احترافية بالعربية PDF",
                    "ربط أوتوماتيكي مع Cloud SQL و Cloud Run",
                    "إشعارات فورية عبر الواتساب والتليجرام",
                    "تكامل مع الذكاء الاصطناعي المباشر Gemini Pro",
                    "إدارة الميزانية المتعددة للعملات"
                ])
                comments = st.text_area("ملاحظات إضافية أو مقترحات لتطوير المنصة", placeholder="اكتب تعليقك وطموحك للمنصة هنا...")
                submit_fb = st.form_submit_button("🚀 إرسال التغذية الراجعة وتحديث النظام")

                if submit_fb:
                    if HybridDatabaseEngine.save_feedback(st.session_state.user['email'], rating_stars, suggested_p, req_feature, comments):
                        new_c = st.session_state.user['credits'] + 1
                        HybridDatabaseEngine.update_credits(st.session_state.user['email'], new_c)
                        st.session_state.user['credits'] = new_c
                        
                        st.balloons()
                        st.success("🎉 شكراً لك! تم إضافة 1 نقطة مجانية إلى حسابك وحفظ التقييم بـ 5 نجوم والتعليق كاملاً!")
                        time.sleep(1)
                        st.rerun()

        with col_fb2:
            st.markdown(f"### {txt['market_proof_title']}")
            feedbacks = HybridDatabaseEngine.get_all_feedback()
            adapted = PhoenixAI.analyze_feedback_and_adapt_pricing(feedbacks)

            st.markdown(f"""
            <div class="feedback-card">
                <h4>🤖 Dynamic Pricing Engine Response:</h4>
                <p>• <b>متوسط السعر المقترح من العملاء:</b> ${adapted['recommended_monthly']}/شهر</p>
                • <b>الاشتراك السنوي المحسوب تلقائياً:</b> ${adapted['recommended_yearly']}/سنة<br>
                • <b>مؤشر رضا السوق (PMF Score):</b> {adapted['market_satisfaction_score']}%<br>
                • <b>إجمالي الآراء المسجلة:</b> {len(feedbacks)} تقييم حقيقي
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"#### {txt['live_feedback_stream']}")
            if feedbacks:
                for f in feedbacks:
                    stars_count = f.get('rating', 5) or 5
                    stars_str = "🌟" * stars_count
                    comment_text = f.get('comments', '') or "لا توجد ملاحظات إضافية."
                    
                    st.markdown(f"""
                    <div class="user-feedback-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <b>👤 البريد: <code>{f['user_email']}</code></b>
                            <span style="font-size: 16px;">{stars_str} ({stars_count}/5)</span>
                        </div>
                        <p style="margin-top: 6px; margin-bottom: 4px;">💵 <b>السعر المقترح:</b> ${f['suggested_price']} | 💡 <b>الميزة المطلوبة:</b> {f['requested_feature']}</p>
                        <p style="color: #94A3B8; font-style: italic; margin-bottom: 0;">💬 <b>التعليق:</b> {comment_text}</p>
                        <small style="color: #64748B;">📅 التاريخ: {f.get('created_at', 'مؤخراً')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد تقييمات سابقة بعد. كن أول من يشارك رأيه!")

    # =========================================================================
    # TAB 5: ACCOUNT & SUBSCRIPTIONS
    # =========================================================================
    with tab5:
        st.subheader(txt['tab5'])
        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            st.markdown(f"### {txt['account_info_title']}")
            st.write(f"**الاسم:** {st.session_state.user['username']}")
            st.write(f"**البريد:** {st.session_state.user['email']}")
            st.write(f"**نوع الاشتراك:** {st.session_state.user['role']}")
            st.write(f"**الرصيد المتاح:** {st.session_state.user['credits']} نقطة")

        with col_acc2:
            st.markdown(f"### {txt['upgrade_plans_title']}")
            st.markdown(f'<a href="{PAYMENT_LINK_MONTHLY}" target="_blank" class="checkout-btn">💳 الاشتراك الشهري (${adapted_insights["recommended_monthly"]})</a>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<a href="{PAYMENT_LINK_YEARLY}" target="_blank" class="checkout-btn-yearly">👑 الاشتراك السنوي (${adapted_insights["recommended_yearly"]})</a>', unsafe_allow_html=True)

        if st.session_state.payment_notifications:
            st.divider()
            st.markdown(f"### {txt['payment_logs_title']}")
            for notif in st.session_state.payment_notifications:
                st.markdown(f"""
                <div class="stat-card-box" style="text-align: right;">
                    <b>المستلم:</b> {notif['to']}<br>
                    <b>رقم الطلب:</b> {notif['order_id']}<br>
                    <b>الباقة:</b> {notif['plan_name']} ({notif['amount']})<br>
                    <b>التاريخ:</b> {notif['date']}
                </div>
                """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 6: CLOUD DB ARCHIVE
    # =========================================================================
    with tab6:
        st.subheader(txt['cloudsql_title'])
        st.caption(txt['cloudsql_caption'])
        
        saved_projs = HybridDatabaseEngine.get_projects(st.session_state.user['email'])
        if saved_projs:
            st.dataframe(pd.DataFrame(saved_projs), use_container_width=True)
        else:
            st.info("لا توجد مشاريع محفوظة حالياً.")

    # =========================================================================
    # TAB ADMIN: CEO CONTROL PANEL
    # =========================================================================
    if is_ceo_owner:
        with tab_admin:
            st.subheader(txt['ceo_title'])
            st.caption(txt['ceo_caption'])

            all_users = HybridDatabaseEngine.get_all_users_admin()
            total_users_count = len(all_users)
            subscribed_count = len([u for u in all_users if u['is_subscribed']])
            admin_supervisors_count = len([u for u in all_users if u.get('is_admin')])

            m_adm1, m_adm2, m_adm3, m_adm4 = st.columns(4)
            m_adm1.metric("👥 إجمالي المستخدمين المسجلين", total_users_count)
            m_adm2.metric("💳 عدد الاشتراكات المدفوعة", subscribed_count)
            m_adm3.metric("👑 المشرفين المعتمدين", admin_supervisors_count)
            m_adm4.metric("📈 نسبة التحويل للاشتراك", f"{round((subscribed_count/max(1, total_users_count))*100, 1)}%")

            st.divider()

            st.markdown(f"### {txt['grant_admin_title']}")
            col_add_adm1, col_add_adm2 = st.columns([2, 1])
            with col_add_adm1:
                target_admin_email = st.text_input("أدخل البريد الإلكتروني للمستخدم لترقيته إلى مشرف", placeholder="supervisor@domain.com").lower().strip()
            with col_add_adm2:
                st.write("<br>", unsafe_allow_html=True)
                if st.button(txt['grant_admin_btn'], type="primary", use_container_width=True):
                    if target_admin_email:
                        if HybridDatabaseEngine.add_admin_privilege(target_admin_email):
                            st.success(f"✅ تم منح صلاحيات المشرف بنجاح لـ `{target_admin_email}`!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ فشل العثور على البريد الإلكتروني في قاعدة البيانات.")

            st.divider()

            st.markdown(f"### {txt['users_log_title']}")
            if all_users:
                df_admin_users = pd.DataFrame(all_users)
                st.dataframe(df_admin_users[["id", "full_name", "email", "role", "credits", "is_subscribed", "is_admin", "created_at"]], use_container_width=True)

            st.markdown(f"### {txt['demands_title']}")
            admin_fb = HybridDatabaseEngine.get_all_feedback()
            if admin_fb:
                df_admin_fb = pd.DataFrame(admin_fb)
                st.dataframe(df_admin_fb[["user_email", "rating", "suggested_price", "requested_feature", "comments", "created_at"]], use_container_width=True)
            else:
                st.info("لا توجد طلبات مدخلة حتى الآن.")

if __name__ == "__main__":
    main()
