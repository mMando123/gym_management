from celery import shared_task
from datetime import date, timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_birthday_rewards():
    """
    التحقق من أعياد الميلاد ومنح المكافآت
    يتم تشغيله يومياً الساعة 9 صباحاً
    """
    try:
        from apps.members.models import Member
        from apps.notifications.models import Notification
        from .models import PointTransaction
        
        today = date.today()
        members = Member.objects.filter(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day,
            is_active=True
        )
        
        count = 0
        for member in members:
            # منح 100 نقطة مكافأة عيد ميلاد
            PointTransaction.objects.create(
                member=member,
                points=100,
                action='BIRTHDAY',
                description='مكافأة عيد الميلاد السنوية 🎉'
            )
            
            # إرسال إشعار
            Notification.objects.create(
                user=member.user,
                type='REWARD',
                title='عيد ميلاد سعيد!',
                message='تم منحك 100 نقطة مكافأة كهدية عيد ميلادك. استمتع بخصومات إضافية! 🎁',
                link=f'/rewards/'
            )
            count += 1
        
        logger.info(f"✓ منح مكافآت أعياد الميلاد: {count} عضو")
        return f"تم منح المكافآت لـ {count} عضو"
    
    except Exception as e:
        logger.error(f"✗ خطأ في منح مكافآت أعياد الميلاد: {str(e)}")
        raise


@shared_task
def expire_redeemed_rewards():
    """
    انتهاء صلاحية المكافآت المستردة
    يتم تشغيله يومياً الساعة 10 صباحاً
    """
    try:
        from .models import RewardRedemption
        
        today = date.today()
        expired = RewardRedemption.objects.filter(
            status='REDEEMED',
            expiry_date__lt=today
        ).update(status='EXPIRED')
        
        logger.info(f"✓ انتهاء صلاحية المكافآت المستردة: {expired} مكافأة")
        return f"انتهت صلاحية {expired} مكافأة"
    
    except Exception as e:
        logger.error(f"✗ خطأ في انتهاء الصلاحية: {str(e)}")
        raise


@shared_task
def calculate_monthly_rewards():
    """
    حساب المكافآت الشهرية بناءً على الأنشطة
    يتم تشغيله آخر يوم من الشهر الساعة 11 مساءً
    """
    try:
        from apps.members.models import Member
        from apps.attendance.models import Attendance
        from .models import PointTransaction
        from django.db.models import Count
        
        last_month = timezone.now().date().replace(day=1) - timedelta(days=1)
        
        # أعضاء أكثر انتظاماً (20+ جلسة)
        active_members = Attendance.objects.filter(
            date__month=last_month.month,
            date__year=last_month.year
        ).values('member').annotate(count=Count('id')).filter(count__gte=20)
        
        count = 0
        for attendance in active_members:
            member = Member.objects.get(id=attendance['member'])
            PointTransaction.objects.create(
                member=member,
                points=50,
                action='MONTHLY_ACTIVITY',
                description=f'مكافأة النشاط الشهري - {attendance["count"]} جلسة'
            )
            count += 1
        
        logger.info(f"✓ حساب المكافآت الشهرية: {count} عضو")
        return f"تم حساب المكافآت لـ {count} عضو"
    
    except Exception as e:
        logger.error(f"✗ خطأ في حساب المكافآت الشهرية: {str(e)}")
        raise
