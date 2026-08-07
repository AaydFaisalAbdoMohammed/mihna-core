#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""وحدة الاتصال بقاعدة البيانات PostgreSQL (Cloud SQL) - متوافقة مع Cloud Run

والتطوير المحلي.
"""

import json
import os
from google.cloud.sql.connector import Connector
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
import streamlit as st

# ============================================================
# بيانات الاتصال (المستخرجة دقيقاً من الشاشة المعروضة)
# ============================================================
CLOUD_SQL_CONNECTION_NAME = os.getenv(
    "CLOUD_SQL_CONNECTION_NAME",
    "project-d699d925-921c-4e54-8c4:asia-south1:mihna-core-ay",
)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "101519Ayad@!")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "34.93.187.161")
DB_PORT = int(os.getenv("DB_PORT", 5432))

# كائن الـ Connector المدار آلياً من Google
connector = Connector()


# ============================================================
# دوال الاتصال المتطورة
# ============================================================
def get_db_connection():
  """إنشاء اتصال آمن وبكفاءة عالية بقاعدة بيانات PostgreSQL."""
  # 1. المحاولة الأولى: عبر Google Cloud SQL Connector (الأكثر أماناً واحترافية)
  try:
    conn = connector.connect(
        CLOUD_SQL_CONNECTION_NAME,
        "psycopg2",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        timeout=10,
    )
    return conn
  except Exception as e_connector:
    # 2. المحاولة الثانية: الاتصال المباشر عبر TCP/IP (للبيئات الخارجية أو التطوير المحلي)
    try:
      conn = psycopg2.connect(
          host=DB_HOST,
          port=DB_PORT,
          user=DB_USER,
          password=DB_PASSWORD,
          dbname=DB_NAME,
          connect_timeout=10,
      )
      return conn
    except OperationalError as e_tcp:
      st.error(
          f"❌ فشل الاتصال بقاعدة البيانات (TCP/IP): {e_tcp}\n"
          "💡 تأكد من إضافة الـ IP الحالي إلى قائمة 'Authorized Networks' في"
          " Cloud SQL."
      )
      return None
    except Exception as e_gen:
      st.error(f"❌ خطأ غير متوقع في الاتصال: {e_gen}")
      return None


def save_to_cloudsql(project_data, user_id=None):
  """حفظ بيانات المشروع والمهام في قاعدة البيانات بالاعتماد على PostgreSQL Transactions."""
  if user_id is None:
    user_id = st.session_state.get("user_id")

  if user_id is None:
    st.error("⚠️ يجب تسجيل الدخول أولاً")
    return False

  conn = get_db_connection()
  if not conn:
    return False

  try:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
      # التحقق من وجود المستخدم
      cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
      if not cursor.fetchone():
        st.error("⚠️ المستخدم غير موجود")
        conn.close()
        return False

      # إضافة المشروع مع إرجاع الـ ID الجديد (PostgreSQL RETURNING Syntax)
      cursor.execute(
          """
                INSERT INTO projects (user_id, client_name, summary, tech_stack, budget_range, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """,
          (
              user_id,
              project_data.get("client_name", "عميل غير معروف")[:255],
              project_data.get("project_summary", "لا يوجد ملخص")[:5000],
              json.dumps(project_data.get("suggested_tech_stack", [])),
              project_data.get("estimated_budget_range", "غير محدد")[:100],
              "pending",
          ),
      )

      project_id = cursor.fetchone()["id"]

      # إضافة المهام المرتبطة بالطلب
      tasks = project_data.get("generated_tasks", [])
      if tasks:
        task_records = [
            (
                project_id,
                t.get("title", "مهمة بدون عنوان")[:255],
                t.get("description", "لا يوجد وصف")[:1000],
                t.get("estimated_days", 2),
                t.get("priority", "Medium"),
                "open",
            )
            for t in tasks
        ]

        cursor.executemany(
            """
                    INSERT INTO tasks (project_id, title, description, estimated_days, priority, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
            task_records,
        )

      conn.commit()
      return True

  except Exception as e:
    conn.rollback()
    st.error(f"❌ خطأ أثنـاء تنفيذ الاستعلام: {e}")
    return False
  finally:
    conn.close()


def get_similar_projects(idea, top_k=2):
  """البحث عن مشاريع مشابهة."""
  conn = get_db_connection()
  if not conn:
    return []

  try:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
      cursor.execute(
          """
                SELECT id, client_name, summary, tech_stack, budget_range
                FROM projects
                WHERE summary ILIKE %s
                LIMIT %s
            """,
          (f"%{idea[:50]}%", top_k),
      )
      results = cursor.fetchall()
      return results
  except Exception as e:
    st.error(f"❌ خطأ أثناء استرجاع البيانات: {e}")
    return []
  finally:
    conn.close()


def get_all_projects(user_id=None):
  """استرجاع جميع مشاريع المستخدم."""
  conn = get_db_connection()
  if not conn:
    return []

  try:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
      if user_id:
        cursor.execute(
            """
                    SELECT id, client_name, summary, tech_stack, budget_range, status, created_at
                    FROM projects
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """,
            (user_id,),
        )
      else:
        cursor.execute("""
                    SELECT id, client_name, summary, tech_stack, budget_range, status, created_at
                    FROM projects
                    ORDER BY created_at DESC
                """)
      results = cursor.fetchall()
      return results
  except Exception as e:
    st.error(f"❌ خطأ أثناء جلب المشاريع: {e}")
    return []
  finally:
    conn.close()


def save_shared_link(share_id, project_id, expires_at):
  """حفظ رابط المشاركة."""
  return True


def get_shared_project(share_id):
  """استرجاع مشروع من رابط مشاركة."""
  return None


def log_user_event(user_id, event_type, event_data):
  """تسجيل حدث مستخدم."""
  return True


print("✅ تم تحميل cloudsql_utils.py المحسّن بنجاح لـ PostgreSQL")
