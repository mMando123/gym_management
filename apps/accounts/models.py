from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .managers import CustomUserManager


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    
    class UserType(models.TextChoices):
        ADMIN = 'admin', 'مدير'
        STAFF = 'staff', 'موظف'
        TRAINER = 'trainer', 'مدرب'
        MEMBER = 'member', 'عضو'
    
    username = None  # نلغي username ونستخدم الهاتف
    email = models.EmailField('البريد الإلكتروني', unique=True, blank=True, null=True)
    phone = models.CharField('رقم الهاتف', max_length=15, unique=True)
    user_type = models.CharField(
        'نوع المستخدم',
        max_length=10,
        choices=UserType.choices,
        default=UserType.MEMBER
    )
    is_verified = models.BooleanField('تم التحقق', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.phone}"


class OTP(models.Model):
    """رموز التحقق"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField('الرمز', max_length=6)
    is_used = models.BooleanField('مستخدم', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    expires_at = models.DateTimeField('ينتهي في')
    
    class Meta:
        verbose_name = 'رمز تحقق'
        verbose_name_plural = 'رموز التحقق'
    
    def __str__(self):
        return f"{self.code} - {self.user.phone}"
    
    def is_expired(self):
        """التحقق من انتهاء صلاحية الرمز"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """التحقق من صحة الرمز"""
        return not self.is_used and not self.is_expired()
    
    @classmethod
    def create_otp(cls, user):
        """إنشاء رمز تحقق جديد"""
        import random
        code = ''.join(random.choices('0123456789', k=6))
        expires_at = timezone.now() + timedelta(minutes=5)
        
        # حذف الرموز القديمة
        cls.objects.filter(user=user, is_used=False).delete()
        
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
