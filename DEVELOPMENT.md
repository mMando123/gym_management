# دليل التطوير - GymPro

## 🔧 إعداد بيئة التطوير

### المتطلبات
- Python 3.10+
- Git
- PostgreSQL (أو SQLite للتطوير السريع)
- Redis

### خطوات الإعداد

```bash
# 1. استنساخ المستودع
git clone <repo-url>
cd gym_management

# 2. إنشاء بيئة افتراضية
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. إنشاء ملف .env
cp .env.example .env

# 5. تطبيق الترحيلات
python manage.py migrate

# 6. إنشاء مستخدم إداري
python manage.py createsuperuser

# 7. تشغيل الخادم
python manage.py runserver
```

## 📝 معايير الكود

### تنسيق الكود
نستخدم **Black** و **Flake8**

```bash
# تنسيق الملفات
black apps/ config/

# التحقق من جودة الكود
flake8 apps/ config/
```

### معايير Python
- متوافق مع PEP 8
- اسم الوحدات والدوال باللغة الإنجليزية (snake_case)
- التعليقات والتوثيق بالعربية
- كل دالة يجب أن تحتوي على docstring

### مثال:
```python
def calculate_member_age(date_of_birth):
    """
    حساب عمر العضو من تاريخ الميلاد
    
    Args:
        date_of_birth: تاريخ الميلاد (date object)
    
    Returns:
        int: العمر بالسنوات
    """
    from datetime import date
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )
```

## 🧪 الاختبارات

### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest

# تشغيل اختبارات معينة
pytest apps/members/tests/

# مع تغطية الكود
pytest --cov=apps

# مع تقرير HTML
pytest --cov=apps --cov-report=html
```

### كتابة الاختبارات

```python
# apps/members/tests/test_models.py
import pytest
from apps.members.models import Member
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestMember:
    def test_member_creation(self, user_factory):
        """اختبار إنشاء عضو جديد"""
        user = user_factory(phone='+966501234567')
        member = Member.objects.create(
            user=user,
            date_of_birth='1990-01-01',
            gender='M'
        )
        assert member.user == user
        assert member.is_active is True
```

## 🔄 سير العمل مع Git

### إنشاء فرع جديد
```bash
git checkout -b feature/اسم-الميزة
# مثال: feature/add-member-filtering
```

### خطوات التطوير
```bash
# 1. تطوير الميزة
# 2. الالتزام بالتغييرات
git add .
git commit -m "feat: وصف الميزة"

# 3. دفع الفرع
git push origin feature/اسم-الميزة

# 4. إنشاء Pull Request
```

### أنواع الالتزامات
- `feat:` - ميزة جديدة
- `fix:` - إصلاح خطأ
- `docs:` - تحديثات التوثيق
- `style:` - تنسيق الكود
- `refactor:` - إعادة هيكلة الكود
- `test:` - إضافة/تحديث الاختبارات
- `chore:` - مهام صيانة

## 📚 هيكل المشروع

```
gym_management/
├── apps/                    # تطبيقات Django
│   ├── accounts/           # المصادقة والمستخدمون
│   ├── members/            # إدارة الأعضاء
│   ├── subscriptions/       # الاشتراكات
│   ├── payments/           # الدفع والفواتير
│   ├── attendance/         # الحضور
│   ├── trainers/           # المدربون
│   ├── sports/             # الرياضات
│   ├── schedules/          # الجداول
│   ├── rewards/            # المكافآت
│   ├── notifications/      # الإشعارات
│   ├── lockers/            # الخزائن
│   └── reports/            # التقارير
├── config/                  # إعدادات المشروع
│   ├── settings/           # ملفات الإعدادات
│   ├── celery.py          # إعدادات Celery
│   └── urls.py            # توجيه URL الرئيسي
├── static/                 # الملفات الثابتة
├── media/                  # الملفات المرفوعة
├── templates/              # قوالب HTML
└── manage.py              # سكريبت Django
```

## 🚀 تشغيل Celery

### Worker
```bash
celery -A config worker --loglevel=info --pool=solo
```

### Beat Scheduler
```bash
celery -A config beat --loglevel=info
```

### المراقبة
```bash
celery -A config events
```

## 🐛 تصحيح الأخطاء

### استخدام Django Shell
```bash
python manage.py shell_plus

>>> from apps.members.models import Member
>>> members = Member.objects.all()
>>> member = members.first()
>>> print(member.user.phone)
```

### استخدام PDB
```python
import pdb; pdb.set_trace()  # سيتوقف هنا
```

### استخدام Django Debug Toolbar
مثبت بالفعل في بيئة التطوير - يظهر على جانب الشاشة

## 📊 API Documentation

### Swagger (Swagger UI)
```
http://localhost:8000/api/schema/swagger/
```

### ReDoc
```
http://localhost:8000/api/schema/redoc/
```

### OpenAPI Schema
```
http://localhost:8000/api/schema/
```

## 🔐 الأمان

### متغيرات البيئة الحساسة
لا تخزن المفاتيح الحساسة في الكود! استخدم `.env`

```python
# ❌ خطأ
SECRET_KEY = 'my-secret-key-12345'

# ✅ صحيح
SECRET_KEY = os.getenv('SECRET_KEY')
```

### الصلاحيات
```python
from rest_framework.permissions import BasePermission

class IsTrainer(BasePermission):
    """السماح فقط للمدربين"""
    
    def has_permission(self, request, view):
        return request.user and request.user.role == 'TRAINER'
```

## 💾 قاعدة البيانات

### إنشاء ترحيل جديد
```bash
python manage.py makemigrations apps/members

# إذا كان لديك اسم محدد
python manage.py makemigrations apps/members --name add_field_description
```

### تطبيق الترحيلات
```bash
python manage.py migrate

# ترحيل معين
python manage.py migrate apps.members 0002_auto
```

### استرجاع البيانات
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > db_backup.json
```

### استيراد البيانات
```bash
python manage.py loaddata db_backup.json
```

## 🎯 أفضل الممارسات

### Models
- استخدم `related_name` في ForeignKey
- أضف `Meta.verbose_name_plural`
- استخدم `__str__` للتمثيل النصي

### Views
- استخدم Serializers للتحقق من البيانات
- طبق الصلاحيات المناسبة
- أضف `queryset` و `serializer_class` في ViewSets

### Serializers
- استخدم `read_only_fields` للحقول المحسوبة
- تحقق من البيانات في `validate_*` methods
- أضف `Meta.extra_kwargs` للتحقق الإضافي

## 📧 البريد الإلكتروني

في بيئة التطوير، البريد يُطبع على الكونسول:

```python
# في بيئة الإنتاج، استخدم:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
USE_TLS = True
```

## 🎓 الموارد المفيدة

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Pytest Django](https://pytest-django.readthedocs.io/)

---

**آخر تحديث**: 2024  
**التطوير**: فريق GymPro
