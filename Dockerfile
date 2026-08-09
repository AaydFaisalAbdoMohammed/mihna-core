FROM python:3.11-slim

# منع بَفرة مخرجات السجلات لرؤيتها فوراً في Cloud Run Logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# تثبيت الحزم وحذف الكاش في نفس الطبقة لتصغير حجم الحاوية
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات أولاً للاستفادة من Docker Layer Caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي أكواد المشروع
COPY . .

EXPOSE 8080

# تعطيل إرسال إحصائيات Streamlit ومنع طلب البريد عند التشغيل
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
