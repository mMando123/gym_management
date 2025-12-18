# 🎯 دليل الاستخدام السريع

## 🚀 البدء في 5 دقائق

### المتطلبات الأساسية
- Python 3.10+
- PostgreSQL (أو SQLite للاختبار)
- Redis (اختياري للتطوير)

### الخطوات الأساسية

```bash
# 1. استنساخ المستودع
git clone <repo-url>
cd gym_management

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. إعداد قاعدة البيانات
python manage.py migrate

# 4. إنشاء حساب إداري
python manage.py createsuperuser

# 5. تشغيل الخادم
python manage.py runserver
```

الآن توجه إلى: `http://localhost:8000`

---

## 📚 المراجع السريعة

### الوصول إلى الأنظمة

| النظام | الرابط | المستخدم |
|-------|--------|---------|
| لوحة التحكم | `/admin/` | Admin فقط |
| API Swagger | `/api/schema/swagger/` | Authenticated |
| API ReDoc | `/api/schema/redoc/` | Authenticated |
| الرئيسية | `/` | Everyone |

### عينات الطلبات (cURL)

```bash
# تسجيل حساب جديد
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+966501234567",
    "password": "SecurePass123",
    "first_name": "أحمد",
    "last_name": "محمد",
    "email": "ahmed@example.com"
  }'

# تسجيل الدخول
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+966501234567",
    "password": "SecurePass123"
  }'

# الحصول على الملف الشخصي
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎮 سيناريوهات الاستخدام

### سيناريو 1: عضو جديد يسجل

```python
# 1. العضو يسجل حساباً جديداً
POST /api/v1/auth/register/

# 2. يتم إنشاء ملف عضو تلقائياً
# 3. يحصل على 50 نقطة ترحيب
# 4. يتلقى إشعار ترحيب

# 4. العضو يشتري اشتراكاً
POST /api/v1/subscriptions/subscriptions/

# 5. يتم إنشاء فاتورة
# 6. يتم إرسال إشعار بنجاح الاشتراك
# 7. يحصل على نقاط إضافية
```

### سيناريو 2: حضور جلسة تدريب

```python
# 1. العضو يسجل الدخول
POST /api/v1/attendance/attendance/check-in/
{
  "sport": 1  # معرف الرياضة
}

# 2. تسجيل الوقت تلقائياً
# 3. عند الانتهاء، يسجل الخروج
POST /api/v1/attendance/attendance/{id}/check-out/

# 4. يتم حساب مدة الجلسة تلقائياً
# 5. يحصل على 10 نقاط
# 6. إذا كانت الجلسة > 90 دقيقة، يحصل على 5 نقاط إضافية
```

### سيناريو 3: دفع اشتراك

```python
# 1. العضو ينقر على "دفع"
POST /api/v1/payments/payments/
{
  "invoice": 1,
  "amount": 200,
  "payment_method": "CARD"
}

# 2. يتم معالجة الدفع
# 3. إذا نجح، يتم تحديث حالة الفاتورة
# 4. يتم تفعيل الاشتراك إذا لم يكن نشطاً
# 5. يتلقى إشعار بنجاح الدفع
# 6. يحصل على نقاط (1 نقطة لكل 10 ريال)
```

---

## 🔧 الأوامر المفيدة

### استخدام Makefile

```bash
# تشغيل الخادم
make run

# إنشاء مستخدم إداري
make superuser

# تطبيق الترحيلات
make migrate

# تشغيل الاختبارات
make test

# تشغيل Celery
make celery-worker
make celery-beat

# التنسيق والفحص
make lint
make format

# تنظيف الملفات المؤقتة
make clean
```

### Django Shell Plus

```bash
python manage.py shell_plus

>>> from apps.members.models import Member
>>> members = Member.objects.all()
>>> member = members.first()
>>> member.age
34
>>> member.bmi
23.5
```

---

## 📊 البيانات التجريبية

### إنشاء بيانات اختبار

```python
# apps/members/tests/factories.py
from factory import Factory
from apps.members.models import Member
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(Factory):
    class Meta:
        model = User
    
    phone = factory.Sequence(lambda n: f"+96650{n:07d}")
    first_name = "Test"
    last_name = f"User {n}"
    email = factory.Sequence(lambda n: f"user{n}@test.com")

class MemberFactory(Factory):
    class Meta:
        model = Member
    
    user = factory.SubFactory(UserFactory)
    date_of_birth = "1990-01-01"
    gender = "M"
    height = 180
    weight = 75
```

### استخدام البيانات

```python
# إنشاء بيانات اختبار
from factories import MemberFactory

member = MemberFactory()
member.save()

# أو بكميات
members = MemberFactory.create_batch(10)
```

---

## 🔍 استكشاف الأخطاء

### مشاكل شائعة وحلولها

| المشكلة | السبب | الحل |
|--------|-------|-----|
| `ModuleNotFoundError` | مكتبة غير مثبتة | `pip install -r requirements.txt` |
| `ProgrammingError` | قاعدة بيانات غير مهيأة | `python manage.py migrate` |
| `ConnectionError` | Redis غير متصل | `redis-server` أو تخطيه للتطوير |
| `PermissionError` | حقوق ملفات | `chmod +x manage.py` |
| `CORS Error` | CORS غير مفعل | تحقق من `settings/base.py` |

### وضع Debug

```python
# settings/base.py
DEBUG = True  # للتطوير فقط

# في الكود
import pdb; pdb.set_trace()  # نقطة توقف

# أو باستخدام logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")
```

---

## 🧪 الاختبار اليدوي

### اختبار API مع Postman

1. **تسجيل حساب**
   ```
   POST http://localhost:8000/api/v1/auth/register/
   Content-Type: application/json
   
   {
     "phone": "+966501234567",
     "password": "Test@1234",
     "first_name": "أحمد",
     "last_name": "محمد"
   }
   ```

2. **تسجيل الدخول**
   ```
   POST http://localhost:8000/api/v1/auth/login/
   Content-Type: application/json
   
   {
     "phone": "+966501234567",
     "password": "Test@1234"
   }
   ```

3. **نسخ الـ Token من الاستجابة**
   ```
   "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   ```

4. **استخدام الـ Token**
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

---

## 📱 الخدمات API الرئيسية

### المصادقة
```
POST   /api/v1/auth/register/          تسجيل جديد
POST   /api/v1/auth/login/             تسجيل دخول
POST   /api/v1/auth/logout/            تسجيل خروج
GET    /api/v1/auth/profile/           الملف الشخصي
POST   /api/v1/auth/change-password/   تغيير كلمة المرور
POST   /api/v1/auth/request-otp/       طلب OTP
POST   /api/v1/auth/verify-otp/        التحقق من OTP
```

### الأعضاء
```
GET    /api/v1/members/                قائمة الأعضاء
POST   /api/v1/members/                إنشاء عضو
GET    /api/v1/members/{id}/           تفاصيل العضو
PATCH  /api/v1/members/{id}/           تحديث العضو
DELETE /api/v1/members/{id}/           حذف العضو
```

### الاشتراكات
```
GET    /api/v1/subscriptions/plans/    قائمة الخطط
POST   /api/v1/subscriptions/subscriptions/   إنشاء اشتراك
GET    /api/v1/subscriptions/subscriptions/   قائمة الاشتراكات
POST   /api/v1/subscriptions/subscriptions/{id}/freeze/     تجميد
POST   /api/v1/subscriptions/subscriptions/{id}/unfreeze/   إلغاء تجميد
```

### الحضور
```
POST   /api/v1/attendance/attendance/check-in/    تسجيل دخول
POST   /api/v1/attendance/attendance/{id}/check-out/  تسجيل خروج
GET    /api/v1/attendance/attendance/              قائمة الحضور
```

### الدفع
```
POST   /api/v1/payments/payments/          إنشاء دفعة
GET    /api/v1/payments/payments/          قائمة الدفعات
GET    /api/v1/payments/invoices/          الفواتير
GET    /api/v1/payments/installments/      الدفعات المقسطة
```

---

## 🎨 تخصيص النظام

### تعديل الألوان

```css
/* static/css/style.css */
:root {
  --primary: #007bff;      /* اللون الأساسي */
  --success: #28a745;      /* لون النجاح */
  --danger: #dc3545;       /* لون التنبيه */
  --warning: #ffc107;      /* لون التحذير */
}
```

### تعديل النصوص والرسائل

```python
# config/settings/base.py
LANGUAGE_CODE = 'ar'  # اللغة
TIME_ZONE = 'UTC'     # التوقيت

# apps/notifications/models.py
# تعديل رسائل الإشعارات
```

### تعديل الشعار والاسم

```python
# config/settings/base.py
SITE_NAME = 'GymPro'
SITE_DOMAIN = 'localhost:8000'

# templates/base.html
<!-- تعديل الشعار والعنوان -->
```

---

## 📞 الحصول على المساعدة

### الموارد المتوفرة

1. **التوثيق**
   - README.md - البدء السريع
   - DEVELOPMENT.md - للمطورين
   - API_DOCUMENTATION.md - توثيق API
   - PROJECT_SUMMARY.md - ملخص المشروع

2. **الأمثلة**
   - conftest.py - أمثلة الاختبار
   - Makefile - أوامر مفيدة
   - docker-compose.yml - للنشر

3. **المجتمع**
   - GitHub Issues - لتقارير الأخطاء
   - GitHub Discussions - للأسئلة

---

## ✅ قائمة تحقق قبل الإطلاق

- [ ] تثبيت جميع المتطلبات
- [ ] إنشاء قاعدة البيانات
- [ ] تطبيق الترحيلات
- [ ] إنشاء مستخدم إداري
- [ ] اختبار تسجيل حساب جديد
- [ ] اختبار تسجيل الدخول
- [ ] اختبار API endpoints
- [ ] التحقق من لوحة التحكم
- [ ] اختبار Celery (إذا كان مثبتاً)
- [ ] التحقق من البريد الإلكتروني (اختياري)

---

## 🎓 الخطوات التالية

بعد الإعداد الأساسي:

1. **قراءة التوثيق** - DEVELOPMENT.md
2. **استكشاف API** - استخدم Swagger UI
3. **اختبار الميزات** - جرّب جميع الوظائف
4. **تطوير ميزات جديدة** - إذا لزم الحال
5. **نشر على الإنتاج** - DEPLOYMENT.md

---

## 💡 نصائح مفيدة

```bash
# شغل مايك أمر واحد
python manage.py runserver 0.0.0.0:8000

# اختبر API بسرعة
http http://localhost:8000/api/v1/auth/profile/ \
  "Authorization: Bearer YOUR_TOKEN"

# شاهد جميع الطلبات
python manage.py shell_plus --ipython

# قم بتصدير البيانات
python manage.py dumpdata > backup.json

# استيراد البيانات
python manage.py loaddata backup.json
```

---

**Happy Coding! 🚀**

**آخر تحديث**: 2024  
**الإصدار**: 1.0.0
