from django.db import models
from apps.members.models import Member
from apps.subscriptions.models import Subscription
from apps.sports.models import Sport
from apps.trainers.models import Trainer


class Attendance(models.Model):
    """سجل الحضور"""
    
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        verbose_name='العضو'
    )
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        verbose_name='الاشتراك'
    )
    sport = models.ForeignKey(
        Sport, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        verbose_name='الرياضة'
    )
    trainer = models.ForeignKey(
        Trainer, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='member_attendances',
        verbose_name='المدرب'
    )
    
    check_in = models.DateTimeField('وقت الدخول')
    check_out = models.DateTimeField('وقت الخروج', blank=True, null=True)
    
    # تسجيل تلقائي أم يدوي
    is_manual_entry = models.BooleanField('تسجيل يدوي', default=False)
    
    notes = models.TextField('ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'حضور'
        verbose_name_plural = 'سجل الحضور'
        ordering = ['-check_in']
    
    def __str__(self):
        return f"{self.member} - {self.sport} - {self.check_in.date()}"
    
    @property
    def duration_minutes(self):
        """مدة التدريب بالدقائق"""
        if self.check_out:
            delta = self.check_out - self.check_in
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def is_checked_out(self):
        """هل تم تسجيل الخروج"""
        return self.check_out is not None


class GuestVisit(models.Model):
    """زيارات الضيوف"""
    
    host_member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='guest_visits',
        verbose_name='العضو المضيف'
    )
    guest_name = models.CharField('اسم الضيف', max_length=100)
    guest_phone = models.CharField('هاتف الضيف', max_length=15)
    
    visit_date = models.DateField('تاريخ الزيارة')
    check_in = models.DateTimeField('وقت الدخول')
    check_out = models.DateTimeField('وقت الخروج', blank=True, null=True)
    
    notes = models.TextField('ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'زيارة ضيف'
        verbose_name_plural = 'زيارات الضيوف'
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"ضيف {self.guest_name} مع {self.host_member}"
    
    @property
    def duration_minutes(self):
        """مدة الزيارة بالدقائق"""
        if self.check_out:
            delta = self.check_out - self.check_in
            return int(delta.total_seconds() / 60)
        return None
