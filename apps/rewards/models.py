from django.db import models
from django.utils import timezone
from apps.members.models import Member


class RewardRule(models.Model):
    """قواعد كسب النقاط"""
    
    class ActionType(models.TextChoices):
        ATTENDANCE = 'attendance', 'حضور تدريب'
        REFERRAL = 'referral', 'إحالة صديق'
        RENEWAL = 'renewal', 'تجديد اشتراك'
        EARLY_RENEWAL = 'early_renewal', 'تجديد مبكر'
        MILESTONE = 'milestone', 'إنجاز'
        REVIEW = 'review', 'تقييم'
        BIRTHDAY = 'birthday', 'عيد ميلاد'
    
    name = models.CharField('اسم القاعدة', max_length=100)
    action_type = models.CharField('نوع الإجراء', max_length=20, choices=ActionType.choices)
    points = models.PositiveIntegerField('النقاط')
    description = models.TextField('الوصف', blank=True, null=True)
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قاعدة مكافأة'
        verbose_name_plural = 'قواعد المكافآت'
        ordering = ['action_type']
    
    def __str__(self):
        return f"{self.name} - {self.points} نقطة"


class PointTransaction(models.Model):
    """سجل النقاط"""
    
    class TransactionType(models.TextChoices):
        EARNED = 'earned', 'كسب'
        REDEEMED = 'redeemed', 'استبدال'
        EXPIRED = 'expired', 'انتهاء'
        ADJUSTED = 'adjusted', 'تعديل'
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='point_transactions',
        verbose_name='العضو'
    )
    transaction_type = models.CharField('نوع العملية', max_length=20, choices=TransactionType.choices)
    points = models.IntegerField('النقاط')  # موجب للكسب، سالب للاستبدال
    balance_after = models.PositiveIntegerField('الرصيد بعد العملية')
    
    rule = models.ForeignKey(
        RewardRule, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='القاعدة'
    )
    description = models.TextField('الوصف')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'حركة نقاط'
        verbose_name_plural = 'حركات النقاط'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.member} - {self.points} ({self.transaction_type})"


class Reward(models.Model):
    """المكافآت القابلة للاستبدال"""
    
    name = models.CharField('اسم المكافأة', max_length=100)
    description = models.TextField('الوصف', blank=True, null=True)
    image = models.ImageField('الصورة', upload_to='rewards/', blank=True, null=True)
    points_required = models.PositiveIntegerField('النقاط المطلوبة')
    quantity_available = models.PositiveIntegerField('الكمية المتاحة', blank=True, null=True)
    
    is_active = models.BooleanField('نشط', default=True)
    valid_from = models.DateField('صالح من', blank=True, null=True)
    valid_until = models.DateField('صالح حتى', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مكافأة'
        verbose_name_plural = 'المكافآت'
        ordering = ['points_required']
    
    def __str__(self):
        return f"{self.name} - {self.points_required} نقطة"
    
    @property
    def is_available(self):
        """هل المكافأة متاحة للاستبدال"""
        if not self.is_active:
            return False
        
        today = timezone.now().date()
        
        if self.valid_from and today < self.valid_from:
            return False
        
        if self.valid_until and today > self.valid_until:
            return False
        
        if self.quantity_available is not None and self.quantity_available <= 0:
            return False
        
        return True


class RewardRedemption(models.Model):
    """استبدال المكافآت"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        APPROVED = 'approved', 'موافق عليه'
        DELIVERED = 'delivered', 'تم التسليم'
        REJECTED = 'rejected', 'مرفوض'
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='reward_redemptions',
        verbose_name='العضو'
    )
    reward = models.ForeignKey(
        Reward, 
        on_delete=models.PROTECT,
        verbose_name='المكافأة'
    )
    points_used = models.PositiveIntegerField('النقاط المستخدمة')
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    
    redeemed_at = models.DateTimeField('وقت الاستبدال', auto_now_add=True)
    delivered_at = models.DateTimeField('وقت التسليم', blank=True, null=True)
    notes = models.TextField('ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'استبدال مكافأة'
        verbose_name_plural = 'استبدالات المكافآت'
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"{self.member} - {self.reward}"
    
    def approve(self):
        """الموافقة على الاستبدال"""
        self.status = self.Status.APPROVED
        self.save()
    
    def deliver(self):
        """تسليم المكافأة"""
        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.save()
    
    def reject(self):
        """رفض الاستبدال"""
        self.status = self.Status.REJECTED
        self.save()
