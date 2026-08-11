#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import streamlit as st

from utils import SecurityEngine, generate_qr_code_image
from db import HybridDatabaseEngine, SUPER_ADMIN_EMAIL

APP_BASE_URL = os.getenv("APP_URL", "https://mihna-core-50335759464.asia-south1.run.app")

def render_auth_page(txt, lang):
    st.markdown(f"<h1 style='text-align: center;'>🚀 {txt['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #64748B;'>{txt['subtitle']}</p>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    query_params = st.query_params
    is_signup_mode = query_params.get("mode") == "signup"

    col_center, _ = st.columns([1, 0.01])
    with col_center:
        tab_login_title = f"🔑 {txt['login_btn']}"
        tab_signup_title = f"✨ {txt['signup_btn']}"
        
        if is_signup_mode:
            auth_tabs = st.tabs([tab_signup_title, tab_login_title])
            signup_tab_container = auth_tabs[0]
            login_tab_container = auth_tabs[1]
        else:
            auth_tabs = st.tabs([tab_login_title, tab_signup_title])
            login_tab_container = auth_tabs[0]
            signup_tab_container = auth_tabs[1]

        with login_tab_container:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            col_l1, col_l2 = st.columns([1.5, 1])
            with col_l1:
                with st.form("login_form"):
                    st.subheader(txt['login_welcome'])
                    email_input = st.text_input(txt['email_label'], placeholder="name@domain.com").strip().lower()
                    password_input = st.text_input(txt['pass_label'], type="password", placeholder="••••••••")
                    submit_login = st.form_submit_button(txt['login_btn'], use_container_width=True)
                    
                    if submit_login:
                        if not email_input or not password_input:
                            st.warning("⚠️ " + ("يرجى إدخال البريد وكلمة المرور." if lang=='ar' else "Please enter email and password."))
                        elif not SecurityEngine.is_valid_email(email_input):
                            st.error("❌ " + ("بريد إلكتروني غير صحيح!" if lang=='ar' else "Invalid email format!"))
                        else:
                            u = HybridDatabaseEngine.get_user(email_input)
                            if u and SecurityEngine.verify_password(password_input, u["password_hash"]):
                                is_super = (u['email'].strip().lower() == SUPER_ADMIN_EMAIL.strip().lower()) or bool(u.get('is_admin', 0))
                                st.session_state.is_authenticated = True
                                st.session_state.user = {
                                    'email': u['email'],
                                    'username': u['full_name'] or "مهندس مهنة",
                                    'credits': u['credits'],
                                    'role': u['role'],
                                    'is_subscribed': bool(u['is_subscribed']),
                                    'is_admin': is_super
                                }
                                HybridDatabaseEngine.log_audit(u['id'], "LOGIN_SUCCESS", "User logged in successfully.")
                                st.success(f"🎉 Welcome back {st.session_state.user['username']}!")
                                time.sleep(0.4)
                                st.rerun()
                            else:
                                st.error("❌ " + ("بيانات الدخول غير صحيحة." if lang=='ar' else "Invalid login credentials."))

            with col_l2:
                st.markdown(f"### {txt['qr_scan_title']}")
                st.caption(txt['qr_scan_caption'])
                
                clean_base_url = APP_BASE_URL.rstrip('/')
                signup_url = f"{clean_base_url}/?mode=signup"
                qr_bytes = generate_qr_code_image(signup_url)
                if qr_bytes:
                    st.image(qr_bytes, width=180, caption="Scan QR Code")
            st.markdown("</div>", unsafe_allow_html=True)

        with signup_tab_container:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            with st.form("signup_form"):
                st.subheader(txt['signup_welcome'])
                new_username = st.text_input(txt['fullname_label'], placeholder="Alex Sterling").strip()
                new_email = st.text_input(txt['email_label'], placeholder="name@domain.com").strip().lower()
                new_password = st.text_input(txt['pass_label'], type="password", placeholder="••••••••")
                confirm_password = st.text_input(txt['confirm_pass_label'], type="password", placeholder="••••••••")
                submit_signup = st.form_submit_button(txt['signup_btn'], use_container_width=True)
                
                if submit_signup:
                    if not new_username:
                        st.error("❌ " + ("يرجى كتابة الاسم الكامل!" if lang=='ar' else "Full Name is strictly required!"))
                    elif not new_email or not SecurityEngine.is_valid_email(new_email):
                        st.error("❌ " + ("يرجى كتابة بريد إلكتروني صحيح وصالح!" if lang=='ar' else "Valid Email is strictly required!"))
                    elif not new_password or len(new_password) < 4:
                        st.error("❌ " + ("كلمة المرور يجب أن تكون 4 رموز على الأقل!" if lang=='ar' else "Password must be at least 4 characters!"))
                    elif new_password != confirm_password:
                        st.error("❌ " + ("كلمة المرور وتأكيدها غير متطابقين!" if lang=='ar' else "Passwords do not match!"))
                    else:
                        existing = HybridDatabaseEngine.get_user(new_email)
                        if existing:
                            st.error("❌ " + ("البريد الإلكتروني مسجل مسبقاً." if lang=='ar' else "Email already registered."))
                        else:
                            hashed_p = SecurityEngine.hash_password(new_password)
                            if HybridDatabaseEngine.register_user(new_username, new_email, hashed_p):
                                is_super = (new_email == SUPER_ADMIN_EMAIL.strip().lower())
                                st.session_state.is_authenticated = True
                                st.session_state.user = {
                                    'email': new_email,
                                    'username': new_username,
                                    'credits': 5,
                                    'role': "Enterprise Owner / Super Admin" if is_super else "Free Trial",
                                    'is_subscribed': False,
                                    'is_admin': is_super
                                }
                                st.balloons()
                                st.success("🎉 Account Created Successfully & Persisted!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("❌ Registration failed, try again.")
            st.markdown("</div>", unsafe_allow_html=True)
