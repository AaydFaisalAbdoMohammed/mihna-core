#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import io
import json
import time
import urllib.parse
import logging
import hashlib
import hmac

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Fallback Dependency Handling
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_PDF_AVAILABLE = True
except ImportError:
    ARABIC_PDF_AVAILABLE = False

SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_ENTERPRISE_ULTIMATE")

class SecurityEngine:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def hash_password(password: str) -> str:
        if BCRYPT_AVAILABLE:
            try:
                salt = bcrypt.gensalt(rounds=10)
                return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            except Exception as e:
                logging.error(f"Bcrypt hash error: {e}")
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        if not hashed or not password:
            return False

        if BCRYPT_AVAILABLE and hashed.startswith("$2"):
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except Exception as e:
                logging.error(f"Bcrypt verification check failed: {e}")

        sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if hmac.compare_digest(sha256_hash, hashed):
            return True

        return hmac.compare_digest(password, hashed)

    @staticmethod
    def generate_signature(data_dict: dict) -> str:
        clean_payload = {k: v for k, v in data_dict.items() if k not in ["signature", "timestamp", "is_tampered"]}
        serialized = json.dumps(clean_payload, sort_keys=True, ensure_ascii=False)
        return hmac.new(SECRET_HMAC_KEY.encode(), serialized.encode(), hashlib.sha512).hexdigest()

    @staticmethod
    def verify_signature(data_dict: dict, signature: str) -> bool:
        if not signature:
            return False
        expected_sig = SecurityEngine.generate_signature(data_dict)
        return hmac.compare_digest(expected_sig, signature)

class NotificationEngine:
    @staticmethod
    def create_whatsapp_link(phone: str, message: str) -> str:
        encoded_msg = urllib.parse.quote(message)
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"

def generate_qr_code_image(target_url: str) -> bytes:
    if QRCODE_AVAILABLE:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(target_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    return b""

def generate_excel_download(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    if OPENPYXL_AVAILABLE:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Project Tasks')
        return output.getvalue()
    else:
        return df.to_csv(index=False).encode('utf-8')

def generate_pdf_plan(plan: dict, signature: str, detailed_text: str) -> bytes:
    buffer = io.BytesIO()
    if not REPORTLAB_AVAILABLE:
        buffer.write(detailed_text.encode('utf-8'))
        return buffer.getvalue()

    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    def prepare_text(text_val):
        if ARABIC_PDF_AVAILABLE:
            try:
                reshaped = arabic_reshaper.reshape(text_val)
                return get_display(reshaped)
            except Exception:
                return text_val
        return text_val

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, alignment=2)

    story.append(Paragraph(prepare_text(f"خطة مشروع: {plan['project_name']}"), title_style))
    story.append(Spacer(1, 15))
    
    info_text = f"المجال التقني: {plan['domain']} | الميزانية: ${plan['budget']} | المدة: {plan['target_days']} يوم"
    story.append(Paragraph(prepare_text(info_text), body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph(prepare_text("--- تفاصيل الخطة التنفيذية والكوادر المخصصة ---"), title_style))
    for line in detailed_text.split("\n"):
        if line.strip():
            story.append(Paragraph(prepare_text(line.strip()), body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 15))
    story.append(Paragraph(prepare_text(f"التوقيع الرقمي HMAC-SHA512: {signature[:40]}..."), body_style))

    doc.build(story)
    return buffer.getvalue()

def create_half_doughnut_gauge(val: float, title: str, color: str, prefix: str = "", suffix: str = "", max_val: float = 100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={'prefix': prefix, 'suffix': suffix, 'font': {'size': 26, 'color': color}},
        title={'text': title, 'font': {'size': 14, 'color': '#64748B'}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "rgba(226, 232, 240, 0.5)",
            'bordercolor': "rgba(0,0,0,0.05)",
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=15, r=15, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#1E293B")
    )
    return fig
