import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('gym_management')

# استرجاع جميع إعدادات Celery من Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# اكتشاف تلقائي للمهام من جميع التطبيقات المسجلة
app.autodiscover_tasks()


# إعدادات Celery Beat - المهام المجدولة
app.conf.beat_schedule = {
    # مهام الاشتراكات
    'check-expired-subscriptions': {
        'task': 'apps.subscriptions.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=8, minute=0),  # يومياً الساعة 8 صباحاً
        'options': {'queue': 'default'}
    },
    'unfreeze-due-subscriptions': {
        'task': 'apps.subscriptions.tasks.unfreeze_due_subscriptions',
        'schedule': crontab(hour=7, minute=0),  # يومياً الساعة 7 صباحاً
        'options': {'queue': 'default'}
    },
    
    # مهام المكافآت
    'check-birthday-rewards': {
        'task': 'apps.rewards.tasks.check_birthday_rewards',
        'schedule': crontab(hour=9, minute=0),  # يومياً الساعة 9 صباحاً
        'options': {'queue': 'default'}
    },
    'expire-redeemed-rewards': {
        'task': 'apps.rewards.tasks.expire_redeemed_rewards',
        'schedule': crontab(hour=10, minute=0),  # يومياً الساعة 10 صباحاً
        'options': {'queue': 'default'}
    },
    'calculate-monthly-rewards': {
        'task': 'apps.rewards.tasks.calculate_monthly_rewards',
        'schedule': crontab(day_of_month=28, hour=23, minute=0),  # يوم 28 من كل شهر الساعة 11 مساءً
        'options': {'queue': 'default'}
    },
    
    # مهام الحضور
    'auto-checkout-attendance': {
        'task': 'apps.attendance.tasks.auto_checkout_expired_attendance',
        'schedule': crontab(minute='*/15'),  # كل 15 دقيقة
        'options': {'queue': 'default'}
    },
    'send-attendance-reminders': {
        'task': 'apps.attendance.tasks.send_attendance_reminders',
        'schedule': crontab(hour=6, minute=0),  # يومياً الساعة 6 صباحاً
        'options': {'queue': 'default'}
    },
    'calculate-attendance-achievements': {
        'task': 'apps.attendance.tasks.calculate_attendance_achievements',
        'schedule': crontab(hour=23, minute=0),  # يومياً الساعة 11 مساءً
        'options': {'queue': 'default'}
    },
}

# إعدادات Celery الأساسية
app.conf.update(
    # وقت التحديث الافتراضي للمهام
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 دقيقة
    task_soft_time_limit=25 * 60,  # 25 دقيقة
    
    # إعدادات الرسائل
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@app.task(bind=True)
def debug_task(self):
    """مهمة اختبار"""
    print(f'Request: {self.request!r}')
