#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & WAKEEL MEHNA PRO ENTERPRISE ARCHITECTURE v13.6 - ULTIMATE SaaS
================================================================================
MAIN APPLICATION: UI, Tabs, Sidebar, and Core Workflow
================================================================================
"""

import os
import time
import json
import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    T, init_session, update_language, update_theme, apply_template,
    inject_custom_css, SecurityEngine, NotificationEngine,
    generate_excel_download, generate_pdf_plan, build_detailed_plan_text,
    create_half_doughnut_gauge, get_env_or_secret
)
from db import HybridDatabaseEngine
from ai import PhoenixAI, AIPaymentAgent
from auth import render_auth_page


# =====================================================================
# CONFIGURATION
# =====================================================================
APP_TITLE = "PHOENIX & WAKEEL MEHNA PRO - ENTERPRISE v13.6"
PAYMENT_LINK_MONTHLY = os.getenv("PAYMENT_LINK_MONTHLY", "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly")
PAYMENT_LINK_YEARLY = os.getenv("PAYMENT_LINK_YEARLY", "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly")
APP_BASE_URL = get_env_or_secret("APP_URL", "https://mihna-core-50335759464.asia-south1.run.app")
SUPER_ADMIN_EMAIL = "eng.alhiadri2021@gmail.com"


# =====================================================================
# MAIN APPLICATION
# =====================================================================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")
    init_session()

    if not st.session_state.is_authenticated:
        render_auth_page()
        return

    # Sync user data from DB
    fresh_u = HybridDatabaseEngine.get_user(st.session_state.user['email'])
    if fresh_u:
        st.session_state.user['credits'] = fresh_u['credits']
        st.session_state.user['role'] = fresh_u['role']
        st.session_state.user['is_subscribed'] = bool(fresh_u['is_subscribed'])
        st.session_state.user['is_admin'] = bool(fresh_u['is_admin']) or (fresh_u['email'].strip().lower() == SUPER_ADMIN_EMAIL.strip().lower())

    lang = st.session_state.lang
    txt = T[lang]

    # --- Inject Custom CSS ---
    inject_custom_css()

    # --- Sidebar ---
    with st.sidebar:
        st.title("🛡️ PHOENIX AGENT")
        st.markdown("<span class='badge-purple'>Enterprise v13.6</span>", unsafe_allow_html=True)
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

    # --- Main Title ---
    st.title(txt['title'])
    st.caption(txt['subtitle'])

    # --- Credit Warning ---
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

    # --- Tabs ---
    if is_ceo_owner:
        tab1, tab2, tab3, tab4, tab5, tab6, tab_admin = st.tabs([
            txt['tab1'], txt['tab2'], txt['tab3'], txt['tab4'], txt['tab5'], txt['tab6'], txt['tab_admin']
        ])
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            txt['tab1'], txt['tab2'], txt['tab3'], txt['tab4'], txt['tab5'], txt['tab6']
        ])

    # =====================================================================
    # TAB 1: BUILD PROJECT PLAN & SPECIALIST PAYROLL
    # =====================================================================
    with tab1:
        st.markdown("<div class='glass-card glass-card-builder'>", unsafe_allow_html=True)
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
            st.markdown("<div class='glass-card glass-card-builder'>", unsafe_allow_html=True)
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
                st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:12px; font-weight:bold; text-decoration:none;">{txt["send_wa"]}</a>', unsafe_allow_html=True)
            with col_n2:
                if st.button(txt['send_tg'], use_container_width=True):
                    st.success(f"✅ Notification sent to {st.session_state.notify_telegram}")
            st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================================
    # TAB 2: ADVANCED 6D INTERACTIVE ANALYTICS (HALF-DOUGHNUT GAUGES)
    # =====================================================================
    with tab2:
        if not st.session_state.current_plan:
            st.markdown("<div class='glass-card glass-card-analytics'>", unsafe_allow_html=True)
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

            st.markdown("<div class='glass-card glass-card-analytics'>", unsafe_allow_html=True)
            st.markdown("## 📊 6D Engineering Dashboard & Quality Assessment")
            st.caption("Interactive colored gauges analyzing budget, hours, success probabilities, and technical readiness.")

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

            st.markdown("<div class='glass-card glass-card-analytics'>", unsafe_allow_html=True)
            col_desc1, col_desc2 = st.columns(2)
            with col_desc1:
                st.markdown(f"""
                <div class="stat-card-box">
                    <h4 style="color: #2563EB;">💵 Budget & Timeline Breakdown</h4>
                    <p>• <b>Total Budget:</b> ${p_budget:,.2f}</p>
                    <p>• <b>Daily Spend Rate:</b> ${daily_cost:,.2f} / day</p>
                    <p>• <b>Hourly Rate:</b> ${(p_budget / max(1, p_hours)):,.2f} / hr</p>
                    <p>• <b>Risk Contingency Reserve:</b> ${(p_budget * 0.1):,.2f} (10%)</p>
                </div>
                """, unsafe_allow_html=True)

            with col_desc2:
                st.markdown(f"""
                <div class="stat-card-box">
                    <h4 style="color: #059669;">🧠 Success & Security Assessment</h4>
                    <p>• <b>Estimated Execution Success:</b> <span style="color: #059669; font-weight: bold;">{success_rate}%</span></p>
                    <p>• <b>Risk Profile:</b> {plan.get('risk', 'Medium')}</p>
                    <p>• <b>Security Recommendation:</b> Enable HMAC Signature & Cloud SQL RLS.</p>
                </div>
                """, unsafe_allow_html=True)

            st.divider()
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

    # =====================================================================
    # TAB 3: TASK EDITOR & DETAILED PLAN
    # =====================================================================
    with tab3:
        if not st.session_state.current_plan:
            st.markdown("<div class='glass-card glass-card-editor'>", unsafe_allow_html=True)
            st.warning("⚠️ No active plan available to edit.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='glass-card glass-card-editor'>", unsafe_allow_html=True)
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

            st.markdown("<div class='glass-card glass-card-editor'>", unsafe_allow_html=True)
            st.markdown(f"### {txt['detailed_plan']}")
            st.markdown(build_detailed_plan_text(st.session_state.current_plan))
            st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================================
    # TAB 4: FEEDBACK LOOP & DYNAMIC PRICING ENGINE
    # =====================================================================
    with tab4:
        st.markdown("<div class='glass-card glass-card-feedback'>", unsafe_allow_html=True)
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
            <div style="background: rgba(245, 158, 11, 0.08); border-radius: 16px; padding: 18px; margin-bottom: 15px; border: 1px solid rgba(245, 158, 11, 0.2);">
                <h4 style="color: #F59E0B;">🤖 AI Dynamic Pricing Response:</h4>
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
                    <div style="background: rgba(255, 255, 255, 0.05); border-left: 4px solid #F59E0B; padding: 12px; border-radius: 10px; margin-bottom: 10px;">
                        <b>👤 {f['user_email']}</b> - {stars_str} ({stars_count}/5)<br>
                        <small>💵 Price: ${f['suggested_price']} | 💡 Feature: {f['requested_feature']}</small><br>
                        <i>💬 "{comment_text}"</i>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No feedback entries yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================================
    # TAB 5: ACCOUNT & SUBSCRIPTIONS
    # =====================================================================
    with tab5:
        st.markdown("<div class='glass-card glass-card-account'>", unsafe_allow_html=True)
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
                <div style="background: rgba(16,185,129,0.08); border-radius:14px; padding:14px; margin-bottom:10px; border: 1px solid rgba(16,185,129,0.2);">
                    <b>To:</b> {notif['to']}<br>
                    <b>Order ID:</b> {notif['order_id']}<br>
                    <b>Plan:</b> {notif['plan_name']} ({notif['amount']})<br>
                    <b>Date:</b> {notif['date']}
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================================
    # TAB 6: DATABASE ARCHIVE (Cloud SQL PostgreSQL 7-Tables Support)
    # =====================================================================
    with tab6:
        st.markdown("<div class='glass-card glass-card-cloudsql'>", unsafe_allow_html=True)
        st.subheader(txt['cloudsql_title'])
        st.caption(txt['cloudsql_caption'])

        saved_projs = HybridDatabaseEngine.get_projects(st.session_state.user['email'])
        if saved_projs:
            st.dataframe(pd.DataFrame(saved_projs), use_container_width=True)
        else:
            st.info("No saved projects found.")
        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================================
    # TAB ADMIN: CEO CONTROL PANEL (Visible ONLY to Owner & Assigned Admins)
    # =====================================================================
    if is_ceo_owner:
        with tab_admin:
            st.markdown("<div class='glass-card glass-card-ceo'>", unsafe_allow_html=True)
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

            st.markdown("<div class='glass-card glass-card-ceo'>", unsafe_allow_html=True)
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
                            st.error("❌ Email address not found or database update failed.")
                    else:
                        st.warning("⚠️ Please specify an email address.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card glass-card-ceo'>", unsafe_allow_html=True)
            st.markdown(f"### {txt['users_log_title']}")
            if all_users:
                st.dataframe(pd.DataFrame(all_users), use_container_width=True)
            else:
                st.info("No registered users found.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card glass-card-ceo'>", unsafe_allow_html=True)
            st.markdown(f"### {txt['demands_title']}")
            all_feedback_demands = HybridDatabaseEngine.get_all_feedback()
            if all_feedback_demands:
                st.dataframe(pd.DataFrame(all_feedback_demands), use_container_width=True)
            else:
                st.info("No user feedback records available.")
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
