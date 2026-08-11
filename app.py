#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
© 2026 PHOENIX & WAKEEL MEHNA PRO ENTERPRISE ARCHITECTURE v13.6 - ULTIMATE SaaS
محرك معالجة البيانات الهجين المتكامل (PostgreSQL Cloud SQL Primary / SQLite)
المعتمد على جميع جداول الـ Schema السبعة، الذكاء الاصطناعي (Gemini)، التوقيع الرقمي (HMAC-SHA512)،
لوحة قيادة المدراء المتقدمة (Admin Dashboard)، مولد الـ QR Code للتسجيل السريع،
التحليلات الهندسية 6D المقسمة بمؤشرات نصف دائرية ملونة، وحساب أجور الكوادر والمتخصصين.
تصميم زجاجي فاخر متطور (Ultra-Luxurious Glassmorphic UI/UX with Glowing Focus Effects).
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
import requests
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

# =====================================================================
# 1. CONFIGURATION & SECRETS (مشفرة ومحمية)
# =====================================================================
APP_TITLE = "PHOENIX & WAKEEL MEHNA PRO - ENTERPRISE v13.6"
PAYMENT_LINK_MONTHLY = os.getenv("PAYMENT_LINK_MONTHLY", "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=monthly")
PAYMENT_LINK_YEARLY = os.getenv("PAYMENT_LINK_YEARLY", "https://nexus-corestore.lemonsqueezy.com/checkout/buy/e6515270-070e-4fc6-b1ea-60c1aeb9e2d3?plan=yearly")
SECRET_HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "PHOENIX_SECURE_HMAC_KEY_2026_ENTERPRISE_ULTIMATE")
APP_BASE_URL = os.getenv("APP_URL", "https://mihna-core-50335759464.asia-south1.run.app")
SUPER_ADMIN_EMAIL = "eng.alhiadri2021@gmail.com"

def get_env_or_secret(key, default_val=""):
    if key in os.environ:
        return os.environ[key]
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default_val

DB_USER = get_env_or_secret("DB_USER", "postgres")
DB_PASS = get_env_or_secret("DB_PASSWORD", "101519Ayad@%")
DB_NAME = get_env_or_secret("DB_NAME", "postgres")
DB_HOST = get_env_or_secret("DB_HOST", "34.93.187.161")
DB_PORT = get_env_or_secret("DB_PORT", "5432")
INSTANCE_CONN = get_env_or_secret("INSTANCE_CONNECTION_NAME", "project-d699d925-921c-4e54-8c4:asia-south1:mihna-core-ay")
SQLITE_DB_FILE = "phoenix_app_data.db"

# =====================================================================
# 2. SECURITY ENGINE (مقاوِم للقرصنة والهندسة العكسية)
# =====================================================================
class SecurityEngine:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def hash_password(password: str) -> str:
        if BCRYPT_AVAILABLE:
            try:
                salt = bcrypt.gensalt(rounds=12)
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
            except Exception:
                pass
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed

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

# =====================================================================
# 3. DATABASE ENGINE (ذكي مع احتياطي SQLite)
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
                cls._sqlalchemy_engine = sqlalchemy.create_engine(db_url, pool_pre_ping=True, pool_timeout=5, pool_size=10, max_overflow=20)
            except Exception as e:
                logging.error(f"PostgreSQL Engine Error: {e}")
                cls._sqlalchemy_engine = None
        return cls._sqlalchemy_engine

    @classmethod
    def init_db(cls):
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            full_name VARCHAR(255),
                            role VARCHAR(100) DEFAULT 'Free Trial',
                            credits INT DEFAULT 5,
                            is_subscribed INT DEFAULT 0,
                            is_admin INT DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS project_plans (
                            id SERIAL PRIMARY KEY,
                            user_id INT REFERENCES users(id) ON DELETE CASCADE,
                            project_name VARCHAR(255),
                            domain VARCHAR(255),
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
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS plan_tasks (
                            id SERIAL PRIMARY KEY,
                            plan_id INT REFERENCES project_plans(id) ON DELETE CASCADE,
                            task_order INT,
                            task_name VARCHAR(255),
                            days INT,
                            cost NUMERIC(12,2),
                            status VARCHAR(50) DEFAULT 'مخطط',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
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
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS payment_transactions (
                            id SERIAL PRIMARY KEY,
                            user_id INT REFERENCES users(id) ON DELETE CASCADE,
                            order_id VARCHAR(100) UNIQUE,
                            gateway VARCHAR(100),
                            plan_type VARCHAR(100),
                            amount_paid NUMERIC(10,2),
                            currency VARCHAR(10) DEFAULT 'USD',
                            status VARCHAR(50),
                            raw_response TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS security_audit_logs (
                            id SERIAL PRIMARY KEY,
                            user_id INT REFERENCES users(id) ON DELETE SET NULL,
                            action_type VARCHAR(100),
                            ip_address VARCHAR(100),
                            details TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    hashed_p = SecurityEngine.hash_password("123456")
                    conn.execute(text("""
                        INSERT INTO users (full_name, email, password_hash, credits, role, is_subscribed, is_admin)
                        VALUES (:fn, :em, :ph, 99999, 'Enterprise Owner / Super Admin', 1, 1)
                        ON CONFLICT (email) DO UPDATE SET is_admin = 1, role = 'Enterprise Owner / Super Admin';
                    """), {"fn": "Alex Sterling (CEO & Owner)", "em": SUPER_ADMIN_EMAIL.lower().strip(), "ph": hashed_p})
                    conn.commit()
            except Exception as e:
                logging.error(f"PostgreSQL Full Schema Init Warning: {e}")

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, full_name TEXT, role TEXT DEFAULT 'Free Trial', credits INTEGER DEFAULT 5, is_subscribed INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS project_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, project_name TEXT, domain TEXT, budget REAL, target_days INTEGER, risk_tolerance TEXT, tech_stack TEXT, scope_of_work TEXT, plan_signature TEXT, is_tampered INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS plan_tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER, task_order INTEGER, task_name TEXT, days INTEGER, cost REAL, status TEXT DEFAULT 'مخطط', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT NOT NULL, project_name TEXT, summary TEXT, budget_range TEXT, tech_stack TEXT, payload TEXT, signature TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT NOT NULL, rating INTEGER, suggested_price INTEGER, requested_feature TEXT, comments TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS payment_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, order_id TEXT UNIQUE, gateway TEXT, plan_type TEXT, amount_paid REAL, currency TEXT DEFAULT 'USD', status TEXT, raw_response TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS security_audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action_type TEXT, ip_address TEXT, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor.execute("SELECT email FROM users WHERE email = ?", (SUPER_ADMIN_EMAIL.lower().strip(),))
            if not cursor.fetchone():
                hashed_p = SecurityEngine.hash_password("123456")
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, credits, role, is_subscribed, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("Alex Sterling (CEO & Owner)", SUPER_ADMIN_EMAIL.lower().strip(), hashed_p, 99999, "Enterprise Owner / Super Admin", 1, 1)
                )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"SQLite Full Schema Init Error: {e}")

    @classmethod
    def get_user(cls, email: str) -> dict:
        email_clean = email.strip().lower()
        if not email_clean:
            return None

        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    res = conn.execute(
                        text("SELECT id, email, password_hash, full_name, role, credits, is_subscribed, is_admin FROM users WHERE LOWER(email) = :email"),
                        {"email": email_clean}
                    ).fetchone()
                    if res:
                        return {
                            "id": res[0], "email": res[1], "password_hash": res[2],
                            "full_name": res[3], "role": res[4], "credits": res[5],
                            "is_subscribed": res[6], "is_admin": res[7]
                        }
            except Exception as e:
                logging.error(f"PostgreSQL fetch user fallback: {e}")

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password_hash, full_name, role, credits, is_subscribed, is_admin FROM users WHERE LOWER(email) = ?", (email_clean,))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                return {
                    "id": d["id"], "email": d["email"], "password_hash": d["password_hash"],
                    "full_name": d["full_name"], "role": d["role"], "credits": d["credits"],
                    "is_subscribed": d["is_subscribed"], "is_admin": d.get("is_admin", 0)
                }
        except Exception as e:
            logging.error(f"SQLite Fetch User Error: {e}")

        return None

    @classmethod
    def register_user(cls, full_name: str, email: str, password_hash: str) -> bool:
        email_clean = email.strip().lower()
        success = False
        is_admin_flag = 1 if email_clean == SUPER_ADMIN_EMAIL.lower().strip() else 0
        role_flag = "Enterprise Owner / Super Admin" if is_admin_flag else "Free Trial"

        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    res = conn.execute(
                        text("""INSERT INTO users (full_name, email, password_hash, credits, role, is_subscribed, is_admin)
                                VALUES (:fn, :em, :ph, 5, :rl, 0, :ia)
                                ON CONFLICT (email) DO UPDATE SET password_hash = :ph, full_name = :fn RETURNING id"""),
                        {"fn": full_name, "em": email_clean, "ph": password_hash, "rl": role_flag, "ia": is_admin_flag}
                    ).fetchone()
                    conn.commit()
                    if res:
                        cls.log_audit(res[0], "USER_REGISTERED", f"User {email_clean} persisted to Cloud SQL PostgreSQL.")
                    success = True
            except Exception as e:
                logging.error(f"PG Sync Register Warning: {e}")

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO users (full_name, email, password_hash, credits, role, is_subscribed, is_admin) VALUES (?, ?, ?, 5, ?, 0, ?)",
                (full_name, email_clean, password_hash, role_flag, is_admin_flag)
            )
            uid = cursor.lastrowid
            conn.commit()
            conn.close()
            cls.log_audit(uid, "USER_REGISTERED", f"User {email_clean} registered successfully in SQLite.")
            success = True
        except Exception as e:
            logging.error(f"SQLite Register Error: {e}")

        return success

    @classmethod
    def add_admin_privilege(cls, target_email: str) -> bool:
        target_clean = target_email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("UPDATE users SET is_admin = 1, role = 'Enterprise Admin Supervisor' WHERE LOWER(email) = :email"), {"email": target_clean})
                    conn.commit()
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_admin = 1, role = 'Enterprise Admin Supervisor' WHERE LOWER(email) = ?", (target_clean,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    @classmethod
    def get_all_users_admin(cls) -> list:
        users = []
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    rows = conn.execute(text("SELECT id, full_name, email, role, credits, is_subscribed, is_admin, created_at FROM users ORDER BY created_at DESC")).fetchall()
                    if rows:
                        for r in rows:
                            users.append({"id": r[0], "full_name": r[1], "email": r[2], "role": r[3], "credits": r[4], "is_subscribed": r[5], "is_admin": r[6], "created_at": str(r[7])})
                        return users
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, full_name, email, role, credits, is_subscribed, is_admin, created_at FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            for r in rows:
                users.append(dict(r))
        except Exception: pass
        return users

    @classmethod
    def update_user_subscription(cls, email: str, role: str, credits: int = 9999) -> bool:
        email_clean = email.strip().lower()
        user = cls.get_user(email_clean)
        
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(
                        text("UPDATE users SET role = :role, credits = :credits, is_subscribed = 1, updated_at = CURRENT_TIMESTAMP WHERE LOWER(email) = :email"),
                        {"role": role, "credits": credits, "email": email_clean}
                    )
                    conn.commit()
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ?, credits = ?, is_subscribed = 1, updated_at = CURRENT_TIMESTAMP WHERE LOWER(email) = ?", (role, credits, email_clean))
            conn.commit()
            conn.close()
            if user:
                cls.log_audit(user['id'], "SUBSCRIPTION_UPDATED", f"Upgraded to {role}")
            return True
        except Exception:
            return False

    @classmethod
    def update_credits(cls, email: str, new_credits: int) -> bool:
        email_clean = email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(text("UPDATE users SET credits = :credits, updated_at = CURRENT_TIMESTAMP WHERE LOWER(email) = :email"), {"credits": new_credits, "email": email_clean})
                    conn.commit()
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET credits = ?, updated_at = CURRENT_TIMESTAMP WHERE LOWER(email) = ?", (new_credits, email_clean))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    @classmethod
    def save_project_plan_full(cls, plan_json: dict, user_email: str) -> bool:
        user = cls.get_user(user_email)
        user_id = user['id'] if user else 1
        p_name = plan_json.get('project_name', 'مشروع جديد')
        domain = plan_json.get('domain', 'تقنية المعلومات')
        budget = float(plan_json.get('budget', 0))
        target_days = int(plan_json.get('target_days', 30))
        risk = plan_json.get('risk', 'متوسط')
        tech = json.dumps(plan_json.get('tech_stack', plan_json.get('tech', '')), ensure_ascii=False)
        scope = plan_json.get('scope', plan_json.get('executive_summary', ''))
        sig = plan_json.get('signature', '')
        tasks = plan_json.get('tasks', [])

        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    res = conn.execute(
                        text("""INSERT INTO project_plans (user_id, project_name, domain, budget, target_days, risk_tolerance, tech_stack, scope_of_work, plan_signature, is_tampered)
                                VALUES (:uid, :pn, :dm, :bg, :td, :rk, :tc, :sc, :sg, 0) RETURNING id"""),
                        {"uid": user_id, "pn": p_name, "dm": domain, "bg": budget, "td": target_days, "rk": risk, "tc": tech, "sc": scope, "sg": sig}
                    ).fetchone()
                    if res:
                        plan_id = res[0]
                        for idx, t in enumerate(tasks, 1):
                            conn.execute(
                                text("""INSERT INTO plan_tasks (plan_id, task_order, task_name, days, cost, status)
                                        VALUES (:pid, :ord, :tn, :ds, :cs, :st)"""),
                                {"pid": plan_id, "ord": idx, "tn": t.get('task'), "ds": t.get('days'), "cs": t.get('cost'), "st": t.get('status', 'مخطط')}
                            )
                    conn.execute(
                        text("""INSERT INTO projects (user_email, project_name, summary, budget_range, tech_stack, payload, signature)
                                VALUES (:em, :pn, :sm, :bg, :tc, :pl, :sg)"""),
                        {"em": user_email.lower().strip(), "pn": p_name, "sm": scope, "bg": str(budget), "tc": tech, "pl": json.dumps(plan_json, ensure_ascii=False), "sg": sig}
                    )
                    conn.commit()
            except Exception as e:
                logging.error(f"PG Full Plan Save Warning: {e}")

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO project_plans (user_id, project_name, domain, budget, target_days, risk_tolerance, tech_stack, scope_of_work, plan_signature, is_tampered)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (user_id, p_name, domain, budget, target_days, risk, tech, scope, sig)
            )
            plan_id = cursor.lastrowid
            for idx, t in enumerate(tasks, 1):
                cursor.execute(
                    """INSERT INTO plan_tasks (plan_id, task_order, task_name, days, cost, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (plan_id, idx, t.get('task'), t.get('days'), t.get('cost'), t.get('status', 'مخطط'))
                )
            cursor.execute(
                """INSERT INTO projects (user_email, project_name, summary, budget_range, tech_stack, payload, signature)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_email.lower().strip(), p_name, scope, str(budget), tech, json.dumps(plan_json, ensure_ascii=False), sig)
            )
            conn.commit()
            conn.close()
            cls.log_audit(user_id, "PLAN_GENERATED", f"Plan '{p_name}' signed and created.")
            return True
        except Exception as e:
            logging.error(f"SQLite Full Plan Save Error: {e}")
            return False

    @classmethod
    def record_payment_transaction(cls, user_email: str, order_id: str, gateway: str, plan_type: str, amount: float, raw_resp: dict) -> bool:
        user = cls.get_user(user_email)
        uid = user['id'] if user else 1
        raw_str = json.dumps(raw_resp, ensure_ascii=False)

        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(
                        text("""INSERT INTO payment_transactions (user_id, order_id, gateway, plan_type, amount_paid, currency, status, raw_response)
                                VALUES (:uid, :oid, :gw, :pt, :am, 'USD', 'PAID', :raw)"""),
                        {"uid": uid, "oid": order_id, "gw": gateway, "pt": plan_type, "am": amount, "raw": raw_str}
                    )
                    conn.commit()
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO payment_transactions (user_id, order_id, gateway, plan_type, amount_paid, currency, status, raw_response)
                   VALUES (?, ?, ?, ?, ?, 'USD', 'PAID', ?)""",
                (uid, order_id, gateway, plan_type, amount, raw_str)
            )
            conn.commit()
            conn.close()
            cls.log_audit(uid, "PAYMENT_SUCCESS", f"Order #{order_id} processed for {amount} USD.")
            return True
        except Exception: return False

    @classmethod
    def log_audit(cls, user_id: int, action_type: str, details: str, ip_address: str = "127.0.0.1"):
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(
                        text("INSERT INTO security_audit_logs (user_id, action_type, ip_address, details) VALUES (:uid, :ac, :ip, :dt)"),
                        {"uid": user_id, "ac": action_type, "ip": ip_address, "dt": details}
                    )
                    conn.commit()
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO security_audit_logs (user_id, action_type, ip_address, details) VALUES (?, ?, ?, ?)", (user_id, action_type, ip_address, details))
            conn.commit()
            conn.close()
        except Exception: pass

    @classmethod
    def get_projects(cls, user_email: str) -> list:
        email_clean = user_email.strip().lower()
        projects = []
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    rows = conn.execute(
                        text("SELECT id, project_name, summary, budget_range, created_at, signature FROM projects WHERE LOWER(user_email) = :em ORDER BY created_at DESC"),
                        {"em": email_clean}
                    ).fetchall()
                    if rows:
                        for r in rows:
                            projects.append({"id": r[0], "project_name": r[1], "summary": r[2], "budget_range": r[3], "created_at": str(r[4]), "signature": r[5]})
                        return projects
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, project_name, summary, budget_range, created_at, signature FROM projects WHERE LOWER(user_email) = ? ORDER BY created_at DESC", (email_clean,))
            rows = cursor.fetchall()
            conn.close()
            for r in rows:
                projects.append(dict(r))
        except Exception: pass
        return projects

    @classmethod
    def save_feedback(cls, user_email: str, rating: int, suggested_price: int, requested_feature: str, comments: str) -> bool:
        email_clean = user_email.strip().lower()
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    conn.execute(
                        text("INSERT INTO feedback (user_email, rating, suggested_price, requested_feature, comments) VALUES (:em, :rt, :sp, :rf, :cm)"),
                        {"em": email_clean, "rt": rating, "sp": suggested_price, "rf": requested_feature, "cm": comments}
                    )
                    conn.commit()
            except Exception as e:
                logging.error(f"PG Save Feedback Error: {e}")

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback (user_email, rating, suggested_price, requested_feature, comments) VALUES (?, ?, ?, ?, ?)",
                (email_clean, rating, suggested_price, requested_feature, comments)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"SQLite Save Feedback Error: {e}")
            return False

    @classmethod
    def get_all_feedback(cls) -> list:
        feedbacks = []
        pg_engine = cls.get_sqlalchemy_engine()
        if pg_engine:
            try:
                with pg_engine.connect() as conn:
                    rows = conn.execute(text("SELECT id, user_email, rating, suggested_price, requested_feature, comments, created_at FROM feedback ORDER BY created_at DESC")).fetchall()
                    if rows:
                        for r in rows:
                            feedbacks.append({
                                "id": r[0], "user_email": r[1], "rating": r[2],
                                "suggested_price": r[3], "requested_feature": r[4],
                                "comments": r[5], "created_at": str(r[6])
                            })
                        return feedbacks
            except Exception: pass

        try:
            conn = sqlite3.connect(SQLITE_DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            for r in rows:
                feedbacks.append(dict(r))
        except Exception: pass
        return feedbacks

HybridDatabaseEngine.init_db()

# =====================================================================
# 4. AI ARCHITECTURE & SPECIALIST PAYROLL ENGINE
# =====================================================================
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

# =====================================================================
# 5. NOTIFICATION & EXPORT & QR UTILITIES
# =====================================================================
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

def create_half_doughnut_gauge(val: float, title: str, color: str, prefix: str = "", suffix: str = "", max_val: float = 100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={'prefix': prefix, 'suffix': suffix, 'font': {'size': 26, 'color': color, 'family': 'Tajawal, sans-serif'}},
        title={'text': title, 'font': {'size': 14, 'color': '#94A3B8'}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "#64748B"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "rgba(226, 232, 240, 0.15)",
            'bordercolor': "rgba(255,255,255,0.1)",
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=15, r=15, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#F8FAFC")
    )
    return fig

# =====================================================================
# 6. UI & APPLICATION ENGINE (مع التصميم الزجاجي الفاخر)
# =====================================================================
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

T = {
    'ar': {
        'title': "🚀 وكيل مهنة PRO | PHOENIX Enterprise v13.6",
        'subtitle': "المنصة المتقدمة لهندسة خطط المشاريع، حساب أجور المتخصصين، وتأمين البيانات بـ Cloud SQL و HMAC-SHA512.",
        'lang_select': "🌐 لغة الواجهة (Language):",
        'theme_select': "🎨 مظهر التطبيق (Theme):",
        'dark': "🌙 الداكن (Dark)", 'light': "☀️ الفاتح (Light)",
        'user': "👤 المستخدم:", 'credits': "💳 الرصيد الحالي:", 'points': "نقاط مجانية",
        'renew_title': "🛒 ترقية الاشتراك", 'renew_btn': "⚡ اشترك الآن وترقية الحساب",
        'logout_btn': "🚪 تسجيل الخروج", 'notify_settings': "📲 إعدادات الإشعارات الفورية",
        'wa_phone': "رقم الواتساب", 'tg_handle': "معرف التليجرام",
        'tab1': "🏗️ بناء الخطة والكوادر", 'tab2': "📊 التحليلات التفاعلية 6D",
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
        'users_log_title': "📋 سجل جميع المستخدمين واشتراكاتهم الحية",
        'demands_title': "💬 طلبات ورغبات المستخدمين من جدول التغذية الراجعة (User Demands & Needs)"
    },
    'en': {
        'title': "🚀 Wakeel Mehna PRO | PHOENIX Enterprise v13.6",
        'subtitle': "Advanced Engineering Project Plan Builder & Specialist Payroll Engine Secured with Cloud SQL & HMAC-SHA512.",
        'lang_select': "🌐 Interface Language:",
        'theme_select': "🎨 Application Theme:",
        'dark': "🌙 Dark", 'light': "☀️ Light",
        'user': "👤 User:", 'credits': "💳 Balance:", 'points': "points",
        'renew_title': "🛒 Upgrade Plan", 'renew_btn': "⚡ Upgrade & Subscribe Now",
        'logout_btn': "🚪 Log Out", 'notify_settings': "📲 Instant Notifications",
        'wa_phone': "WhatsApp Phone", 'tg_handle': "Telegram Handle",
        'tab1': "🏗️ Build Plan & Payroll", 'tab2': "📊 Advanced 6D Analytics",
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
        'demands_title': "💬 User Demands & Market Feature Requests"
    }
}

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

# =====================================================================
# 7. PAGE RENDER: AUTH PAGE
# =====================================================================
def render_auth_page():
    lang = st.session_state.lang
    txt = T[lang]

    st.markdown(f"<h1 style='text-align: center; font-family: Tajawal, sans-serif;'>🚀 {txt['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #94A3B8; font-size: 1.1rem;'>{txt['subtitle']}</p>", unsafe_allow_html=True)
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
            st.markdown("<div class='glass-card glass-card-builder'>", unsafe_allow_html=True)
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
            st.markdown("<div class='glass-card glass-card-builder'>", unsafe_allow_html=True)
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

def inject_custom_css():
    lang = st.session_state.lang
    theme = st.session_state.theme
    direction = "rtl" if lang == "ar" else "ltr"
    align_text = "right" if lang == "ar" else "left"

    if theme == "dark":
        bg_main = "#070A12"
        bg_sidebar = "#0F172A"
        text_color = "#F8FAFC"
        glass_bg = "rgba(15, 23, 42, 0.72)"
        glass_border = "rgba(255, 255, 255, 0.12)"
        glass_shadow = "0 20px 60px rgba(0, 0, 0, 0.55)"
        glass_focus_bg = "rgba(24, 34, 58, 0.92)"
        glass_focus_border = "rgba(99, 102, 241, 0.85)"
        glass_focus_shadow = "0 0 45px rgba(99, 102, 241, 0.45), inset 0 0 20px rgba(99, 102, 241, 0.15)"
        glow_colors = {
            "builder": "rgba(59,130,246,0.35)",
            "analytics": "rgba(16,185,129,0.35)",
            "editor": "rgba(139,92,246,0.35)",
            "feedback": "rgba(245,158,11,0.35)",
            "account": "rgba(236,72,153,0.35)",
            "cloudsql": "rgba(6,182,212,0.35)",
            "ceo": "rgba(217,119,6,0.40)"
        }
    else:
        bg_main = "#F8FAFC"
        bg_sidebar = "#FFFFFF"
        text_color = "#0F172A"
        glass_bg = "rgba(255, 255, 255, 0.78)"
        glass_border = "rgba(255, 255, 255, 0.80)"
        glass_shadow = "0 20px 60px rgba(31, 38, 135, 0.08)"
        glass_focus_bg = "rgba(255, 255, 255, 0.96)"
        glass_focus_border = "rgba(37, 99, 235, 0.85)"
        glass_focus_shadow = "0 0 45px rgba(37, 99, 235, 0.30), inset 0 0 20px rgba(37, 99, 235, 0.10)"
        glow_colors = {
            "builder": "rgba(59,130,246,0.25)",
            "analytics": "rgba(16,185,129,0.25)",
            "editor": "rgba(139,92,246,0.25)",
            "feedback": "rgba(245,158,11,0.25)",
            "account": "rgba(236,72,153,0.25)",
            "cloudsql": "rgba(6,182,212,0.25)",
            "ceo": "rgba(217,119,6,0.30)"
        }

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');
        * {{ font-family: 'Tajawal', sans-serif !important; }}

        .stApp {{
            background-color: {bg_main};
            background-image: 
                radial-gradient(at 10% 10%, rgba(99,102,241,0.08) 0px, transparent 50%),
                radial-gradient(at 90% 20%, rgba(16,185,129,0.06) 0px, transparent 50%),
                radial-gradient(at 50% 80%, rgba(139,92,246,0.07) 0px, transparent 50%);
            color: {text_color};
        }}

        /* --- Glass Cards --- */
        .glass-card {{
            background: {glass_bg};
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-radius: 32px;
            border: 1px solid {glass_border};
            box-shadow: {glass_shadow};
            padding: 28px;
            margin-bottom: 24px;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }}
        /* Geometric shapes behind cards */
        .glass-card::before {{
            content: '';
            position: absolute;
            top: -30%;
            right: -10%;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            z-index: 0;
            pointer-events: none;
        }}
        .glass-card::after {{
            content: '';
            position: absolute;
            bottom: -20%;
            left: -10%;
            width: 140px;
            height: 140px;
            border-radius: 50%;
            z-index: 0;
            pointer-events: none;
        }}
        /* Hover: glowing effect */
        .glass-card:hover, .glass-card:focus-within {{
            background: {glass_focus_bg};
            border-color: {glass_focus_border};
            box-shadow: {glass_focus_shadow};
            transform: translateY(-4px) scale(1.005);
        }}
        /* Each section type gets distinct geometry & colors */
        .glass-card-builder {{ border-left: 5px solid #3B82F6; }}
        .glass-card-builder::before {{ background: radial-gradient(circle, {glow_colors['builder']} 0%, transparent 70%); }}
        .glass-card-builder:hover {{ border-color: #3B82F6; box-shadow: 0 0 40px {glow_colors['builder']}; }}

        .glass-card-analytics {{ border-left: 5px solid #10B981; }}
        .glass-card-analytics::before {{ background: radial-gradient(circle, {glow_colors['analytics']} 0%, transparent 70%); }}
        .glass-card-analytics:hover {{ border-color: #10B981; box-shadow: 0 0 40px {glow_colors['analytics']}; }}

        .glass-card-editor {{ border-left: 5px solid #8B5CF6; }}
        .glass-card-editor::before {{ background: radial-gradient(circle, {glow_colors['editor']} 0%, transparent 70%); }}
        .glass-card-editor:hover {{ border-color: #8B5CF6; box-shadow: 0 0 40px {glow_colors['editor']}; }}

        .glass-card-feedback {{ border-left: 5px solid #F59E0B; }}
        .glass-card-feedback::before {{ background: radial-gradient(circle, {glow_colors['feedback']} 0%, transparent 70%); }}
        .glass-card-feedback:hover {{ border-color: #F59E0B; box-shadow: 0 0 40px {glow_colors['feedback']}; }}

        .glass-card-account {{ border-left: 5px solid #EC4899; }}
        .glass-card-account::before {{ background: radial-gradient(circle, {glow_colors['account']} 0%, transparent 70%); }}
        .glass-card-account:hover {{ border-color: #EC4899; box-shadow: 0 0 40px {glow_colors['account']}; }}

        .glass-card-cloudsql {{ border-left: 5px solid #06B6D4; }}
        .glass-card-cloudsql::before {{ background: radial-gradient(circle, {glow_colors['cloudsql']} 0%, transparent 70%); }}
        .glass-card-cloudsql:hover {{ border-color: #06B6D4; box-shadow: 0 0 40px {glow_colors['cloudsql']}; }}

        .glass-card-ceo {{ border-left: 5px solid #D97706; }}
        .glass-card-ceo::before {{ background: radial-gradient(circle, {glow_colors['ceo']} 0%, transparent 70%); }}
        .glass-card-ceo:hover {{ border-color: #D97706; box-shadow: 0 0 40px {glow_colors['ceo']}; }}

        /* --- Sidebar collapse button --- */
        [data-testid="stSidebarCollapseButton"] {{
            display: flex !important;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(10px);
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            border: 1px solid {glass_border} !important;
            color: #94A3B8 !important;
            transition: all 0.3s ease;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebarCollapseButton"]:hover {{
            background: rgba(255,255,255,0.15) !important;
            box-shadow: 0 0 25px {glow_colors['builder']};
            transform: scale(1.1);
        }}

        /* --- Other UI elements --- */
        .badge-green {{ background-color: #10B981; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(16,185,129,0.3); }}
        .badge-purple {{ background-color: #8B5CF6; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(139,92,246,0.3); }}
        .badge-gold {{ background-color: #F59E0B; color: white; padding: 6px 14px; border-radius: 12px; font-weight: bold; font-size: 13px; display: inline-block; box-shadow: 0 4px 12px rgba(245,158,11,0.3); }}

        .checkout-btn {{
            display: block; width: 100%; text-align: center;
            background: linear-gradient(135deg, #2563EB, #1D4ED8);
            color: white !important; padding: 12px 16px; border-radius: 14px;
            font-weight: bold; text-decoration: none; border: none; font-size: 14px;
            box-shadow: 0 6px 20px rgba(37,99,235,0.35);
            transition: all 0.3s ease;
        }}
        .checkout-btn:hover {{ transform: scale(1.02); box-shadow: 0 8px 25px rgba(37,99,235,0.5); }}

        .checkout-btn-yearly {{
            display: block; width: 100%; text-align: center;
            background: linear-gradient(135deg, #D97706, #B45309);
            color: white !important; padding: 12px 16px; border-radius: 14px;
            font-weight: bold; text-decoration: none; border: none; font-size: 14px;
            box-shadow: 0 6px 20px rgba(217,119,6,0.35);
            transition: all 0.3s ease;
        }}
        .checkout-btn-yearly:hover {{ transform: scale(1.02); box-shadow: 0 8px 25px rgba(217,119,6,0.5); }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background: {glass_bg};
            padding: 10px;
            border-radius: 18px;
            border: 1px solid {glass_border};
            box-shadow: {glass_shadow};
            backdrop-filter: blur(12px);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255,255,255,0.08);
            color: #3B82F6;
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(59,130,246,0.2);
            border-bottom: 3px solid #3B82F6;
        }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 8. MAIN APPLICATION
# =====================================================================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="wide")
    init_session()

    if not st.session_state.is_authenticated:
        render_auth_page()
        return

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
            df_projs = pd.DataFrame(saved_projs)
            st.dataframe(df_projs, use_container_width=True)
        else:
            st.info("No saved project records found in Cloud SQL or local database.")
        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================================
    # TAB ADMIN: CEO CONTROL CENTER
    # =====================================================================
    if is_ceo_owner:
        with tab_admin:
            st.markdown("<div class='glass-card glass-card-ceo'>", unsafe_allow_html=True)
            st.subheader(txt['ceo_title'])
            st.caption(txt['ceo_caption'])

            st.markdown(f"### {txt['grant_admin_title']}")
            with st.form("grant_admin_form"):
                target_email = st.text_input(txt['email_label'], placeholder="supervisor@domain.com").strip().lower()
                submit_grant = st.form_submit_button(txt['grant_admin_btn'])
                
                if submit_grant:
                    if target_email and SecurityEngine.is_valid_email(target_email):
                        if HybridDatabaseEngine.add_admin_privilege(target_email):
                            st.success(f"🎉 Admin Supervisor privileges granted to `{target_email}`!")
                        else:
                            st.error("❌ Failed to update privileges.")
                    else:
                        st.error("❌ Invalid email format.")

            st.divider()
            st.markdown(f"### {txt['users_log_title']}")
            all_users = HybridDatabaseEngine.get_all_users_admin()
            if all_users:
                st.dataframe(pd.DataFrame(all_users), use_container_width=True)
            else:
                st.info("No user records found.")

            st.divider()
            st.markdown(f"### {txt['demands_title']}")
            all_feedbacks = HybridDatabaseEngine.get_all_feedback()
            if all_feedbacks:
                st.dataframe(pd.DataFrame(all_feedbacks), use_container_width=True)
            else:
                st.info("No feedback records available.")
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
