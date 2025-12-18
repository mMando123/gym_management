from django.db import models
from django.utils import timezone
from apps.sports.models import Sport
from apps.trainers.models import Trainer
from apps.members.models import Member


class ClassSchedule(models.Model):
    """جدول الحصص"""
    
    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, 'السبت'
        SUNDAY = 1, 'الأحد'
        MONDAY = 2, 'الاثنين'
        TUESDAY = 3, 'الثلاثاء'
        WEDNESDAY = 4, 'الأربعاء'
        THURSDAY = 5, 'الخميس'
        FRIDAY = 6, 'الجمعة'
    
    sport = models.ForeignKey(
        Sport, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name='الرياضة'
    )
    trainer = models.ForeignKey(
        Trainer, 
        on_delete=models.CASCADE, 
        related_name='class_schedules',
        verbose_name='المدرب'
    )
    
    name = models.CharField('اسم الحصة', max_length=100, blank=True, null=True)
    day_of_week = models.IntegerField('اليوم', choices=DayOfWeek.choices)
    start_time = models.TimeField('وقت البداية')
    end_time = models.TimeField('وقت النهاية')
    
    max_participants = models.PositiveIntegerField('الحد الأقصى للمشاركين', default=20)
    difficulty_level = models.CharField(
        'مستوى الصعوبة', 
        max_length=20,
        choices=[
            ('beginner', 'مبتدئ'),
            ('intermediate', 'متوسط'),
            ('advanced', 'متقدم'),
            ('all', 'جميع المستويات'),
        ],
        default='all'
    )
    
    room = models.CharField('القاعة', max_length=50, blank=True, null=True)
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'جدول حصة'
        verbose_name_plural = 'جداول الحصص'
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.sport.name} - {self.get_day_of_week_display()} {self.start_time}"


class ClassSession(models.Model):
    """حصة فعلية (instance من الجدول)"""
    
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'مجدولة'
        IN_PROGRESS = 'in_progress', 'جارية'
        COMPLETED = 'completed', 'منتهية'
        CANCELLED = 'cancelled', 'ملغاة'
    
    schedule = models.ForeignKey(
        ClassSchedule, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        verbose_name='الجدول'
    )
    date = models.DateField('التاريخ')
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        choices=Status.choices, 
        default=Status.SCHEDULED
    )
    
    actual_trainer = models.ForeignKey(
        Trainer, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='conducted_sessions',
        verbose_name='المدرب الفعلي'
    )
    
    participants_count = models.PositiveIntegerField('عدد المشاركين', default=0)
    notes = models.TextField('ملاحظات', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'حصة'
        verbose_name_plural = 'الحصص'
        unique_together = ['schedule', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.schedule.sport.name} - {self.date}"
    
    @property
    def available_spots(self):
        """المقاعد المتاحة"""
        return self.schedule.max_participants - self.participants_count
    
    @property
    def is_full(self):
        """هل الحصة ممتلئة"""
        return self.participants_count >= self.schedule.max_participants


class ClassBooking(models.Model):
    """حجز في حصة"""
    
    class Status(models.TextChoices):
        BOOKED = 'booked', 'محجوز'
        ATTENDED = 'attended', 'حضر'
        NO_SHOW = 'no_show', 'لم يحضر'
        CANCELLED = 'cancelled', 'ملغى'
    
    session = models.ForeignKey(
        ClassSession, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='الحصة'
    )
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='class_bookings',
        verbose_name='العضو'
    )
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        choices=Status.choices, 
        default=Status.BOOKED
    )
    
    booked_at = models.DateTimeField('وقت الحجز', auto_now_add=True)
    cancelled_at = models.DateTimeField('وقت الإلغاء', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'حجز حصة'
        verbose_name_plural = 'حجوزات الحصص'
        unique_together = ['session', 'member']
        ordering = ['-booked_at']
    
    def __str__(self):
        return f"{self.member} - {self.session}"
    
    def cancel(self):
        """إلغاء الحجز"""
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.save()
