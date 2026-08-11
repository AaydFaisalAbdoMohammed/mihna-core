#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
import logging
from urllib.parse import quote_plus
import streamlit as st

from utils import SecurityEngine

try:
    import sqlalchemy
    from sqlalchemy import text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

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
