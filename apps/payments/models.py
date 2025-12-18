from django.db import models
from apps.members.models import Member
from apps.subscriptions.models import Subscription
from apps.accounts.models import User


class Payment(models.Model):
    """المدفوعات"""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        CARD = 'card', 'بطاقة'
        BANK_TRANSFER = 'bank_transfer', 'تحويل بنكي'
        ONLINE = 'online', 'إلكتروني'
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        COMPLETED = 'completed', 'مكتمل'
        FAILED = 'failed', 'فشل'
        REFUNDED = 'refunded', 'مسترد'
        PARTIAL = 'partial', 'جزئي'
    
    class PaymentType(models.TextChoices):
        SUBSCRIPTION = 'subscription', 'اشتراك'
        RENEWAL = 'renewal', 'تجديد'
        UPGRADE = 'upgrade', 'ترقية'
        PERSONAL_TRAINING = 'pt', 'تدريب شخصي'
        PRODUCT = 'product', 'منتج'
        LOCKER = 'locker', 'خزانة'
        OTHER = 'other', 'أخرى'
    
    payment_number = models.CharField('رقم العملية', max_length=30, unique=True)
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name='العضو'
    )
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payments',
        verbose_name='الاشتراك'
    )
    
    payment_type = models.CharField('نوع الدفع', max_length=20, choices=PaymentType.choices)
    payment_method = models.CharField('طريقة الدفع', max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    
    amount = models.DecimalField('المبلغ', max_digits=10, decimal_places=2)
    discount = models.DecimalField('الخصم', max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField('الضريبة', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('الإجمالي', max_digits=10, decimal_places=2)
    
    # للدفع الجزئي
    amount_paid = models.DecimalField('المبلغ المدفوع', max_digits=10, decimal_places=2, default=0)
    amount_remaining = models.DecimalField('المبلغ المتبقي', max_digits=10, decimal_places=2, default=0)
    
    # تفاصيل إضافية
    transaction_id = models.CharField('رقم المعاملة', max_length=100, blank=True, null=True)
    receipt_number = models.CharField('رقم الإيصال', max_length=50, blank=True, null=True)
    
    notes = models.TextField('ملاحظات', blank=True, null=True)
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='processed_payments',
        verbose_name='بواسطة'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'المدفوعات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_number} - {self.member} - {self.total}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        self.amount_remaining = self.total - self.amount_paid
        super().save(*args, **kwargs)
    
    def generate_payment_number(self):
        """توليد رقم دفعة فريد"""
        import datetime
        import random
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_num = random.randint(100, 999)
        return f"PAY{timestamp}{random_num}"
    
    @property
    def is_fully_paid(self):
        """هل تم دفع الكل"""
        return self.amount_paid >= self.total
    
    @property
    def payment_percentage(self):
        """نسبة الدفع"""
        if self.total > 0:
            return round((self.amount_paid / self.total) * 100, 2)
        return 0


class Invoice(models.Model):
    """الفواتير"""
    
    invoice_number = models.CharField('رقم الفاتورة', max_length=30, unique=True)
    payment = models.OneToOneField(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='invoice',
        verbose_name='الدفعة'
    )
    
    issued_date = models.DateField('تاريخ الإصدار', auto_now_add=True)
    due_date = models.DateField('تاريخ الاستحقاق', blank=True, null=True)
    
    subtotal = models.DecimalField('المجموع الفرعي', max_digits=10, decimal_places=2)
    discount = models.DecimalField('الخصم', max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField('الضريبة', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('الإجمالي', max_digits=10, decimal_places=2)
    
    is_paid = models.BooleanField('مدفوعة', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"فاتورة {self.invoice_number}"


class Installment(models.Model):
    """أقساط الدفع"""
    
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='installments',
        verbose_name='الدفعة'
    )
    installment_number = models.PositiveIntegerField('رقم القسط')
    amount = models.DecimalField('المبلغ', max_digits=10, decimal_places=2)
    due_date = models.DateField('تاريخ الاستحقاق')
    paid_date = models.DateField('تاريخ الدفع', blank=True, null=True)
    is_paid = models.BooleanField('مدفوع', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قسط'
        verbose_name_plural = 'الأقساط'
        ordering = ['payment', 'installment_number']
        unique_together = ['payment', 'installment_number']
    
    def __str__(self):
        return f"قسط {self.installment_number} - {self.payment}"


class InstallmentPlan(models.Model):
    """خطط التقسيط"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الإنشاء'
        ACTIVE = 'active', 'نشط'
        COMPLETED = 'completed', 'مكتمل'

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        verbose_name='العضو'
    )
    total_amount = models.DecimalField('إجمالي القيمة', max_digits=10, decimal_places=2)
    installment_count = models.PositiveIntegerField('عدد الأقساط')
    start_date = models.DateField('تاريخ البداية')
    notes = models.TextField('ملاحظات', blank=True, null=True)
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'خطة التقسيط'
        verbose_name_plural = 'خطط التقسيط'
        ordering = ['-created_at']

    def __str__(self):
        return f"خطة {self.member.user.get_full_name()} - {self.total_amount}"
