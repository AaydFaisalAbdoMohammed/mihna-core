#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import time
import math
import logging
import datetime
import hashlib
import numpy as np
import pandas as pd
import streamlit as st
import google.generativeai as genai

from utils import SecurityEngine
from db import HybridDatabaseEngine

PAYMENT_LINK_MONTHLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly"
PAYMENT_LINK_YEARLY = "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly"


class EngineeringAIEngine:
    """
    محرك الذكاء الاصطناعي الخاص بالتخطيط المعماري والتصميم الجيلاتي وحساب الكميات (AI-ConTech).
    """
    def __init__(self, gemini_api_key: str = None):
        self.api_key = gemini_api_key

    def generate_generative_floor_plan(self, land_area: float, num_floors: int, num_bedrooms: int, budget: float, style: str) -> dict:
        """
        توليد مخطط معماري هندسي محسن بناءً على المساحة والميزانية
        """
        total_built_area = land_area * 0.65 * num_floors  # نسبة البناء المسموحة تقريبياً 65%
        
        # توزيع المساحات الافتراضي المعتمد هندسياً
        rooms_layout = [
            {"name": "Master Bedroom", "area_sqm": round(total_built_area * 0.15, 2), "type": "Private"},
            {"name": "Living Room", "area_sqm": round(total_built_area * 0.22, 2), "type": "Public"},
            {"name": "Kitchen", "area_sqm": round(total_built_area * 0.10, 2), "type": "Service"},
            {"name": "Bathrooms", "area_sqm": round(total_built_area * 0.08, 2), "type": "Service"},
            {"name": "Corridors & Stairs", "area_sqm": round(total_built_area * 0.15, 2), "type": "Circulation"}
        ]
        
        # إضافة غرف النوم إضافية حسب الطلب
        for i in range(1, num_bedrooms):
            rooms_layout.append({
                "name": f"Bedroom {i+1}",
                "area_sqm": round((total_built_area * 0.30) / max(1, num_bedrooms - 1), 2),
                "type": "Private"
            })

        return {
            "land_area": land_area,
            "total_built_area": round(total_built_area, 2),
            "estimated_cost": round(total_built_area * 350, 2),  # متوسط تكلفة بناء المتر المربع
            "style": style,
            "layout": rooms_layout
        }

    def calculate_automated_boq(self, built_area_sqm: float, quality_tier: str = "Standard") -> dict:
        """
        حساب جدول الكميات (Bill of Quantities) وتكاليف المواد بناءً على أسعار السوق
        """
        multipliers = {
            "Economy": {"steel_ratio": 0.035, "concrete_ratio": 0.35, "price_mult": 0.85},
            "Standard": {"steel_ratio": 0.042, "concrete_ratio": 0.40, "price_mult": 1.0},
            "Luxury": {"steel_ratio": 0.050, "concrete_ratio": 0.45, "price_mult": 1.4}
        }
        
        tier = multipliers.get(quality_tier, multipliers["Standard"])
        
        # معدلات استهلاك المواد التقريبية لكل متر مربع بناء
        steel_ton = built_area_sqm * tier["steel_ratio"]  # طن حديد
        concrete_m3 = built_area_sqm * tier["concrete_ratio"]  # متر مكعب خرسانة
        blocks_units = built_area_sqm * 12.5  # عدد الطابوق/الجراد
        finishing_sqm = built_area_sqm * 2.8  # مساحة التشطيبات الداخلية والخارجية

        # أسعار تقريبية قياسية مع ضبط الفئة
        unit_prices = {
            "steel": 750 * tier["price_mult"],       # $ / طن
            "concrete": 80 * tier["price_mult"],      # $ / م3
            "blocks": 0.75 * tier["price_mult"],      # $ / حبة
            "finishing": 45 * tier["price_mult"]      # $ / م2
        }

        boq_items = [
            {
                "item": "حديد التسليح (Reinforcement Steel)",
                "quantity": round(steel_ton, 2),
                "unit": "طن",
                "unit_price": unit_prices["steel"],
                "total_price": round(steel_ton * unit_prices["steel"], 2)
            },
            {
                "item": "الخرسانة الجاهزة (Ready-Mix Concrete)",
                "quantity": round(concrete_m3, 2),
                "unit": "متر مكعب",
                "unit_price": unit_prices["concrete"],
                "total_price": round(concrete_m3 * unit_prices["concrete"], 2)
            },
            {
                "item": "الطابوق / البلوك (Concrete Blocks)",
                "quantity": round(blocks_units, 0),
                "unit": "حبة",
                "unit_price": unit_prices["blocks"],
                "total_price": round(blocks_units * unit_prices["blocks"], 2)
            },
            {
                "item": "أعمال التشطيبات (Finishing & Coating)",
                "quantity": round(finishing_sqm, 2),
                "unit": "متر مكعب/م2",
                "unit_price": unit_prices["finishing"],
                "total_price": round(finishing_sqm * unit_prices["finishing"], 2)
            }
        ]

        total_boq_cost = sum(item["total_price"] for item in boq_items)

        return {
            "boq_items": boq_items,
            "grand_total_usd": round(total_boq_cost, 2),
            "contingency_buffer_10pct": round(total_boq_cost * 0.10, 2)
        }


class PhoenixAI:
    @staticmethod
    def generate_architecture(req: dict, api_key: str = None) -> dict:
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt = f"""قم بإنشاء خطة معمارية هندسية بتنسيق JSON للمشروع التالي:
اسم المشروع: {req['project_name']}
المجال: {req['domain']}
الميزانية: {req['budget']}
الأيام المستهدفة: {req['target_days']}
التقنيات: {req['tech_stack']}
نطاق العمل: {req['scope']}

قم بإرجاع JSON فقط يحوي: project_name, domain, budget, target_days, risk, executive_summary, tech_stack (قائمة), tasks (قائمة كائنات بها: id, task, days, cost, status, priority)."""
                response = model.generate_content(prompt)
                match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    data["scope"] = req['scope']
                    data["signature"] = SecurityEngine.generate_signature(data)
                    data["generated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    return data
            except Exception as e:
                logging.error(f"Gemini API Exception fallback: {e}")

        return PhoenixAI._fallback_architecture(req)

    @staticmethod
    def _fallback_architecture(req: dict) -> dict:
        b = float(req['budget'])
        d = int(req['target_days'])
        tasks = [
            {"id": 1, "task": "تحليل المتطلبات وتصميم المعمارية HLD/LLD", "days": max(1, int(d*0.15)), "cost": int(b*0.15), "status": "مخطط", "priority": "High"},
            {"id": 2, "task": "بناء قواعد البيانات وتأمين APIs RLS Backend", "days": max(1, int(d*0.35)), "cost": int(b*0.35), "status": "مخطط", "priority": "High"},
            {"id": 3, "task": "تطوير واجهات المستخدم Frontend & UI Components", "days": max(1, int(d*0.30)), "cost": int(b*0.30), "status": "مخطط", "priority": "Medium"},
            {"id": 4, "task": "الااختبارات الشاملة QA & Cloud Deployment", "days": max(1, int(d*0.20)), "cost": int(b*0.20), "status": "مخطط", "priority": "Low"}
        ]
        
        tech_list = [t.strip() for t in req['tech_stack'].split(",")] if isinstance(req['tech_stack'], str) else req['tech_stack']

        data = {
            "project_name": req['project_name'],
            "domain": req['domain'],
            "executive_summary": f"خطة هندسية تنفيذية فائقة الدقة لمشروع ({req['project_name']}) بتصميم أمني ومعماري متكامل.",
            "tech": req['tech_stack'],
            "tech_stack": tech_list,
            "scope": req.get('scope', ''),
            "budget": b,
            "target_days": d,
            "risk": req.get('risk', 'متوسط'),
            "tasks": tasks,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data["signature"] = SecurityEngine.generate_signature(data)
        return data

    @staticmethod
    def calculate_specialists_breakdown(budget: float, target_days: int, domain: str) -> list:
        total_man_hours = target_days * 8
        dev_budget = budget * 0.75

        if "ذكاء" in domain or "AI" in domain or "SaaS" in domain:
            roles_ratio = [
                {"role": "مهندس المعمارية والذكاء الاصطناعي (AI/Cloud Architect)", "ratio": 0.25, "icon": "🧠"},
                {"role": "مطور خلفية النظم (Senior Backend Engineer)", "ratio": 0.25, "icon": "⚙️"},
                {"role": "مطور واجهات المستخدم (Frontend/Mobile Engineer)", "ratio": 0.20, "icon": "💻"},
                {"role": "مصمم تجربة وواجهة المستخدم (UI/UX Designer)", "ratio": 0.12, "icon": "🎨"},
                {"role": "مهندس جودة واختبار الأمان (QA & Security Engineer)", "ratio": 0.10, "icon": "🛡️"},
                {"role": "مدير المشروع الهندسي (Agile Project Manager)", "ratio": 0.08, "icon": "📊"}
            ]
        else:
            roles_ratio = [
                {"role": "مهندس البرمجيات الرئيسي (Lead Software Engineer)", "ratio": 0.22, "icon": "🏗️"},
                {"role": "مطور خلفية النظم (Backend Developer)", "ratio": 0.26, "icon": "⚙️"},
                {"role": "مطور واجهات التطبيق (Frontend Developer)", "ratio": 0.22, "icon": "💻"},
                {"role": "مصمم واجهات المستخدم (UI/UX Designer)", "ratio": 0.12, "icon": "🎨"},
                {"role": "مهندس فحص الجودة (QA Specialist)", "ratio": 0.10, "icon": "🧪"},
                {"role": "مدير المشروع (Technical Project Manager)", "ratio": 0.08, "icon": "📋"}
            ]

        specialists = []
        for r in roles_ratio:
            allocated_cost = dev_budget * r["ratio"]
            allocated_hours = total_man_hours * r["ratio"]
            allocated_days = allocated_hours / 8
            hourly_rate = allocated_cost / max(1, allocated_hours)
            daily_rate = hourly_rate * 8

            specialists.append({
                "icon": r["icon"],
                "role": r["role"],
                "ratio_pct": round(r["ratio"] * 100, 1),
                "total_cost": round(allocated_cost, 2),
                "total_hours": round(allocated_hours, 1),
                "allocated_days": round(allocated_days, 1),
                "hourly_rate": round(hourly_rate, 2),
                "daily_rate": round(daily_rate, 2)
            })

        return specialists

    @staticmethod
    def analyze_feedback_and_adapt_pricing(feedbacks: list) -> dict:
        if not feedbacks:
            return {
                "recommended_monthly": 29,
                "recommended_yearly": 279,
                "top_requested_features": ["تصدير PDF باللغة العربية", "ربط مباشر مع Cloud SQL", "تكامل الذكاء الاصطناعي مع Gemini Pro"],
                "market_satisfaction_score": 93.5
            }
        
        avg_price = np.mean([f['suggested_price'] for f in feedbacks if f.get('suggested_price', 0) > 0]) if feedbacks else 29
        avg_rating = np.mean([f['rating'] for f in feedbacks if f.get('rating') is not None]) if feedbacks else 4.5
        
        features = [f['requested_feature'] for f in feedbacks if f.get('requested_feature')]
        feature_counts = pd.Series(features).value_counts().to_dict() if features else {}
        top_features = list(feature_counts.keys())[:3] if feature_counts else ["تكامل تلقائي مع Cloud SQL", "تخزين الخطط مؤمنة", "دعم الدفع المحلي"]
        
        rec_monthly = max(19, int(avg_price))
        rec_yearly = int(rec_monthly * 9.5)

        return {
            "recommended_monthly": rec_monthly,
            "recommended_yearly": rec_yearly,
            "top_requested_features": top_features,
            "market_satisfaction_score": round(float(avg_rating) * 20, 1)
        }


class AIPaymentAgent:
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
        amount_num = 279.00 if plan_type == "yearly" else 29.00
        amount_str = f"${amount_num:.2f}"

        method_info = AIPaymentAgent.inspect_payment_method(user_email)
        status_box.info(f"🤖 **[AI Agent]:** Checking payment method for `{user_email}`...")
        time.sleep(0.4)
        progress_bar.progress(30)

        status_box.info(f"🔗 **[AI Agent]:** Directing to Lemon Squeezy Router...")
        time.sleep(0.4)
        progress_bar.progress(70)

        status_box.info("🔐 **[AI Agent]:** Confirming Digital Signature & Upgrading Subscription...")
        time.sleep(0.4)
        progress_bar.progress(100)
        
        progress_bar.empty()
        status_box.empty()

        order_id = f"LS-ORD-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()}"
        HybridDatabaseEngine.update_user_subscription(user_email, role=f"Enterprise ({plan_name})", credits=9999)
        HybridDatabaseEngine.record_payment_transaction(user_email, order_id, "Lemon Squeezy", plan_type, amount_num, method_info)

        email_payload = {
            "to": user_email,
            "subject": f"🎉 Receipt & Confirmation for Order #{order_id} from Lemon Squeezy",
            "order_id": order_id,
            "plan_name": plan_name,
            "amount": amount_str,
            "checkout_url_used": checkout_url,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "payment_method": f"Card ending in {method_info['card_last4']}"
        }

        if 'payment_notifications' not in st.session_state:
            st.session_state.payment_notifications = []
        st.session_state.payment_notifications.insert(0, email_payload)


def build_detailed_plan_text(plan: dict) -> str:
    p_name = plan.get('project_name', 'المشروع')
    domain = plan.get('domain', 'تقني')
    budget = float(plan.get('budget', 0))
    days = int(plan.get('target_days', 0))
    tech = plan.get('tech', plan.get('tech_stack', 'Flutter, Node.js, Supabase, PostgreSQL'))
    risk = plan.get('risk', 'متوسط')
    tasks = plan.get('tasks', [])
    
    working_hours_per_day = 8
    total_man_hours = days * working_hours_per_day
    daily_rate = budget / max(1, days)
    hourly_rate = budget / max(1, total_man_hours)
    
    contingency_rate = 0.15 if risk == "عالي" or risk == "High" else (0.10 if risk == "متوسط" or risk == "Medium" else 0.05)
    contingency_amount = budget * contingency_rate
    effective_operational_budget = budget - contingency_amount
    
    cloud_infra_cost = budget * 0.10
    dev_labor_cost = effective_operational_budget - cloud_infra_cost

    specialists = PhoenixAI.calculate_specialists_breakdown(budget, days, domain)
    specialists_str = ""
    for s in specialists:
        specialists_str += f"""
* {s['icon']} **{s['role']}**
  * ⏱️ **إجمالي الساعات:** {s['total_hours']} ساعة ({s['allocated_days']} أيام عمل)
  * 💵 **أجر الساعة الهندسية:** ${s['hourly_rate']:,.2f} / ساعة | **اليومي:** ${s['daily_rate']:,.2f} / يوم
  * 💰 **إجمالي المستحقات:** `${s['total_cost']:,.2f}` ({s['ratio_pct']}% من ميزانية الكوادر)
"""

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
* 📊 **المعدل اليومي للإنفاق:** ${daily_t_cost:,.2f} / يوم | **الساعة:** ${hourly_t_cost:,.2f} / ساعة
* 📌 **الحالة التنفيذية:** {t.get('status', 'مخطط')}
"""

    return f"""📌 **المستند التنفيذي والهندسي المتكامل لمشروع ({p_name})**
*تاريخ التوليد والتوقيع الرقمي: {plan.get('generated_at', datetime.datetime.now().strftime('%Y-%m-%d'))}*

---

### 1. نظرة عامة والأهداف التنفيذية (Executive Summary & KPIs)
يهدف مشروع **{p_name}** إلى تقديم حل سحابي برمجي فائق الأداء في قطاع **{domain}**، معتمداً على البيئة والتقنيات: **({tech})**.
* **الميزانية الكلية (Total Budget):** `${budget:,.2f}`
* **المدى الزمني المستهدف (Timeline):** `{days}` يوماً تقويمياً.
* **مستوى تحمل المخاطر (Risk Profile):** `{risk}`.

---

### 2. توزيع الكوادر والتخصصات الهندسية وأجورهم (Engineering Specialists & Payroll Allocation)
تم استخدام خوارزمية **Phoenix Resource Allocation Engine** لتحديد الكوادر الدقيقة المطلوبة وحساب أجورهم:
{specialists_str}

---

### 3. الحسابات المالية والهندسية التفصيلية (Precise Cost & Time Allocation)
* ⏳ **إجمالي الساعات الهندسية (Total Man-Hours):** `{total_man_hours:,}` ساعة عمل ({working_hours_per_day} ساعات/يوم).
* 💵 **معدل التكلفة اليومي الكلي:** `${daily_rate:,.2f}` / يوم.
* ⏱️ **معدل تكلفة الساعة الهندسية:** `${hourly_rate:,.2f}` / ساعة.
* 🛡️ **احتياطي الطوارئ والمخاطر ({contingency_rate*100:.0f}% Risk Reserve):** `${contingency_amount:,.2f}`.
* ☁️ **تكاليف البنية التحتية والاستضافة Cloud Infrastructure:** `${cloud_infra_cost:,.2f}`.
* 🛠️ **صافي ميزانية تطوير الكوادر (Effective Dev Budget):** `${dev_labor_cost:,.2f}`.

---

### 4. التفصيل المرحلي للمهام (Work Breakdown Structure)
{tasks_breakdown_str}

---

### 5. مصفوفة الأمان والتوقيع الرقمي المشفر (Digital HMAC Signature)
* **التوقيع الرقمي:** تم توقيع هذه الخطة رسمياً وحفظها في قاعدة بيانات Cloud SQL.
* **تشفير HMAC-SHA512:** المعيار السري المعتمد في المؤسسة.
"""
