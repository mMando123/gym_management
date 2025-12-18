FROM python:3.11-slim

WORKDIR /app

# تثبيت المتطلبات النظامية
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# نسخ المشروع
COPY . .

# جمع الملفات الثابتة
RUN python manage.py collectstatic --noinput

# تشغيل gunicorn بشكل افتراضي
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
