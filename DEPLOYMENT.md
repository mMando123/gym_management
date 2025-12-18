# 🚀 دليل النشر والإنتاج

## متطلبات الإنتاج

### الخوادم المطلوبة
- **Web Server**: Ubuntu 20.04+ أو Linux
- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Storage**: 50GB SSD
- **Database**: PostgreSQL 13+
- **Cache**: Redis 6+

### المتطلبات البرمجية
```bash
Python 3.10+
pip
Git
Docker & Docker Compose (اختياري)
```

---

## النشر باستخدام Docker (الطريقة الموصى بها)

### 1. إعداد الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# التحقق من التثبيت
docker --version
docker-compose --version
```

### 2. تحضير المشروع

```bash
# استنساخ المستودع
git clone <repo-url>
cd gym_management

# إنشاء متغيرات البيئة الإنتاجية
nano .env
```

```env
# Django
DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gym_production
DB_USER=gym_prod_user
DB_PASSWORD=strong-password-here
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
EMAIL_USE_TLS=True

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. تشغيل المشروع

```bash
# بناء الصور
docker-compose build

# تشغيل الخدمات
docker-compose up -d

# تطبيق الترحيلات
docker-compose exec web python manage.py migrate

# إنشاء مستخدم إداري
docker-compose exec web python manage.py createsuperuser

# جمع الملفات الثابتة
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. التحقق من الحالة

```bash
# عرض السجلات
docker-compose logs -f

# التحقق من الخدمات
docker-compose ps

# اختبار الاتصال
curl http://localhost:8000/admin/
```

---

## النشر اليدوي (بدون Docker)

### 1. إعداد الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install -y python3.10 python3-pip python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx supervisor
```

### 2. إعداد PostgreSQL

```bash
# تسجيل الدخول إلى PostgreSQL
sudo -u postgres psql

# إنشاء قاعدة البيانات
CREATE DATABASE gym_production;
CREATE USER gym_user WITH PASSWORD 'strong_password';
ALTER ROLE gym_user SET client_encoding TO 'utf8';
ALTER ROLE gym_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gym_user SET default_transaction_deferrable TO on;
ALTER ROLE gym_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gym_production TO gym_user;
\q
```

### 3. تحضير التطبيق

```bash
# إنشاء مجلد المشروع
sudo mkdir -p /var/www/gym_management
sudo chown $USER:$USER /var/www/gym_management

# استنساخ المستودع
cd /var/www/gym_management
git clone <repo-url> .

# إنشاء بيئة افتراضية
python3.10 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt

# إنشاء ملف .env
nano .env
```

### 4. تطبيق الترحيلات

```bash
# تفعيل البيئة الافتراضية
source venv/bin/activate

# تطبيق الترحيلات
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# إنشاء مستخدم إداري
python manage.py createsuperuser
```

### 5. إعداد Gunicorn

```bash
# إنشاء ملف خدمة Gunicorn
sudo nano /etc/systemd/system/gym_gunicorn.service
```

```ini
[Unit]
Description=GymPro Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gym_management
ExecStart=/var/www/gym_management/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/gym_management/gunicorn.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل الخدمة
sudo systemctl enable gym_gunicorn
sudo systemctl start gym_gunicorn
sudo systemctl status gym_gunicorn
```

### 6. إعداد Nginx

```bash
# إنشاء ملف الإعدادات
sudo nano /etc/nginx/sites-available/gym_management
```

```nginx
upstream gym_app {
    server unix:/var/www/gym_management/gunicorn.sock;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/gym_management/static/;
    }

    location /media/ {
        alias /var/www/gym_management/media/;
    }

    location / {
        proxy_pass http://gym_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/gym_management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. إعداد Celery

```bash
# إنشاء ملف خدمة Celery Worker
sudo nano /etc/systemd/system/gym_celery.service
```

```ini
[Unit]
Description=GymPro Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gym_management
Environment="PATH=/var/www/gym_management/venv/bin"
ExecStart=/var/www/gym_management/venv/bin/celery -A config worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل الخدمة
sudo systemctl enable gym_celery
sudo systemctl start gym_celery
```

### 8. إعداد Celery Beat

```bash
# إنشاء ملف خدمة Celery Beat
sudo nano /etc/systemd/system/gym_celery_beat.service
```

```ini
[Unit]
Description=GymPro Celery Beat Scheduler
After=network.target gym_celery.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gym_management
Environment="PATH=/var/www/gym_management/venv/bin"
ExecStart=/var/www/gym_management/venv/bin/celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل الخدمة
sudo systemctl enable gym_celery_beat
sudo systemctl start gym_celery_beat
```

---

## إعداد HTTPS (Let's Encrypt)

### تثبيت Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# تجديد تلقائي
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### تحديث Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... باقي الإعدادات
}

# إعادة التوجيه من HTTP إلى HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## المراقبة والصيانة

### رصد الأخطاء

```bash
# عرض السجلات
sudo journalctl -u gym_gunicorn -f
sudo journalctl -u gym_celery -f

# حفظ السجلات
sudo tail -100 /var/log/nginx/error.log
```

### النسخ الاحتياطية

```bash
# نسخ احتياطية لقاعدة البيانات
pg_dump -U gym_user gym_production > backup_$(date +%Y%m%d).sql

# استرجاع النسخة الاحتياطية
psql -U gym_user gym_production < backup_20240101.sql

# حفظ البيانات
python manage.py dumpdata > data_backup.json
```

### تحديثات الأمان

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تحديث المكتبات Python
source venv/bin/activate
pip install --upgrade -r requirements.txt
python manage.py migrate
```

---

## استكشاف الأخطاء

### الخادم لا يستجيب

```bash
# التحقق من حالة Gunicorn
sudo systemctl status gym_gunicorn
sudo journalctl -u gym_gunicorn -n 50

# إعادة تشغيل الخدمة
sudo systemctl restart gym_gunicorn
```

### مشاكل قاعدة البيانات

```bash
# التحقق من الاتصال
psql -h localhost -U gym_user -d gym_production -c "SELECT version();"

# إعادة تطبيق الترحيلات
python manage.py migrate --plan
python manage.py migrate
```

### مشاكل Celery

```bash
# التحقق من Redis
redis-cli ping

# إعادة تشغيل العمال
sudo systemctl restart gym_celery
sudo systemctl restart gym_celery_beat
```

---

## قائمة التحقق قبل الإنتاج

- [ ] تغيير `SECRET_KEY`
- [ ] تعيين `DEBUG=False`
- [ ] إعداد `ALLOWED_HOSTS`
- [ ] إعداد قاعدة بيانات الإنتاج
- [ ] تشفير HTTPS
- [ ] النسخ الاحتياطية التلقائية
- [ ] المراقبة والتنبيهات
- [ ] حدود معدل الطلب
- [ ] سياسة CORS الصحيحة
- [ ] التحقق من الأمان (OWASP Top 10)

---

## المراجع المفيدة

- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**آخر تحديث**: 2024  
**الحالة**: جاهز للإنتاج ✅
