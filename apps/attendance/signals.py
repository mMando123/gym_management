from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Attendance

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Attendance)
def attendance_post_save(sender, instance, created, **kwargs):
    """إشارة بعد حفظ سجل الحضور"""
    
    try:
        if created:
            # 1. منح نقاط الحضور
            _grant_attendance_points(instance)
            
            # 2. تحديث إحصائيات العضو
            _update_member_stats(instance)
            
            logger.info(f"تم تسجيل حضور جديد: {instance.member.member_id}")
        
        else:
            # معالجة تسجيل الخروج
            _handle_checkout(instance)
    
    except Exception as e:
        logger.error(f"خطأ في attendance_post_save: {str(e)}")


def _grant_attendance_points(attendance):
    """منح نقاط الحضور"""
    try:
        from apps.rewards.services import RewardService
        
        # منح 10 نقاط لكل حضور
        RewardService.add_points(
            member=attendance.member,
            points=10,
            transaction_type='earned',
            description=f'نقاط حضور - {attendance.sport.name}'
        )
        
        logger.info(f"تم منح 10 نقاط حضور للعضو {attendance.member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في منح نقاط الحضور: {str(e)}")


def _update_member_stats(attendance):
    """تحديث إحصائيات العضو"""
    try:
        # حساب عدد الزيارات هذا الشهر
        from django.utils import timezone
        from .models import Attendance
        
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_visits = Attendance.objects.filter(
            member=attendance.member,
            check_in__gte=month_start
        ).count()
        
        # إذا كان عدد الزيارات = 10، منح مكافأة
        if this_month_visits == 10:
            from apps.rewards.services import RewardService
            
            RewardService.add_points(
                member=attendance.member,
                points=50,
                transaction_type='earned',
                description='مكافأة 10 حضور هذا الشهر!'
            )
            
            logger.info(f"تم منح مكافأة 10 حضور للعضو {attendance.member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في تحديث إحصائيات العضو: {str(e)}")


def _handle_checkout(attendance):
    """معالجة تسجيل الخروج"""
    try:
        # الحصول على النسخة السابقة
        old_attendance = Attendance.objects.get(pk=attendance.pk)
        
        # إذا تم تسجيل الخروج الآن
        if not old_attendance.check_out and attendance.check_out:
            duration = attendance.duration_minutes
            
            if duration and duration > 90:
                # منح نقطة إضافية للجلسات الطويلة (أكثر من 90 دقيقة)
                from apps.rewards.services import RewardService
                
                RewardService.add_points(
                    member=attendance.member,
                    points=5,
                    transaction_type='earned',
                    description=f'مكافأة جلسة طويلة ({duration} دقيقة)'
                )
                
                logger.info(f"تم منح نقاط جلسة طويلة للعضو {attendance.member.member_id}")
    
    except Attendance.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"خطأ في معالجة الخروج: {str(e)}")
