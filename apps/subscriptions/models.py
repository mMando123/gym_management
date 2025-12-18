from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from apps.members.models import Member
from apps.sports.models import Sport


class SubscriptionPlan(models.Model):
    """خطط الاشتراك"""
    
    class DurationType(models.TextChoices):
        MONTHLY = 'monthly', 'شهري'
        QUARTERLY = 'quarterly', 'ربع سنوي (3 شهور)'
        SEMI_ANNUAL = 'semi_annual', 'نصف سنوي (6 شهور)'
        ANNUAL = 'annual', 'سنوي'
    
    name = models.CharField('اسم الخطة', max_length=100)
    duration_type = models.CharField(
        'نوع المدة', 
        max_length=20, 
        choices=DurationType.choices
    )
    duration_days = models.PositiveIntegerField('عدد الأيام')
    
    # التسعير
    sports = models.ManyToManyField(
        Sport, 
        through='PlanSportPrice',
        related_name='plans',
        verbose_name='الرياضات'
    )
    
    # الخصومات
    discount_percentage = models.DecimalField(
        'نسبة الخصم %', 
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    
    # المميزات
    freeze_days_allowed = models.PositiveIntegerField('أيام التجميد المسموحة', default=0)
    guest_passes = models.PositiveIntegerField('تذاكر الضيوف', default=0)
    locker_included = models.BooleanField('خزانة مجانية', default=False)
    towel_service = models.BooleanField('خدمة المناشف', default=False)
    personal_training_sessions = models.PositiveIntegerField('حصص تدريب شخصي', default=0)
    
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'خطة اشتراك'
        verbose_name_plural = 'خطط الاشتراك'
    
    def __str__(self):
        return f"{self.name} - {self.get_duration_type_display()}"


class PlanSportPrice(models.Model):
    """أسعار الرياضات في كل خطة"""
    
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    price = models.DecimalField('السعر', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'سعر رياضة في خطة'
        verbose_name_plural = 'أسعار الرياضات في الخطط'
        unique_together = ['plan', 'sport']
    
    def __str__(self):
        return f"{self.plan.name} - {self.sport.name}: {self.price}"


class Package(models.Model):
    """الباقات المجمعة (عدة رياضات بخصم)"""
    
    name = models.CharField('اسم الباقة', max_length=100)
    description = models.TextField('الوصف', blank=True, null=True)
    sports = models.ManyToManyField(Sport, related_name='packages', verbose_name='الرياضات')
    
    # الخصم على الباقة
    discount_percentage = models.DecimalField(
        'نسبة الخصم %', 
        max_digits=5, 
        decimal_places=2
    )
    
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'باقة'
        verbose_name_plural = 'الباقات'
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """اشتراك العضو"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        ACTIVE = 'active', 'نشط'
        FROZEN = 'frozen', 'مجمد'
        EXPIRED = 'expired', 'منتهي'
        CANCELLED = 'cancelled', 'ملغي'
    
    subscription_number = models.CharField('رقم الاشتراك', max_length=30, unique=True)
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name='العضو'
    )
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.PROTECT,
        verbose_name='الخطة'
    )
    sports = models.ManyToManyField(
        Sport, 
        related_name='subscriptions',
        verbose_name='الرياضات المشترك بها'
    )
    package = models.ForeignKey(
        Package, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='الباقة'
    )
    
    # التواريخ
    start_date = models.DateField('تاريخ البداية')
    end_date = models.DateField('تاريخ الانتهاء')
    
    # التجميد
    freeze_days_used = models.PositiveIntegerField('أيام التجميد المستخدمة', default=0)
    freeze_days_remaining = models.PositiveIntegerField('أيام التجميد المتبقية', default=0)
    
    # الحالة
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    
    # الأسعار
    original_price = models.DecimalField('السعر الأصلي', max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField('قيمة الخصم', max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField('السعر النهائي', max_digits=10, decimal_places=2)
    
    # المميزات المتبقية
    guest_passes_remaining = models.PositiveIntegerField('تذاكر الضيوف المتبقية', default=0)
    pt_sessions_remaining = models.PositiveIntegerField('حصص التدريب الشخصي المتبقية', default=0)
    
    notes = models.TextField('ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'اشتراك'
        verbose_name_plural = 'الاشتراكات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.member} - {self.plan} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.subscription_number:
            self.subscription_number = self.generate_subscription_number()
        super().save(*args, **kwargs)
    
    def generate_subscription_number(self):
        """توليد رقم اشتراك فريد"""
        import datetime
        import random
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
        random_num = random.randint(100, 999)
        return f"SUB{timestamp}{random_num}"
    
    @property
    def days_remaining(self):
        """الأيام المتبقية"""
        if self.status == self.Status.ACTIVE:
            remaining = (self.end_date - timezone.now().date()).days
            return max(0, remaining)
        return 0
    
    @property
    def is_expiring_soon(self):
        """هل ينتهي قريباً (خلال 7 أيام)"""
        return 0 < self.days_remaining <= 7
    
    def activate(self):
        """تفعيل الاشتراك"""
        self.status = self.Status.ACTIVE
        self.save()
    
    def freeze(self, days):
        """تجميد الاشتراك"""
        if days <= self.freeze_days_remaining:
            self.status = self.Status.FROZEN
            self.freeze_days_used += days
            self.freeze_days_remaining -= days
            self.end_date = self.end_date + timedelta(days=days)
            self.save()
            return True
        return False
    
    def unfreeze(self):
        """إلغاء تجميد الاشتراك"""
        self.status = self.Status.ACTIVE
        self.save()


class SubscriptionFreeze(models.Model):
    """سجل تجميد الاشتراكات"""
    
    class FreezeReason(models.TextChoices):
        MEDICAL = 'medical', 'طبي'
        TRAVEL = 'travel', 'سفر'
        PERSONAL = 'personal', 'شخصي'
        OTHER = 'other', 'أخرى'
    
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE, 
        related_name='freezes',
        verbose_name='الاشتراك'
    )
    start_date = models.DateField('تاريخ بداية التجميد')
    end_date = models.DateField('تاريخ نهاية التجميد')
    days = models.PositiveIntegerField('عدد الأيام')
    reason = models.CharField('السبب', max_length=20, choices=FreezeReason.choices)
    notes = models.TextField('ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تجميد اشتراك'
        verbose_name_plural = 'تجميدات الاشتراكات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subscription} - {self.days} أيام"
