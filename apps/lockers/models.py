from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.members.models import Member


class Locker(models.Model):
    """الخزائن"""
    
    class Size(models.TextChoices):
        SMALL = 'small', 'صغيرة'
        MEDIUM = 'medium', 'متوسطة'
        LARGE = 'large', 'كبيرة'
    
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'متاحة'
        OCCUPIED = 'occupied', 'مشغولة'
        MAINTENANCE = 'maintenance', 'صيانة'
    
    locker_number = models.CharField('رقم الخزانة', max_length=10, unique=True)
    size = models.CharField('الحجم', max_length=10, choices=Size.choices)
    location = models.CharField('الموقع', max_length=50)
    
    daily_rate = models.DecimalField('السعر اليومي', max_digits=6, decimal_places=2)
    monthly_rate = models.DecimalField('السعر الشهري', max_digits=8, decimal_places=2)
    
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        choices=Status.choices, 
        default=Status.AVAILABLE
    )
    
    notes = models.TextField('ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'خزانة'
        verbose_name_plural = 'الخزائن'
        ordering = ['locker_number']
    
    def __str__(self):
        return f"خزانة {self.locker_number}"
    
    @property
    def current_rental(self):
        """الإيجار الحالي النشط"""
        today = timezone.now().date()
        return self.rentals.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).first()
    
    @property
    def is_available(self):
        """هل الخزانة متاحة للإيجار"""
        return self.status == self.Status.AVAILABLE and self.current_rental is None


class LockerRental(models.Model):
    """إيجار الخزائن"""
    
    class RentalType(models.TextChoices):
        DAILY = 'daily', 'يومي'
        MONTHLY = 'monthly', 'شهري'
    
    locker = models.ForeignKey(
        Locker, 
        on_delete=models.CASCADE, 
        related_name='rentals',
        verbose_name='الخزانة'
    )
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='locker_rentals',
        verbose_name='العضو'
    )
    
    rental_type = models.CharField('نوع الإيجار', max_length=10, choices=RentalType.choices)
    start_date = models.DateField('تاريخ البداية')
    end_date = models.DateField('تاريخ النهاية')
    
    price = models.DecimalField('السعر', max_digits=8, decimal_places=2)
    is_active = models.BooleanField('نشط', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'إيجار خزانة'
        verbose_name_plural = 'إيجارات الخزائن'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.locker} - {self.member}"
    
    @property
    def days_remaining(self):
        """الأيام المتبقية"""
        today = timezone.now().date()
        if today <= self.end_date:
            return (self.end_date - today).days
        return 0
    
    @property
    def is_expired(self):
        """هل انتهى الإيجار"""
        today = timezone.now().date()
        return today > self.end_date
    
    @property
    def is_expiring_soon(self):
        """هل الإيجار ينتهي قريباً (خلال 7 أيام)"""
        return 0 < self.days_remaining <= 7
    
    def auto_renew(self):
        """تجديد تلقائي للإيجار"""
        if self.rental_type == self.RentalType.MONTHLY:
            self.end_date = self.end_date + timedelta(days=30)
            self.save()
            return True
        return False
