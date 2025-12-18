from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Member

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Member)
def member_pre_save(sender, instance, **kwargs):
    """إشارة قبل حفظ العضو - للتحقق من التغييرات"""
    
    try:
        # التحقق من وجود عضو سابق
        if instance.pk:
            old_member = Member.objects.get(pk=instance.pk)
            
            # تتبع التغييرات الهامة
            if old_member.is_active != instance.is_active:
                if not instance.is_active:
                    # تسجيل إلغاء تفعيل العضو
                    logger.info(f"عضو {instance.member_id} تم تعطيله")
    
    except Member.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"خطأ في member_pre_save: {str(e)}")


@receiver(post_save, sender=Member)
def member_post_save(sender, instance, created, **kwargs):
    """إشارة بعد حفظ العضو - للإشعارات والنقاط"""
    
    try:
        if created:
            # 1. إرسال إشعار ترحيب
            _send_welcome_notification(instance)
            
            # 2. منح نقاط الترحيب
            _grant_welcome_points(instance)
            
            # 3. تسجيل إنشاء العضو
            logger.info(f"تم إنشاء عضو جديد: {instance.member_id}")
        
        else:
            # تفعيل العضو
            _handle_member_activation(instance)
    
    except Exception as e:
        logger.error(f"خطأ في member_post_save: {str(e)}")


def _send_welcome_notification(member):
    """إرسال إشعار ترحيب للعضو الجديد"""
    try:
        from apps.notifications.models import Notification
        from apps.notifications.services import NotificationService
        
        # إنشاء إشعار الترحيب
        notification = Notification.objects.create(
            user=member.user,
            title="مرحباً بك في GymPro! 🎉",
            body="تم إنشاء حسابك بنجاح. استمتع برحلة اللياقة معنا!",
            notification_type='welcome'
        )
        
        logger.info(f"تم إرسال إشعار ترحيب للعضو {member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في إرسال إشعار الترحيب: {str(e)}")


def _grant_welcome_points(member):
    """منح نقاط الترحيب للعضو الجديد"""
    try:
        from apps.rewards.services import RewardService
        
        # منح 50 نقطة ترحيب
        RewardService.add_points(
            member=member,
            points=50,
            transaction_type='earned',
            description='نقاط الترحيب - مرحباً بك! 🎉'
        )
        
        logger.info(f"تم منح نقاط الترحيب للعضو {member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في منح نقاط الترحيب: {str(e)}")


def _handle_member_activation(instance):
    """معالجة تفعيل/تعطيل العضو"""
    try:
        # الحصول على النسخة السابقة
        old_member = Member.objects.get(pk=instance.pk)
        
        # إذا كان تم تفعيل العضو
        if not old_member.is_active and instance.is_active:
            from apps.notifications.models import Notification
            
            Notification.objects.create(
                user=instance.user,
                title="تم تفعيل حسابك ✓",
                body="حسابك تم تفعيله بنجاح. يمكنك الآن الوصول لجميع الخدمات!",
                notification_type='activation'
            )
            
            logger.info(f"تم تفعيل العضو {instance.member_id}")
        
        # إذا كان تم تعطيل العضو
        elif old_member.is_active and not instance.is_active:
            from apps.notifications.models import Notification
            
            Notification.objects.create(
                user=instance.user,
                title="تم تعطيل حسابك",
                body="تم تعطيل حسابك. يرجى التواصل مع الإدارة للمزيد من المعلومات.",
                notification_type='deactivation'
            )
            
            logger.info(f"تم تعطيل العضو {instance.member_id}")
    
    except Member.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"خطأ في معالجة تفعيل العضو: {str(e)}")


# تسجيل الإشارات
def ready(self):
    """دالة الاستعداد عند تحميل التطبيق"""
    import apps.members.signals
