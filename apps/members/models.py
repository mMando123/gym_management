from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from datetime import date
from django.utils import timezone


class Member(models.Model):
    """نموذج العضو/المتدرب"""
    
    class Gender(models.TextChoices):
        MALE = 'male', 'ذكر'
        FEMALE = 'female', 'أنثى'
    
    class BloodType(models.TextChoices):
        A_POSITIVE = 'A+', 'A+'
        A_NEGATIVE = 'A-', 'A-'
        B_POSITIVE = 'B+', 'B+'
        B_NEGATIVE = 'B-', 'B-'
        O_POSITIVE = 'O+', 'O+'
        O_NEGATIVE = 'O-', 'O-'
        AB_POSITIVE = 'AB+', 'AB+'
        AB_NEGATIVE = 'AB-', 'AB-'
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='member_profile',
        verbose_name='المستخدم'
    )
    member_id = models.CharField('رقم العضوية', max_length=20, unique=True, editable=False)
    gender = models.CharField('الجنس', max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField('تاريخ الميلاد')
    national_id = models.CharField('رقم الهوية', max_length=20, blank=True, null=True)
    address = models.TextField('العنوان', blank=True, null=True)
    
    # البيانات الصحية
    height = models.DecimalField(
        'الطول (سم)', 
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    weight = models.DecimalField(
        'الوزن (كجم)', 
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    blood_type = models.CharField(
        'فصيلة الدم', 
        max_length=5, 
        choices=BloodType.choices, 
        blank=True, 
        null=True
    )
    medical_conditions = models.TextField('الحالات الصحية', blank=True, null=True)
    emergency_contact_name = models.CharField('اسم جهة الاتصال للطوارئ', max_length=100)
    emergency_contact_phone = models.CharField('رقم هاتف الطوارئ', max_length=15)
    
    # الصور
    photo = models.ImageField('الصورة الشخصية', upload_to='members/photos/', blank=True, null=True)
    
    # الحالة
    is_active = models.BooleanField('نشط', default=True)
    join_date = models.DateField('تاريخ الانضمام', auto_now_add=True)
    notes = models.TextField('ملاحظات', blank=True, null=True)
    
    # النقاط
    reward_points = models.PositiveIntegerField('نقاط المكافآت', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'عضو'
        verbose_name_plural = 'الأعضاء'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.member_id}"
    
    def save(self, *args, **kwargs):
        if not self.member_id:
            self.member_id = self.generate_member_id()
        super().save(*args, **kwargs)
    
    def generate_member_id(self):
        """توليد رقم عضوية فريد"""
        import datetime
        import random
        year = datetime.datetime.now().year
        random_num = random.randint(1000, 9999)
        return f"GYM{year}{random_num}"
    
    @property
    def age(self):
        """حساب العمر"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def bmi(self):
        """حساب مؤشر كتلة الجسم"""
        if self.height and self.weight:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 2)
        return None
    
    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def active_subscription(self):
        today = timezone.now().date()
        return self.subscriptions.filter(
            status='active',
            end_date__gte=today
        ).select_related('plan').first()

    @property
    def has_active_subscription(self):
        return bool(self.active_subscription)


class MemberBodyMetrics(models.Model):
    """سجل قياسات الجسم للعضو"""
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='body_metrics',
        verbose_name='العضو'
    )
    date = models.DateField('التاريخ', auto_now_add=True)
    weight = models.DecimalField('الوزن (كجم)', max_digits=5, decimal_places=2)
    body_fat_percentage = models.DecimalField(
        'نسبة الدهون %', 
        max_digits=4, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    muscle_mass = models.DecimalField(
        'كتلة العضلات (كجم)', 
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    chest = models.DecimalField('محيط الصدر (سم)', max_digits=5, decimal_places=2, blank=True, null=True)
    waist = models.DecimalField('محيط الخصر (سم)', max_digits=5, decimal_places=2, blank=True, null=True)
    hips = models.DecimalField('محيط الأرداف (سم)', max_digits=5, decimal_places=2, blank=True, null=True)
    arms = models.DecimalField('محيط الذراع (سم)', max_digits=5, decimal_places=2, blank=True, null=True)
    thighs = models.DecimalField('محيط الفخذ (سم)', max_digits=5, decimal_places=2, blank=True, null=True)
    notes = models.TextField('ملاحظات', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قياسات الجسم'
        verbose_name_plural = 'قياسات الجسم'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.member} - {self.date}"
