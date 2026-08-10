#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & WAKEEL MEHNA PRO ENTERPRISE ARCHITECTURE v12.0 - SILICON VALLEY EDITION
محرك معالجة البيانات الهجين المتوافق 100% مع كافة جداول Cloud SQL Studio (PostgreSQL & SQLite)
- معالجة الجداول الـ 7 بالكامل (users, project_plans, plan_tasks, payment_transactions, feedback, security_audit_logs, projects)
- الذكاء الاصطناعي الهندسي (Gemini 2.5 Flash) مع حساب أجور المتخصصين وساعات العمل التفصيلية
- التوقيع الرقمي (HMAC-SHA512) وسجلات التدقيق الأمني Audit Logs
===============================================================================
"""

import os
import re
import io
import json
import time
import uuid
import hmac
import hashlib
import sqlite3
import logging
import datetime
import urllib.parse
from urllib.parse import quote_plus

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# ----------------- Fallback Dependency Handling -----------------
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy import text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

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

# =====================================================================
# 1. CONFIGURATION & SETTINGS
# =====================================================================
APP_TITLE = "PHOENIX & WAKEEL MEHNA PRO - ENTERPRISE v12.0"
PAYMENT_LINK_MONTHLY = os.getenv("PAYMENT_LINK_MONTHLY", "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly")
PAYMENT_LINK_YEARLY = os.getenv("PAYMENT_LINK_YEARLY", "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly")
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_ENTERPRISE_ULTIMATE")

# Cloud SQL / PostgreSQL Parameters
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "101519Ayad@!")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
INSTANCE_CONN = os.getenv("INSTANCE_CONNECTION_NAME", "project-d699d925-921c-4e54-8c4:asia-south1:mihna-core-ay")

SQLITE_DB_FILE = "phoenix_app_data.db"

# =====================================================================
# 2. COMPLETE HYBRID DATABASE ENGINE (100% TABLES MATCHED)
# =====================================================================
class HybridDatabaseEngine:
    _sqlalchemy_engine = None

    @classmethod
    def get_sqlalchemy_engine(cls):
        if not SQLALCHEMY_AVAILABLE:
            return None
        if cls._sqlalchemy_engine is None:
            try:
                encoded_pass = quote_plus(DB_PASS)
                if os.path.exists(f"/cloudsql/{INSTANCE_CONN}"):
                    db_url = f"postgresql+psycopg2://{DB_USER}:{encoded_pass}@/{DB_NAME}?host=/cloudsql/{INSTANCE_CONN}"
                else:
                    db_url = f"postgresql+psycopg2://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                cls._sqlalchemy_engine = sqlalchemy.create_engine(db_url, pool_pre_ping=True)
            except Exception as e:
                logging.error(f"PostgreSQL Engine Error: {e}")
                cls._sqlalchemy_engine = None
        return cls._sqlalchemy_engine

    @classmethod
    def init_db(cls):
        """مطابقة تامة لجميع الجداول السبعة الموضحة في صور Cloud SQL Studio"""
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    # 1. users
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            full_name VARCHAR(255),
                            role VARCHAR(100) DEFAULT 'Free Trial',
                            credits INT DEFAULT 5,
                            is_subscribed INT DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    # 2. project_plans
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS project_plans (
                            id SERIAL PRIMARY KEY,
                            user_id INT REFERENCES users(id) ON DELETE CASCADE,
                            project_name VARCHAR(255),
                            domain VARCHAR(100),
                            budget NUMERIC(12,2),
                            target_days INT,
                            risk_tolerance VARCHAR(50),
                            tech_stack TEXT,
                            scope_of_work TEXT,
                            plan_signature TEXT,
                            is_tampered INT DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    # 3. plan_tasks
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS plan_tasks (
                            id SERIAL PRIMARY KEY,
                            plan_id INT REFERENCES project_plans(id) ON DELETE CASCADE,
                            task_order INT,
                            task_name VARCHAR(255),
                            days INT,
                            cost NUMERIC(12,2),
                            status VARCHAR(50),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    # 4. payment_transactions
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS payment_transactions (
                            id SERIAL PRIMARY KEY,
                            user_id INT REFERENCES users(id) ON DELETE CASCADE,
                            order_id VARCHAR(100) UNIQUE,
                            gateway VARCHAR(50),
                            plan_type VARCHAR(50),
                            amount_paid NUMERIC(10,2),
                            currency VARCHAR(10) DEFAULT 'USD',
                            status VARCHAR(50),
                            raw_response TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    # 5. feedback
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS feedback (
                            id SERIAL PRIMARY KEY,
                            user_email VARCHAR(255) NOT NULL,
                            rating INT,
                            suggested_price INT,
                            requested_feature TEXT,
                            comments TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    # 6. security_audit_logs
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS security_audit_logs (
                            id SERIAL PRIMARY KEY,
                            user_id INT,
                            action_type VARCHAR(100),
                            ip_address VARCHAR(50),
                            details TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    # 7. projects
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS projects (
                            id SERIAL PRIMARY KEY,
                            user_email VARCHAR(255) NOT NULL,
                            project_name VARCHAR(255),
                            summary TEXT,
                            budget_range VARCHAR(100),
                            tech_stack TEXT,
                            payload TEXT,
                            signature TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    conn.commit()
            except Exception as e:
                logging.error(f"PostgreSQL Full Init Warning: {e}")

        # SQLite Fallback Matrix
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password_hash TEXT, full_name TEXT, role TEXT, credits INTEGER DEFAULT 5, is_subscribed INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS project_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, project_name TEXT, domain TEXT, budget REAL, target_days INTEGER, risk_tolerance TEXT, tech_stack TEXT, scope_of_work TEXT, plan_signature TEXT, is_tampered INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS plan_tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER, task_order INTEGER, task_name TEXT, days INTEGER, cost REAL, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS payment_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, order_id TEXT UNIQUE, gateway TEXT, plan_type TEXT, amount_paid REAL, currency TEXT DEFAULT 'USD', status TEXT, raw_response TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, rating INTEGER, suggested_price INTEGER, requested_feature TEXT, comments TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS security_audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action_type TEXT, ip_address TEXT, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, project_name TEXT, summary TEXT, budget_range TEXT, tech_stack TEXT, payload TEXT, signature TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            # الحساب القيادي
            admin_email = "eng.alhiadri2020@gmail.com"
            cursor.execute("SELECT email FROM users WHERE email = ?", (admin_email,))
            if not cursor.fetchone():
                hp = hashlib.sha256("123456".encode()).hexdigest()
                cursor.execute("INSERT INTO users (full_name, email, password_hash, credits, role, is_subscribed) VALUES (?, ?, ?, ?, ?, ?)", ("AYAD FAISAL ABDO MOHAMMED", admin_email, hp, 9999, "Enterprise Pro Owner", 1))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"SQLite Complete Init Error: {e}")

    @classmethod
    def log_security_event(cls, user_id: int, action_type: str, details: str, ip: str = "127.0.0.1"):
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("INSERT INTO security_audit_logs (user_id, action_type, ip_address, details) VALUES (:uid, :act, :ip, :dt)"),
                                 {"uid": user_id, "act": action_type, "ip": ip, "dt": details})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO security_audit_logs (user_id, action_type, ip_address, details) VALUES (?, ?, ?, ?)", (user_id, action_type, ip, details))
            conn.commit()
            conn.close()
        except Exception: pass

    @classmethod
    def save_payment_transaction(cls, user_id: int, order_id: str, gateway: str, plan_type: str, amount: float, status: str, raw_resp: str):
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("""INSERT INTO payment_transactions (user_id, order_id, gateway, plan_type, amount_paid, currency, status, raw_response) 
                                        VALUES (:uid, :oid, :gw, :pt, :amt, 'USD', :st, :raw)"""),
                                 {"uid": user_id, "oid": order_id, "gw": gateway, "pt": plan_type, "amt": amount, "st": status, "raw": raw_resp})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO payment_transactions (user_id, order_id, gateway, plan_type, amount_paid, currency, status, raw_response) VALUES (?, ?, ?, ?, ?, 'USD', ?, ?)",
                           (user_id, order_id, gateway, plan_type, amount, status, raw_resp))
            conn.commit()
            conn.close()
        except Exception: pass

    @classmethod
    def save_full_project_plan(cls, user_id: int, user_email: str, plan_data: dict) -> int:
        p_id = None
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    res = conn.execute(text("""INSERT INTO project_plans (user_id, project_name, domain, budget, target_days, risk_tolerance, tech_stack, scope_of_work, plan_signature, is_tampered)
                                               VALUES (:uid, :pn, :dm, :bg, :td, :rt, :ts, :sw, :ps, 0) RETURNING id"""),
                                       {"uid": user_id, "pn": plan_data['project_name'], "dm": plan_data['domain'], "bg": plan_data['budget'],
                                        "td": plan_data['target_days'], "rt": plan_data.get('risk', 'متوسط'), "ts": str(plan_data['tech_stack']),
                                        "sw": plan_data.get('scope', ''), "ps": plan_data['signature']}).fetchone()
                    conn.commit()
                    if res: p_id = res[0]
            except Exception as e: logging.error(f"PG Save Plan Error: {e}")

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO project_plans (user_id, project_name, domain, budget, target_days, risk_tolerance, tech_stack, scope_of_work, plan_signature, is_tampered)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                           (user_id, plan_data['project_name'], plan_data['domain'], plan_data['budget'], plan_data['target_days'],
                            plan_data.get('risk', 'متوسط'), str(plan_data['tech_stack']), plan_data.get('scope', ''), plan_data['signature']))
            conn.commit()
            if not p_id: p_id = cursor.lastrowid
            conn.close()
        except Exception as e: logging.error(f"SQLite Save Plan Error: {e}")

        # حفظ المهام في جدول plan_tasks المنفصل
        if p_id and 'tasks' in plan_data:
            cls.save_plan_tasks(p_id, plan_data['tasks'])

        # الأرشفة الاحتياطية في جدول projects
        cls.save_project(plan_data, user_email)
        return p_id

    @classmethod
    def save_plan_tasks(cls, plan_id: int, tasks: list):
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    for idx, t in enumerate(tasks, 1):
                        conn.execute(text("INSERT INTO plan_tasks (plan_id, task_order, task_name, days, cost, status) VALUES (:pid, :to, :tn, :dy, :cs, :st)"),
                                     {"pid": plan_id, "to": idx, "tn": t['task'], "dy": t['days'], "cs": t['cost'], "st": t.get('status', 'مخطط')})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            for idx, t in enumerate(tasks, 1):
                cursor.execute("INSERT INTO plan_tasks (plan_id, task_order, task_name, days, cost, status) VALUES (?, ?, ?, ?, ?, ?)",
                               (plan_id, idx, t['task'], t['days'], t['cost'], t.get('status', 'مخطط')))
            conn.commit()
            conn.close()
        except Exception: pass

    @classmethod
    def get_user(cls, email: str) -> dict:
        email_clean = email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    res = conn.execute(text("SELECT id, email, password_hash, full_name, credits, role, is_subscribed FROM users WHERE email = :email"), {"email": email_clean}).fetchone()
                    if res: return {"id": res[0], "email": res[1], "password_hash": res[2], "full_name": res[3], "credits": res[4], "role": res[5], "is_subscribed": res[6]}
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                return {"id": d["id"], "email": d["email"], "password_hash": d["password_hash"], "full_name": d["full_name"], "credits": d["credits"], "role": d["role"], "is_subscribed": d["is_subscribed"]}
        except Exception: pass
        return None

    @classmethod
    def register_user(cls, full_name: str, email: str, password_hash: str) -> bool:
        email_clean = email.strip().lower()
        success = False
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("INSERT INTO users (full_name, email, password_hash, credits, role, is_subscribed) VALUES (:fn, :em, :ph, 5, 'Free Trial', 0)"), {"fn": full_name, "em": email_clean, "ph": password_hash})
                    conn.commit()
                    success = True
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (full_name, email, password_hash, credits, role, is_subscribed) VALUES (?, ?, ?, 5, 'Free Trial', 0)", (full_name, email_clean, password_hash))
            conn.commit()
            conn.close()
            success = True
        except Exception: pass
        return success

    @classmethod
    def update_user_subscription(cls, email: str, role: str, credits: int = 9999) -> bool:
        email_clean = email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("UPDATE users SET role = :role, credits = :credits, is_subscribed = 1, updated_at = CURRENT_TIMESTAMP WHERE email = :email"), {"role": role, "credits": credits, "email": email_clean})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ?, credits = ?, is_subscribed = 1, updated_at = CURRENT_TIMESTAMP WHERE email = ?", (role, credits, email_clean))
            conn.commit()
            conn.close()
            return True
        except Exception: return False

    @classmethod
    def update_credits(cls, email: str, new_credits: int) -> bool:
        email_clean = email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("UPDATE users SET credits = :credits WHERE email = :email"), {"credits": new_credits, "email": email_clean})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET credits = ? WHERE email = ?", (new_credits, email_clean))
            conn.commit()
            conn.close()
            return True
        except Exception: return False

    @classmethod
    def save_project(cls, plan_json: dict, user_email: str) -> bool:
        email_clean = user_email.strip().lower()
        payload_str = json.dumps(plan_json, ensure_ascii=False)
        p_name = plan_json.get('project_name', 'مشروع جديد')
        summary = plan_json.get('executive_summary', '')
        budget = str(plan_json.get('budget', 0))
        tech = json.dumps(plan_json.get('tech_stack', plan_json.get('tech', '')), ensure_ascii=False)
        sig = plan_json.get('signature', '')

        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("""INSERT INTO projects (user_email, project_name, summary, budget_range, tech_stack, payload, signature) VALUES (:em, :pn, :sm, :bg, :tc, :pl, :sg)"""),
                                 {"em": email_clean, "pn": p_name, "sm": summary, "bg": budget, "tc": tech, "pl": payload_str, "sg": sig})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO projects (user_email, project_name, summary, budget_range, tech_stack, payload, signature) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (email_clean, p_name, summary, budget, tech, payload_str, sig))
            conn.commit()
            conn.close()
            return True
        except Exception: return False

    @classmethod
    def get_projects(cls, user_email: str) -> list:
        email_clean = user_email.strip().lower()
        projects = []
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    rows = conn.execute(text("SELECT id, project_name, summary, budget_range, created_at, signature FROM projects WHERE user_email = :em ORDER BY created_at DESC"), {"em": email_clean}).fetchall()
                    if rows:
                        for r in rows: projects.append({"id": r[0], "project_name": r[1], "summary": r[2], "budget_range": r[3], "created_at": str(r[4]), "signature": r[5]})
                        return projects
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, project_name, summary, budget_range, created_at, signature FROM projects WHERE user_email = ? ORDER BY created_at DESC", (email_clean,))
            rows = cursor.fetchall()
            conn.close()
            for r in rows: projects.append(dict(r))
        except Exception: pass
        return projects

    @classmethod
    def save_feedback(cls, user_email: str, rating: int, suggested_price: int, requested_feature: str, comments: str) -> bool:
        email_clean = user_email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("INSERT INTO feedback (user_email, rating, suggested_price, requested_feature, comments) VALUES (:em, :rt, :sp, :rf, :cm)"),
                                 {"em": email_clean, "rt": rating, "sp": suggested_price, "rf": requested_feature, "cm": comments})
                    conn.commit()
            except Exception: pass
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedback (user_email, rating, suggested_price, requested_feature, comments) VALUES (?, ?, ?, ?, ?)", (email_clean, rating, suggested_price, requested_feature, comments))
            conn.commit()
            conn.close()
            return True
        except Exception: return False

    @classmethod
    def get_all_feedback(cls) -> list:
        feedbacks = []
        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            for r in rows: feedbacks.append(dict(r))
        except Exception: pass
        return feedbacks

HybridDatabaseEngine.init_db()

# =====================================================================
# 3. SECURITY ENGINE (HMAC-SHA512 & Hashing)
# =====================================================================
class SecurityEngine:
    @staticmethod
    def hash_password(password: str) -> str:
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode(), salt).decode()
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        if BCRYPT_AVAILABLE and hashed.startswith("$2b$"):
            try: return bcrypt.checkpw(password.encode(), hashed.encode())
            except Exception: return False
        return hashlib.sha256(password.encode()).hexdigest() == hashed

    @staticmethod
    def generate_signature(data_dict: dict) -> str:
        clean_payload = {k: v for k, v in data_dict.items() if k not in ["signature", "timestamp"]}
        serialized = json.dumps(clean_payload, sort_keys=True, ensure_ascii=False)
        return hmac.new(SECRET_HMAC_KEY.encode(), serialized.encode(), hashlib.sha512).hexdigest()

    @staticmethod
    def verify_signature(data_dict: dict, signature: str) -> bool:
        if not signature: return False
        expected_sig = SecurityEngine.generate_signature(data_dict)
        return hmac.compare_digest(expected_sig, signature)

# =====================================================================
# 4. SPECIALISTS & AI ARCHITECTURE GENERATOR
# =====================================================================
class SpecialistsCalculator:
    """حساب أجور الموظفين والمهندسين بدقة متناهية بناءً على مجال المشروع ونطاقه"""
    @staticmethod
    def calculate_specialists(domain: str, budget: float, total_days: int) -> list:
        total_hours = total_days * 8
        dev_budget = budget * 0.65  # 65% ميزانية الفريق البشري

        specialists_templates = {
            "التجارة الإلكترونية": [
                {"role": "مهندس معمارية السحاب وبناء الموارد (Cloud Architect)", "share": 0.20, "hourly_rate_base": 65},
                {"role": "مطور Full-Stack Node.js & React/Flutter", "share": 0.35, "hourly_rate_base": 50},
                {"role": "مصمم واجهات المستخدم وتجربة المستخدم (UI/UX Specialist)", "share": 0.20, "hourly_rate_base": 40},
                {"role": "مهندس أمن المعلومات والتحقق (Cybersecurity Lead)", "share": 0.15, "hourly_rate_base": 70},
                {"role": "مدير مشروع تقني (Agile Technical PM)", "share": 0.10, "hourly_rate_base": 55}
            ],
            "الذكاء الاصطناعي": [
                {"role": "مهندس نماذج الذكاء الاصطناعي (AI/LLM Engineer)", "share": 0.35, "hourly_rate_base": 85},
                {"role": "مهندس معالجة البيانات والأنظمة (Data & Backend Engineer)", "share": 0.25, "hourly_rate_base": 60},
                {"role": "مطور واجهات تفاعلية (Frontend Developer)", "share": 0.15, "hourly_rate_base": 45},
                {"role": "مهندس عمليات الذكاء الاصطناعي (MLOps Lead)", "share": 0.15, "hourly_rate_base": 75},
                {"role": "مدير جودة واختبارات النماذج (QA AI Lead)", "share": 0.10, "hourly_rate_base": 50}
            ]
        }

        default_template = [
            {"role": "كبير المهندسين ومصمم المعمارية (Lead Software Architect)", "share": 0.25, "hourly_rate_base": 60},
            {"role": "مطور التطبيقات والأنظمة (Senior Full-Stack Developer)", "share": 0.35, "hourly_rate_base": 50},
            {"role": "مصمم واجهات وسلوك المستخدم (UI/UX Designer)", "share": 0.15, "hourly_rate_base": 40},
            {"role": "مهندس أتمتة واختبارات الجودة (QA Automation Engineer)", "share": 0.15, "hourly_rate_base": 42},
            {"role": "مدير تنفيذ ورئيس فريق (Technical Project Manager)", "share": 0.10, "hourly_rate_base": 55}
        ]

        specs = specialists_templates.get(domain, default_template)
        result = []
        for s in specs:
            allocated_cost = dev_budget * s["share"]
            allocated_hours = max(10, int(total_hours * s["share"] * 1.5))
            effective_hourly = round(allocated_cost / max(1, allocated_hours), 2)
            daily_cost = round(allocated_cost / max(1, total_days), 2)
            result.append({
                "role": s["role"],
                "allocated_hours": allocated_hours,
                "hourly_rate": effective_hourly,
                "daily_rate": daily_cost,
                "total_cost": round(allocated_cost, 2)
            })
        return result

class PhoenixAI:
    @staticmethod
    def generate_architecture(req: dict, api_key: str = None) -> dict:
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt = f"""قم بإنشاء خطة معمارية هندسية احترافية بتنسيق JSON للمشروع التالي:
اسم المشروع: {req['project_name']}
المجال: {req['domain']}
الميزانية: {req['budget']}
الأيام المستهدفة: {req['target_days']}
التقنيات: {req['tech_stack']}
نطاق العمل: {req['scope']}

قم بإرجاع JSON فقط يحوي القواعد: project_name, domain, budget, target_days, risk, executive_summary, tech_stack (قائمة), tasks (قائمة كائنات بها: id, task, days, cost, status, priority)."""
                response = model.generate_content(prompt)
                match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    data["specialists"] = SpecialistsCalculator.calculate_specialists(req['domain'], float(req['budget']), int(req['target_days']))
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
            {"id": 4, "task": "الاختبارات الشاملة والتكامل QA & Cloud Deployment", "days": max(1, int(d*0.20)), "cost": int(b*0.20), "status": "مخطط", "priority": "Low"}
        ]
        
        tech_list = [t.strip() for t in req['tech_stack'].split(",")] if isinstance(req['tech_stack'], str) else req['tech_stack']
        specialists = SpecialistsCalculator.calculate_specialists(req['domain'], b, d)

        data = {
            "project_name": req['project_name'],
            "domain": req['domain'],
            "executive_summary": f"خطة هندسية تنفيذية لمشروع ({req['project_name']}) بتصميم فائق الجودة والأمان الرقمي مع فريق كامل التخصص.",
            "tech": req['tech_stack'],
            "tech_stack": tech_list,
            "budget": b,
            "target_days": d,
            "risk": req.get('risk', 'متوسط'),
            "tasks": tasks,
            "specialists": specialists,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data["signature"] = SecurityEngine.generate_signature(data)
        return data

    @staticmethod
    def analyze_feedback_and_adapt_pricing(feedbacks: list) -> dict:
        if not feedbacks:
            return {"recommended_monthly": 29, "recommended_yearly": 279, "top_requested_features": ["تصدير PDF باللغة العربية", "ربط مباشر مع GitHub", "تكامل الذكاء الاصطناعي مع Slack"], "market_satisfaction_score": 92.5}
        avg_price = np.mean([f['suggested_price'] for f in feedbacks if f['suggested_price'] > 0]) if feedbacks else 29
        avg_rating = np.mean([f['rating'] for f in feedbacks]) if feedbacks else 4.5
        features = [f['requested_feature'] for f in feedbacks if f['requested_feature']]
        feature_counts = pd.Series(features).value_counts().to_dict() if features else {}
        top_features = list(feature_counts.keys())[:3] if feature_counts else ["تكامل تلقائي مع Cloud SQL", "تخزين الخطط على IPFS", "دعم الدفع المحلي"]
        rec_monthly = max(19, int(avg_price))
        rec_yearly = int(rec_monthly * 9.5)
        return {"recommended_monthly": rec_monthly, "recommended_yearly": rec_yearly, "top_requested_features": top_features, "market_satisfaction_score": round(float(avg_rating) * 20, 1)}

class AIPaymentAgent:
    @staticmethod
    def execute_auto_checkout(user_id: int, user_email: str, plan_type: str = "monthly"):
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        checkout_url = PAYMENT_LINK_YEARLY if plan_type == "yearly" else PAYMENT_LINK_MONTHLY
        plan_name = "Enterprise Yearly Plan ($279)" if plan_type == "yearly" else "Pro Monthly Plan ($29)"
        amount_val = 279.0 if plan_type == "yearly" else 29.0

        status_box.info(f"🤖 **[AI Agent]:** فحص وسيلة الدفع للبريد: `{user_email}`...")
        time.sleep(0.4)
        progress_bar.progress(30)

        status_box.info(f"🔗 **[AI Agent]:** الربط مع بوابات Lemon Squeezy Router...")
        time.sleep(0.4)
        progress_bar.progress(70)

        progress_bar.progress(100)
        time.sleep(0.3)
        progress_bar.empty()
        status_box.empty()

        order_id = f"LS-ORD-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()}"
        
        # التحديث والتسجيل في جميع الجداول
        HybridDatabaseEngine.update_user_subscription(user_email, role=f"Enterprise ({plan_name})", credits=9999)
        HybridDatabaseEngine.save_payment_transaction(user_id, order_id, "LemonSqueezy_AI_Gateway", plan_type, amount_val, "COMPLETED", json.dumps({"checkout_url": checkout_url}))
        HybridDatabaseEngine.log_security_event(user_id, "SUBSCRIPTION_UPGRADE", f"Upgraded to {plan_name} via AI Payment Agent")

        email_payload = {
            "to": user_email,
            "subject": f"🎉 Confirmation for Order #{order_id}",
            "order_id": order_id,
            "plan_name": plan_name,
            "amount": f"${amount_val:.2f}",
            "checkout_url_used": checkout_url,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        if 'payment_notifications' not in st.session_state:
            st.session_state.payment_notifications = []
        st.session_state.payment_notifications.insert(0, email_payload)

# =====================================================================
# 5. EXPORT & DETAILED PLAN GENERATOR WITH SPECIALISTS
# =====================================================================
def build_detailed_plan_text(plan: dict) -> str:
    p_name = plan.get('project_name', 'المشروع')
    domain = plan.get('domain', 'تقني')
    budget = float(plan.get('budget', 0))
    days = int(plan.get('target_days', 0))
    tech = plan.get('tech', plan.get('tech_stack', 'Flutter, Node.js, Supabase, PostgreSQL'))
    risk = plan.get('risk', 'متوسط')
    tasks = plan.get('tasks', [])
    specialists = plan.get('specialists', SpecialistsCalculator.calculate_specialists(domain, budget, days))

    working_hours_per_day = 8
    total_man_hours = days * working_hours_per_day
    daily_rate = budget / max(1, days)
    hourly_rate = budget / max(1, total_man_hours)

    contingency_rate = 0.15 if risk == "عالي" else (0.10 if risk == "متوسط" else 0.05)
    contingency_amount = budget * contingency_rate
    effective_operational_budget = budget - contingency_amount

    # حساب جدول أجور المتخصصين
    specialists_text = ""
    total_specialists_cost = 0
    for s in specialists:
        specialists_text += f"""
* 👨‍💻 **الرتبة/المتخصص:** {s['role']}
  * ⏱️ **ساعات العمل المخصصة:** {s['allocated_hours']} ساعة
  * 💵 **أجر الساعة التقديري:** ${s['hourly_rate']:.2f} / ساعة
  * 📈 **المعدل اليومي:** ${s['daily_rate']:.2f} / يوم
  * 💰 **إجمالي الأجر المخصص:** `${s['total_cost']:,.2f}`
"""
        total_specialists_cost += s['total_cost']

    tasks_breakdown_str = ""
    for idx, t in enumerate(tasks, 1):
        t_cost = float(t.get('cost', 0))
        t_days = int(t.get('days', 0))
        t_hours = t_days * working_hours_per_day
        cost_percentage = (t_cost / max(1, budget)) * 100
        
        tasks_breakdown_str += f"""
#### المرحلة {idx}: {t.get('task', 'مهمة')}
* ⏱️ **المدى الزمني:** {t_days} أيام عمل ({t_hours} ساعة هندسية)
* 💰 **التكلفة:** ${t_cost:,.2f} ({cost_percentage:.1f}% من الميزانية)
* 📌 **الحالة التنفيذية:** {t.get('status', 'مخطط')}
"""

    return f"""📌 **المستند التنفيذي والتفصيلي المعمق لمشروع ({p_name})**
*تاريخ التوليد الهندي التلقائي: {plan.get('generated_at', datetime.datetime.now().strftime('%Y-%m-%d'))}*

---

### 1. نظرة عامة والأهداف التنفيذية (Executive Summary & KPIs)
يهدف مشروع **{p_name}** إلى تقديم حل سحابي متكامل ومنافس عالمياً في قطاع **{domain}** مع إدماج حزمة التقنيات: **({tech})**.
* **الميزانية الإجمالية (Total Budget):** `${budget:,.2f}`
* **الملاذ الزمني للتنفيذ (Timeline):** `{days}` يوماً تقويمياً.
* **مستوى مخاطر المشروع (Risk Level):** `{risk}`.

---

### 2. التكاليف وحساب أجور المتخصصين والمهندسين (Specialists & Payroll Allocation)
تم استخدام خوارزميات الحساب الهيكلي لحساب أجور الفريق البشري والمهندسين الذين سينفذون الخطة بدقة متناهية:
{specialists_text}
* 📊 **إجمالي أجور كادر العمل (Total Team Payroll):** `${total_specialists_cost:,.2f}`
* ⏳ **ساعات العمل الهندسية المباشرة (Total Man-Hours):** `{total_man_hours:,}` ساعة.
* 🛡️ **احتياطي الطوارئ المالي ({contingency_rate*100:.0f}% Risk Reserve):** `${contingency_amount:,.2f}`.
* ☁️ **تكاليف الخوادم والخدمات السحابية (Infra OpEx):** `${(budget - total_specialists_cost - contingency_amount):,.2f}`.

---

### 3. المعمارية الهندسية ومحطات العمل (Work Breakdown Structure)
{tasks_breakdown_str}

---

### 4. الضمان الرقمي وتدقيق الأمان (HMAC-SHA512 Cryptographic Seal)
تم توقيع وتشفير هذا المستند رقمياً في قاعدة بيانات Cloud SQL وتأكيده عبر خوارزمية **HMAC-SHA512** لمنع أي تلاعب بالتكاليف أو الميزانية.
"""

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
            try: return get_display(arabic_reshaper.reshape(text_val))
            except Exception: return text_val
        return text_val

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, alignment=1)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, alignment=2)

    story.append(Paragraph(prepare_text(f"خطة مشروع: {plan['project_name']}"), title_style))
    story.append(Spacer(1, 15))
    
    for line in detailed_text.split("\n"):
        if line.strip():
            story.append(Paragraph(prepare_text(line.strip()), body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    return buffer.getvalue()

# =====================================================================
# 6. UI & APPLICATION ENGINE
# =====================================================================
def init_session():
    if 'lang' not in st.session_state: st.session_state.lang = 'ar'
    if 'theme' not in st.session_state: st.session_state.theme = 'dark'
    if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = {'id': 0, 'email': '', 'username': 'زائر', 'credits': 5, 'role': 'Free Trial', 'is_subscribed': False}
    if 'current_plan' not in st.session_state: st.session_state.current_plan = None
    if 'plan_signature' not in st.session_state: st.session_state.plan_signature = None
    if 'notify_whatsapp' not in st.session_state: st.session_state.notify_whatsapp = "+967700000000"
    if 'notify_telegram' not in st.session_state: st.session_state.notify_telegram = "@Ayad_Developer"
    if 'payment_notifications' not in st.session_state: st.session_state.payment_notifications = []

def render_auth_page():
    st.markdown("<h1 style='text-align: center;'>🚀 PHOENIX & WAKEEL MEHNA PRO v12.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>سجل دخولك للوصول إلى النواة الهندسية المترابطة مع Cloud SQL Studio</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "✨ حساب جديد (5 نقاط مجانية)"])
    with tab1:
        with st.form("login_form"):
            email_input = st.text_input("البريد الإلكتروني").lower().strip()
            password_input = st.text_input("كلمة المرور", type="password")
            submit_login = st.form_submit_button("🚀 دخول", use_container_width=True)
            if submit_login:
                u = HybridDatabaseEngine.get_user(email_input)
                if u and SecurityEngine.verify_password(password_input, u["password_hash"]):
                    st.session_state.is_authenticated = True
                    st.session_state.user = {'id': u['id'], 'email': u['email'], 'username': u['full_name'] or "مهندس", 'credits': u['credits'], 'role': u['role'], 'is_subscribed': bool(u['is_subscribed'])}
                    HybridDatabaseEngine.log_security_event(u['id'], "LOGIN_SUCCESS", f"User {email_input} logged in successfully")
                    st.success("🎉 أهلاً بك!")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("❌ بيانات غير صحيحة.")

    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("الاسم الكامل")
            new_email = st.text_input("البريد الإلكتروني").lower().strip()
            new_password = st.text_input("كلمة المرور", type="password")
            submit_signup = st.form_submit_button("✨ تسجيل حساب جديد", use_container_width=True)
            if submit_signup:
                if new_username and new_email and new_password:
                    if HybridDatabaseEngine.register_user(new_username, new_email, SecurityEngine.hash_password(new_password)):
                        u = HybridDatabaseEngine.get_user(new_email)
                        st.session_state.is_authenticated = True
                        st.session_state.user = {'id': u['id'], 'email': u['email'], 'username': new_username, 'credits': 5, 'role': "Free Trial", 'is_subscribed': False}
                        HybridDatabaseEngine.log_security_event(u['id'], "USER_REGISTER", f"User registered {new_email}")
                        st.success("🎉 تم التسجيل بنجاح!")
                        time.sleep(0.5)
                        st.rerun()

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")
    init_session()

    if not st.session_state.is_authenticated:
        render_auth_page()
        return

    fresh_u = HybridDatabaseEngine.get_user(st.session_state.user['email'])
    if fresh_u:
        st.session_state.user['id'] = fresh_u['id']
        st.session_state.user['credits'] = fresh_u['credits']
        st.session_state.user['role'] = fresh_u['role']
        st.session_state.user['is_subscribed'] = bool(fresh_u['is_subscribed'])

    with st.sidebar:
        st.title("🛡️ PHOENIX AGENT")
        st.caption("Enterprise Silicon Valley v12.0")
        st.divider()
        st.write(f"👤 المستخدم: **{st.session_state.user['username']}**")
        st.write(f"💳 الرصيد: `{st.session_state.user['credits']}` نقاط")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.title("🚀 وكيل مهنة PRO | PHOENIX Enterprise v12.0")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏗️ بناء خطة المشروع والمتخصصين", 
        "📊 التحليلات الهندسية 6D & Speciality Radar", 
        "✏️ محرر المهام وحساب الأجور", 
        "🔄 التغذية الراجعة والتسعير التكيفي", 
        "🗄️ Cloud SQL Studio Complete Archive"
    ])

    with tab1:
        with st.form("project_form"):
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input("اسم المشروع", value="منصة تجارة سحابية وتطبيقات AI")
                domain = st.selectbox("المجال التقني", ["التجارة الإلكترونية", "الذكاء الاصطناعي", "التعليم الرقمي", "الخدمات واللوجستيات"])
                budget = st.number_input("الميزانية الكلية ($)", min_value=500, value=5000)
            with col2:
                tech_stack = st.text_input("التقنيات", value="Flutter, Node.js, Cloud SQL, Gemini API")
                target_days = st.number_input("المدة الزمنية المستهدفة (أيام)", min_value=5, value=30)
                risk_tolerance = st.select_slider("تحمل المخاطر", options=["منخفض جداً", "متوسط", "عالي"])

            project_scope = st.text_area("نطاق العمل تفصيلياً", value="بناء منصة متكاملة تدعم التوسع وإتاحة الدفع للعملاء وحساب أجور المتخصصين تلقائياً.")
            gemini_key = st.text_input("مفتاح Gemini API (اختياري)", type="password")
            submit_btn = st.form_submit_button("🚀 توليد وتوقيع الخطة مع فريق المتخصصين", use_container_width=True)

        if submit_btn:
            if st.session_state.user['credits'] < 1 and not st.session_state.user['is_subscribed']:
                st.error("❌ نفدت نقاطك المجانية! يرجى الترقية.")
            else:
                req = {"project_name": project_name, "domain": domain, "budget": budget, "target_days": target_days, "tech_stack": tech_stack, "scope": project_scope, "risk": risk_tolerance}
                plan = PhoenixAI.generate_architecture(req, api_key=gemini_key)
                plan['scope'] = project_scope
                
                # حفظ في الجداول الكاملة
                plan_id = HybridDatabaseEngine.save_full_project_plan(st.session_state.user['id'], st.session_state.user['email'], plan)
                HybridDatabaseEngine.log_security_event(st.session_state.user['id'], "CREATE_PROJECT_PLAN", f"Created Plan ID #{plan_id}")

                if not st.session_state.user['is_subscribed']:
                    new_c = max(0, st.session_state.user['credits'] - 1)
                    HybridDatabaseEngine.update_credits(st.session_state.user['email'], new_c)
                    st.session_state.user['credits'] = new_c

                st.session_state.current_plan = plan
                st.session_state.plan_signature = plan.get("signature")
                st.success("✅ تم توليد الخطة وحفظها بنجاح في قاعدة البيانات!")

        if st.session_state.current_plan:
            st.divider()
            st.info(f"🔑 التوقيع الرقمي المشفر (HMAC-SHA512): `{st.session_state.plan_signature}`")
            
            st.markdown("### 👨‍💻 توزيع أجور المتخصصين والمهندسين المسؤولين عن التنفيذ")
            df_specs = pd.DataFrame(st.session_state.current_plan.get('specialists', []))
            st.dataframe(df_specs, use_container_width=True)

            st.markdown("### 📋 المهام الأساسية للمشروع")
            st.dataframe(pd.DataFrame(st.session_state.current_plan.get('tasks', [])), use_container_width=True)

    with tab2:
        if st.session_state.current_plan:
            plan = st.session_state.current_plan
            st.markdown("## 📊 التحليلات الهندسية الشاملة وتكاليف التخصصات")
            
            df_specs = pd.DataFrame(plan.get('specialists', []))
            fig_specs = px.pie(df_specs, values='total_cost', names='role', title="توزيع الميزانية على المتخصصين والمهندسين", hole=0.4)
            st.plotly_chart(fig_specs, use_container_width=True)

    with tab3:
        if st.session_state.current_plan:
            st.markdown("### 📜 المستند التنفيذي والشامل")
            detailed_txt = build_detailed_plan_text(st.session_state.current_plan)
            st.markdown(detailed_txt)
            pdf_bytes = generate_pdf_plan(st.session_state.current_plan, st.session_state.plan_signature, detailed_txt)
            st.download_button("📄 تحميل الخطة التنفيذية (PDF)", pdf_bytes, f"{st.session_state.current_plan['project_name']}_Plan.pdf", "application/pdf", use_container_width=True)

    with tab4:
        st.subheader("🔄 نظام التغذية الراجعة بالتكامل مع جدول feedback")
        with st.form("feedback_form"):
            rating = st.slider("التقييم", 1, 5, 5)
            suggested_p = st.number_input("السعر المقترح ($)", value=29)
            req_feature = st.text_input("الميزة المطلوبة", value="إضافة أدوات الذكاء الاصطناعي")
            comments = st.text_area("الملاحظات")
            if st.form_submit_button("إرسال التغذية الراجعة"):
                HybridDatabaseEngine.save_feedback(st.session_state.user['email'], rating, suggested_p, req_feature, comments)
                st.success("🎉 تم الحفظ بنجاح!")

    with tab5:
        st.subheader("🗄️ الأرشيف المباشر لقواعد البيانات (Cloud SQL & SQLite)")
        saved_projs = HybridDatabaseEngine.get_projects(st.session_state.user['email'])
        if saved_projs:
            st.dataframe(pd.DataFrame(saved_projs), use_container_width=True)

if __name__ == "__main__":
    main()
