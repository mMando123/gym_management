from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class NotificationTemplate(models.Model):
    """قوالب الإشعارات"""
    
    class NotificationType(models.TextChoices):
        SUBSCRIPTION_EXPIRY = 'sub_expiry', 'انتهاء اشتراك'
        PAYMENT_REMINDER = 'payment_reminder', 'تذكير بالدفع'
        WELCOME = 'welcome', 'ترحيب'
        BIRTHDAY = 'birthday', 'عيد ميلاد'
        CLASS_REMINDER = 'class_reminder', 'تذكير بحصة'
        PROMOTION = 'promotion', 'عرض'
        GENERAL = 'general', 'عام'
    
    name = models.CharField('اسم القالب', max_length=100)
    notification_type = models.CharField(
        'نوع الإشعار', 
        max_length=20, 
        choices=NotificationType.choices
    )
    
    title_template = models.CharField('عنوان الإشعار', max_length=200)
    body_template = models.TextField('نص الإشعار')
    
    # القنوات
    send_push = models.BooleanField('إشعار Push', default=True)
    send_sms = models.BooleanField('رسالة SMS', default=False)
    send_email = models.BooleanField('بريد إلكتروني', default=False)
    
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قالب إشعار'
        verbose_name_plural = 'قوالب الإشعارات'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """الإشعارات"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='المستخدم'
    )
    template = models.ForeignKey(
        NotificationTemplate, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name='القالب'
    )
    
    title = models.CharField('العنوان', max_length=200)
    body = models.TextField('النص')
    
    is_read = models.BooleanField('مقروء', default=False)
    read_at = models.DateTimeField('وقت القراءة', blank=True, null=True)
    
    # حالة الإرسال
    push_sent = models.BooleanField('تم إرسال Push', default=False)
    sms_sent = models.BooleanField('تم إرسال SMS', default=False)
    email_sent = models.BooleanField('تم إرسال Email', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.title}"
    
    def mark_as_read(self):
        """تعليم الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @property
    def send_channels(self):
        """القنوات المفعلة للإرسال"""
        channels = []
        if self.template:
            if self.template.send_push:
                channels.append('push')
            if self.template.send_sms:
                channels.append('sms')
            if self.template.send_email:
                channels.append('email')
        return channels
    
    @classmethod
    def send_notification(cls, user, template, context=None):
        """إرسال إشعار للمستخدم"""
        # استبدال المتغيرات في القالب
        title = template.title_template
        body = template.body_template
        
        if context:
            title = title.format(**context)
            body = body.format(**context)
        
        notification = cls.objects.create(
            user=user,
            template=template,
            title=title,
            body=body
        )
        
        # إرسال عبر القنوات المفعلة
        if template.send_push:
            notification.send_push_notification()
        
        if template.send_sms:
            notification.send_sms_notification()
        
        if template.send_email:
            notification.send_email_notification()
        
        return notification
    
    def send_push_notification(self):
        """إرسال إشعار push"""
        # سيتم تطبيقه مع مكتبة Firebase أو OneSignal
        self.push_sent = True
        self.save()
    
    def send_sms_notification(self):
        """إرسال رسالة SMS"""
        # سيتم تطبيقه مع مكتبة Twilio أو نحوها
        self.sms_sent = True
        self.save()
    
    def send_email_notification(self):
        """إرسال بريد إلكتروني"""
        # سيتم تطبيقه مع Django Email
        self.email_sent = True
        self.save()
