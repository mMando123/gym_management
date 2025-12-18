# 🚀 دليل البدء السريع - GymPro

## الخطوة 1: استنساخ المشروع
```bash
git clone <repository-url>
cd gym_management
```

## الخطوة 2: إنشاء البيئة الافتراضية
```bash
# على Windows
python -m venv venv
venv\Scripts\activate

# على Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## الخطوة 3: تثبيت المتطلبات
```bash
pip install -r requirements/development.txt
```

## الخطوة 4: إعداد البيئة
```bash
# نسخ ملف البيئة
cp .env.example .env

# تعديل .env بإضافة قيمك الخاصة
# أهم شيء: SECRET_KEY و قاعدة البيانات
```

## الخطوة 5: إعداد قاعدة البيانات

### باستخدام SQLite (للتطوير السريع):
```bash
# فقط شغّل الترحيلات
python manage.py migrate
```

### باستخدام PostgreSQL (موصى به):
```bash
# تأكد من تثبيت PostgreSQL
# ثم قم بتشغيل:
docker-compose up -d db redis

# انتظر قليلاً حتى تشتغل الخدمات
python manage.py migrate
```

## الخطوة 6: إنشاء حساب إداري
```bash
python manage.py createsuperuser
# اتبع التعليمات لإنشاء حساب admin
```

## الخطوة 7: تحميل البيانات الأولية (اختياري)
```bash
python manage.py loaddata initial_data
```

## الخطوة 8: تشغيل خادم التطوير
```bash
python manage.py runserver
```

## ✅ الآن يمكنك الوصول إلى:
- 🌐 الموقع: http://localhost:8000
- 🔐 لوحة الإدارة: http://localhost:8000/admin

---

## 🐳 باستخدام Docker (موصى به):

```bash
# ابن الصور
docker-compose build

# شغل الخدمات
docker-compose up

# في terminal آخر، طبق الترحيلات
docker-compose exec web python manage.py migrate

# أنشئ حساب admin
docker-compose exec web python manage.py createsuperuser

# الآن يمكنك الوصول إلى:
# 🌐 http://localhost:8000
# 📊 Flower: http://localhost:5555 (مراقب Celery)
```

---

## 📁 هيكل المشروع المهم:

```
gym_management/
├── config/settings/       # إعدادات حسب البيئة
├── apps/                  # تطبيقات Django
├── static/               # CSS, JS, صور
├── templates/            # قوالب HTML
├── manage.py             # أداة إدارة Django
└── .env                  # ملف البيئة (لا تشارك!)
```

---

## 🔧 أوامر مفيدة:

```bash
# تطبيق الترحيلات
python manage.py migrate

# إنشاء ترحيلات جديدة
python manage.py makemigrations

# تشغيل السيرفر
python manage.py runserver

# تشغيل اختبارات
python manage.py test

# تنظيف قاعدة البيانات
python manage.py flush

# إنشاء نسخة احتياطية
python manage.py dumpdata > backup.json

# استعادة نسخة احتياطية
python manage.py loaddata backup.json
```

---

## 🔑 معلومات الوصول الافتراضية:

| العنصر | القيمة |
|--------|--------|
| **URL** | http://localhost:8000 |
| **Admin Panel** | http://localhost:8000/admin |
| **اسم المستخدم** | admin |
| **كلمة المرور** | (التي أنشأتها) |

---

## ⚠️ المشاكل الشائعة وحلولها:

### المشكلة: "ModuleNotFoundError: No module named 'django'"
**الحل:** تأكد من تفعيل البيئة الافتراضية:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### المشكلة: "No module named 'psycopg2'"
**الحل:** إذا كنت تستخدم PostgreSQL:
```bash
pip install psycopg2-binary
```

### المشكلة: قاعدة البيانات لا تعمل
**الحل:** 
```bash
# حذف ملف قاعدة البيانات القديم
rm db.sqlite3

# أعد الترحيلات
python manage.py migrate

# أنشئ حساب admin جديد
python manage.py createsuperuser
```

### المشكلة: الصفحة تظهر بدون تنسيق
**الحل:**
```bash
# اجمع الملفات الثابتة
python manage.py collectstatic --noinput
```

---

## 📚 المراجع المفيدة:

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap RTL](https://getbootstrap.com/)
- [Chart.js Docs](https://www.chartjs.org/)
- [DataTables](https://datatables.net/)

---

## 💡 نصائح للتطوير:

1. **استخدم Django Debug Toolbar للتطوير:**
   ```bash
   pip install django-debug-toolbar
   ```

2. **استخدم Black لتنسيق الكود:**
   ```bash
   pip install black
   black .
   ```

3. **تحقق من جودة الكود مع Flake8:**
   ```bash
   pip install flake8
   flake8 apps/
   ```

4. **استخدم Pre-commit Hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

---

## 🎯 الخطوات التالية:

بعد أن تشتغل البيئة بنجاح:

1. تطوير نماذج البيانات (Models)
2. إنشاء Admin Interfaces
3. بناء REST API
4. إضافة المنطق التجاري
5. الاختبارات الشاملة
6. النشر والتطوير المستمر

---

## 📞 هل تحتاج مساعدة؟

- 📧 البريد: support@gym.sa
- 📱 الهاتف: +966501234567
- 💬 Chat: [رابط الدعم]

---

**تم تحديثه:** ديسمبر 2025  
**النسخة:** 1.0.0
