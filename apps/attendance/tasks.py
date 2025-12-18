from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def auto_checkout_expired_attendance():
    """
    تسجيل الخروج التلقائي للجلسات المنتهية
    يتم تشغيله كل 15 دقيقة
    """
    try:
        from .models import Attendance
        
        now = timezone.now()
        # الجلسات التي انتهت منذ أكثر من 30 دقيقة ولم يتم تسجيل خروج
        expired_sessions = Attendance.objects.filter(
            check_out__isnull=True,
            check_in__lt=now - timedelta(minutes=30)
        )
        
        count = 0
        for attendance in expired_sessions:
            # تسجيل الخروج التلقائي
            duration_minutes = (now - attendance.check_in).total_seconds() / 60
            
            attendance.check_out = now
            attendance.duration_minutes = int(duration_minutes)
            attendance.save(update_fields=['check_out', 'duration_minutes'])
            count += 1
        
        logger.info(f"✓ تسجيل الخروج التلقائي: {count} جلسة")
        return f"تم تسجيل الخروج لـ {count} جلسة"
    
    except Exception as e:
        logger.error(f"✗ خطأ في التسجيل التلقائي: {str(e)}")
        raise


@shared_task
def send_attendance_reminders():
    """
    إرسال تذكيرات الحضور للأعضاء غير النشطين
    يتم تشغيله يومياً الساعة 6 صباحاً
    """
    try:
        from apps.members.models import Member
        from apps.notifications.models import Notification
        from datetime import timedelta
        
        # الأعضاء الذين لم يحضروا لمدة أسبوع
        week_ago = timezone.now() - timedelta(days=7)
        inactive_members = Member.objects.filter(
            is_active=True,
            attendance__isnull=True
        ) | Member.objects.filter(
            is_active=True,
            attendance__date__lt=week_ago.date()
        ).distinct()
        
        count = 0
        for member in inactive_members:
            Notification.objects.create(
                user=member.user,
                type='REMINDER',
                title='تذكير: حان وقت الرياضة!',
                message='لم نرك منذ فترة... نشتاق لك في الجيم! 💪',
                link='/attendance/'
            )
            count += 1
        
        logger.info(f"✓ تذكيرات الحضور: {count} عضو")
        return f"تم إرسال تذكيرات لـ {count} عضو"
    
    except Exception as e:
        logger.error(f"✗ خطأ في إرسال التذكيرات: {str(e)}")
        raise


@shared_task
def calculate_attendance_achievements():
    """
    حساب الإنجازات بناءً على سجل الحضور
    يتم تشغيله كل يوم الساعة 11 مساءً
    """
    try:
        from apps.members.models import Member
        from apps.notifications.models import Notification
        from django.db.models import Count
        from datetime import timedelta
        
        month_ago = timezone.now() - timedelta(days=30)
        
        # الأعضاء بـ 10 جلسات في الشهر
        active_this_month = Member.objects.annotate(
            month_attendance=Count(
                'attendance',
                filter=models.Q(attendance__date__gte=month_ago)
            )
        ).filter(month_attendance__gte=10)
        
        count = 0
        for member in active_this_month:
            Notification.objects.create(
                user=member.user,
                type='ACHIEVEMENT',
                title='🏆 إنجاز: نشيط جداً!',
                message=f'أنت من أكثر الأعضاء نشاطاً! لديك {member.month_attendance} جلسة هذا الشهر.',
                link='/achievements/'
            )
            count += 1
        
        logger.info(f"✓ حساب الإنجازات: {count} عضو")
        return f"تم حساب الإنجازات لـ {count} عضو"
    
    except Exception as e:
        logger.error(f"✗ خطأ في حساب الإنجازات: {str(e)}")
        raise
