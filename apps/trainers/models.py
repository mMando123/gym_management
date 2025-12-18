from django.db import models
from apps.accounts.models import User
from apps.members.models import Member
from apps.sports.models import Sport


class Specialization(models.Model):
    """التخصصات المتاحة للمدربين"""

    name = models.CharField('اسم التخصص', max_length=100)
    description = models.TextField('الوصف', blank=True, null=True)
    sport = models.ForeignKey(
        Sport,
        on_delete=models.SET_NULL,
        null=True,
        related_name='specializations',
        verbose_name='الرياضة'
    )

    class Meta:
        verbose_name = 'تخصص مدرب'
        verbose_name_plural = 'تخصصات المدربين'

    def __str__(self):
        return self.name


class Trainer(models.Model):
    """نموذج المدرب"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='trainer_profile',
        verbose_name='المستخدم'
    )
    trainer_id = models.CharField('رقم المدرب', max_length=20, unique=True)
    specializations = models.ManyToManyField(
        Specialization, 
        related_name='trainers',
        verbose_name='التخصصات'
    )
    bio = models.TextField('نبذة', blank=True, null=True)
    photo = models.ImageField('الصورة', upload_to='trainers/', blank=True, null=True)
    
    # المؤهلات
    certifications = models.TextField('الشهادات والمؤهلات', blank=True, null=True)
    years_of_experience = models.PositiveIntegerField('سنوات الخبرة', default=0)
    
    # التقييم
    rating = models.DecimalField(
        'التقييم', 
        max_digits=3, 
        decimal_places=2, 
        default=0.00
    )
    total_ratings = models.PositiveIntegerField('عدد التقييمات', default=0)
    
    # العمل
    hire_date = models.DateField('تاريخ التعيين')
    salary = models.DecimalField('الراتب', max_digits=10, decimal_places=2, blank=True, null=True)
    commission_percentage = models.DecimalField(
        'نسبة العمولة %', 
        max_digits=4, 
        decimal_places=2, 
        default=0
    )
    
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مدرب'
        verbose_name_plural = 'المدربون'
        ordering = ['user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.trainer_id}"
    
    def update_rating(self, new_rating):
        """تحديث التقييم"""
        total = (self.rating * self.total_ratings) + new_rating
        self.total_ratings += 1
        self.rating = total / self.total_ratings
        self.save()


class TrainerAvailability(models.Model):
    """أوقات توفر المدرب"""
    
    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, 'السبت'
        SUNDAY = 1, 'الأحد'
        MONDAY = 2, 'الاثنين'
        TUESDAY = 3, 'الثلاثاء'
        WEDNESDAY = 4, 'الأربعاء'
        THURSDAY = 5, 'الخميس'
        FRIDAY = 6, 'الجمعة'
    
    trainer = models.ForeignKey(
        Trainer, 
        on_delete=models.CASCADE, 
        related_name='availability',
        verbose_name='المدرب'
    )
    day_of_week = models.IntegerField('اليوم', choices=DayOfWeek.choices)
    start_time = models.TimeField('من الساعة')
    end_time = models.TimeField('إلى الساعة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'وقت توفر'
        verbose_name_plural = 'أوقات التوفر'
        unique_together = ['trainer', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.trainer} - {self.get_day_of_week_display()}"


class Session(models.Model):
    """جلسات التدريب الخاصة بكل مدرب"""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'مجدولة'
        COMPLETED = 'completed', 'مكتملة'
        CANCELLED = 'cancelled', 'ملغاة'

    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='session_set',
        verbose_name='المدرب'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions',
        verbose_name='العضو'
    )
    date = models.DateField('تاريخ الجلسة')
    time = models.TimeField('وقت الجلسة')
    duration = models.PositiveIntegerField('المدة (دقائق)', default=60)
    notes = models.TextField('ملاحظات', blank=True, null=True)
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'جلسة تدريب'
        verbose_name_plural = 'جلسات التدريب'
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.trainer} - {self.date} {self.time.strftime('%H:%M')}"
