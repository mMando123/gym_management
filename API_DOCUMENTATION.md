# 📖 توثيق API - GymPro

## المصادقة

### تسجيل حساب جديد
```
POST /api/v1/auth/register/
Content-Type: application/json

{
  "phone": "+966501234567",
  "first_name": "أحمد",
  "last_name": "محمد",
  "email": "ahmed@example.com",
  "password": "SecurePassword123"
}

Response 201:
{
  "user": {
    "id": 1,
    "phone": "+966501234567",
    "first_name": "أحمد",
    "last_name": "محمد",
    "email": "ahmed@example.com",
    "role": "MEMBER"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### تسجيل الدخول
```
POST /api/v1/auth/login/
Content-Type: application/json

{
  "phone": "+966501234567",
  "password": "SecurePassword123"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### طلب OTP
```
POST /api/v1/auth/request-otp/
Content-Type: application/json

{
  "phone": "+966501234567"
}

Response 200:
{
  "message": "تم إرسال رمز OTP إلى الهاتف",
  "expires_in": 600
}
```

### التحقق من OTP
```
POST /api/v1/auth/verify-otp/
Content-Type: application/json

{
  "phone": "+966501234567",
  "otp": "123456"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### الملف الشخصي
```
GET /api/v1/auth/profile/
Authorization: Bearer <access-token>

Response 200:
{
  "id": 1,
  "phone": "+966501234567",
  "first_name": "أحمد",
  "last_name": "محمد",
  "email": "ahmed@example.com",
  "role": "MEMBER",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### تغيير كلمة المرور
```
POST /api/v1/auth/change-password/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "old_password": "OldPassword123",
  "new_password": "NewPassword123"
}

Response 200:
{
  "message": "تم تغيير كلمة المرور بنجاح"
}
```

### تسجيل الخروج
```
POST /api/v1/auth/logout/
Authorization: Bearer <access-token>

Response 200:
{
  "message": "تم تسجيل الخروج بنجاح"
}
```

---

## إدارة الأعضاء

### قائمة الأعضاء
```
GET /api/v1/members/
Authorization: Bearer <access-token>

Query Parameters:
- page: رقم الصفحة (افتراضي: 1)
- page_size: عدد النتائج (افتراضي: 10)
- search: البحث بالاسم أو الهاتف
- gender: النوع (M/F)
- status: الحالة (ACTIVE/INACTIVE)
- min_age: الحد الأدنى للعمر
- max_age: الحد الأقصى للعمر

Response 200:
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/members/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "phone": "+966501234567",
        "first_name": "أحمد"
      },
      "date_of_birth": "1990-01-01",
      "gender": "M",
      "age": 34,
      "height": 180,
      "weight": 75,
      "is_active": true,
      "joined_at": "2024-01-01"
    }
  ]
}
```

### تفاصيل العضو
```
GET /api/v1/members/{id}/
Authorization: Bearer <access-token>

Response 200:
{
  "id": 1,
  "user": {...},
  "date_of_birth": "1990-01-01",
  "gender": "M",
  "age": 34,
  "height": 180,
  "weight": 75,
  "bmi": 23.1,
  "address": "123 Main Street",
  "is_active": true,
  "joined_at": "2024-01-01",
  "body_metrics": [...]
}
```

### تحديث ملف العضو
```
PATCH /api/v1/members/{id}/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "height": 182,
  "weight": 77,
  "address": "456 New Street"
}

Response 200: تفاصيل العضو المحدثة
```

---

## الاشتراكات

### قائمة الخطط
```
GET /api/v1/subscriptions/plans/
Authorization: Bearer <access-token>

Response 200:
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "الخطة الذهبية",
      "price": 200.0,
      "duration_days": 30,
      "description": "خطة شاملة",
      "features": [
        "وصول غير محدود",
        "استشارة مجانية"
      ]
    }
  ]
}
```

### إنشاء اشتراك
```
POST /api/v1/subscriptions/subscriptions/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "plan": 1,
  "package": 2,
  "start_date": "2024-01-01"
}

Response 201:
{
  "id": 1,
  "member": 1,
  "plan": {...},
  "status": "ACTIVE",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "remaining_days": 30
}
```

### تجميد الاشتراك
```
POST /api/v1/subscriptions/subscriptions/{id}/freeze/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "reason": "إجازة"
}

Response 200:
{
  "id": 1,
  "status": "FROZEN",
  "freeze_date": "2024-01-15",
  "freeze_period_days": 7
}
```

### إلغاء تجميد الاشتراك
```
POST /api/v1/subscriptions/subscriptions/{id}/unfreeze/
Authorization: Bearer <access-token>

Response 200:
{
  "id": 1,
  "status": "ACTIVE",
  "end_date": "2024-02-07"
}
```

---

## المدفوعات

### قائمة الدفعات
```
GET /api/v1/payments/payments/
Authorization: Bearer <access-token>

Query Parameters:
- status: حالة الدفع (COMPLETED/PENDING/FAILED)
- payment_method: طريقة الدفع (CARD/BANK_TRANSFER/CASH)

Response 200:
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "amount": 200.0,
      "currency": "SAR",
      "status": "COMPLETED",
      "payment_method": "CARD",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### الفواتير
```
GET /api/v1/payments/invoices/
Authorization: Bearer <access-token>

Response 200:
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "invoice_number": "INV-2024-001",
      "total_amount": 200.0,
      "paid_amount": 200.0,
      "remaining_amount": 0.0,
      "status": "PAID",
      "due_date": "2024-01-31"
    }
  ]
}
```

### الدفعات المقسطة
```
GET /api/v1/payments/installments/
Authorization: Bearer <access-token>

Response 200:
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "invoice": 1,
      "amount": 50.0,
      "due_date": "2024-02-01",
      "status": "PENDING",
      "days_until_due": 31
    }
  ]
}
```

---

## الحضور

### تسجيل الدخول
```
POST /api/v1/attendance/attendance/check-in/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "sport": 1
}

Response 201:
{
  "id": 1,
  "member": 1,
  "sport": 1,
  "check_in": "2024-01-15T10:00:00Z",
  "status": "CHECKED_IN"
}
```

### تسجيل الخروج
```
POST /api/v1/attendance/attendance/{id}/check-out/
Authorization: Bearer <access-token>

Response 200:
{
  "id": 1,
  "check_out": "2024-01-15T11:30:00Z",
  "duration_minutes": 90,
  "status": "COMPLETED"
}
```

### سجل الحضور
```
GET /api/v1/attendance/attendance/
Authorization: Bearer <access-token>

Query Parameters:
- date_from: تاريخ البداية
- date_to: تاريخ النهاية
- sport: معرف الرياضة

Response 200:
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "member": 1,
      "sport": "الجري",
      "check_in": "2024-01-15T10:00:00Z",
      "check_out": "2024-01-15T11:30:00Z",
      "duration_minutes": 90
    }
  ]
}
```

---

## المكافآت والنقاط

### رصيد النقاط
```
GET /api/v1/rewards/rewards/
Authorization: Bearer <access-token>

Response 200:
{
  "member": 1,
  "total_points": 1500,
  "available_points": 1200,
  "redeemed_points": 300,
  "transactions": [
    {
      "id": 1,
      "points": 100,
      "action": "ATTENDANCE",
      "description": "حضور جلسة تدريب",
      "created_at": "2024-01-15"
    }
  ]
}
```

### المكافآت المتاحة
```
GET /api/v1/rewards/redemptions/
Authorization: Bearer <access-token>

Response 200:
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "شراب مجاني",
      "points_required": 50,
      "quantity_available": 10,
      "description": "شراب بروتين مجاني"
    }
  ]
}
```

### استبدال مكافأة
```
POST /api/v1/rewards/redemptions/{id}/redeem/
Authorization: Bearer <access-token>

Response 201:
{
  "id": 1,
  "reward": 1,
  "status": "REDEEMED",
  "redeemed_at": "2024-01-15T10:00:00Z",
  "expiry_date": "2024-02-15"
}
```

---

## رموز الأخطاء

| الرمز | المعنى | الحل |
|------|--------|------|
| 400 | Bad Request | تحقق من صحة البيانات المرسلة |
| 401 | Unauthorized | أعد تسجيل الدخول أو تحديث الرمز |
| 403 | Forbidden | ليس لديك صلاحيات كافية |
| 404 | Not Found | المورد غير موجود |
| 429 | Too Many Requests | انتظر قبل محاولة مجددًا |
| 500 | Server Error | تواصل مع الدعم الفني |

---

## معلومات مفيدة

### Headers المطلوبة
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

### صيغ التواريخ
```
ISO 8601: 2024-01-15T10:30:00Z
```

### Pagination
```
GET /api/v1/members/?page=1&page_size=20
```

---

**آخر تحديث**: 2024  
**الإصدار**: 1.0.0
