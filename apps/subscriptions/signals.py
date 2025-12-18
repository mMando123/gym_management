from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Subscription

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription)
def subscription_post_save(sender, instance, created, **kwargs):
    """إشارة بعد حفظ الاشتراك"""
    
    try:
        if created:
            # 1. تفعيل الاشتراك تلقائياً
            if instance.status == 'pending':
                instance.status = 'active'
                instance.save(update_fields=['status'])
            
            # 2. إرسال إشعار باشتراك جديد
            _send_subscription_notification(instance)
            
            # 3. منح نقاط الاشتراك
            _grant_subscription_points(instance)
            
            logger.info(f"تم إنشاء اشتراك جديد: {instance.subscription_number}")
    
    except Exception as e:
        logger.error(f"خطأ في subscription_post_save: {str(e)}")


def _send_subscription_notification(subscription):
    """إرسال إشعار باشتراك جديد"""
    try:
        from apps.notifications.models import Notification
        
        sports_list = ', '.join([s.name for s in subscription.sports.all()])
        
        Notification.objects.create(
            user=subscription.member.user,
            title="اشتراك جديد ✓",
            body=f"تم تفعيل اشتراكك الجديد في {sports_list}. استمتع بالجلسات!",
            notification_type='subscription'
        )
        
        logger.info(f"تم إرسال إشعار اشتراك للعضو {subscription.member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في إرسال إشعار الاشتراك: {str(e)}")


def _grant_subscription_points(subscription):
    """منح نقاط الاشتراك"""
    try:
        from apps.rewards.services import RewardService
        
        # حساب النقاط بناءً على السعر النهائي (1 نقطة لكل 10 ريالات)
        points = int(subscription.final_price / 10)
        
        if points > 0:
            RewardService.add_points(
                member=subscription.member,
                points=points,
                transaction_type='earned',
                description=f'نقاط الاشتراك - {subscription.plan.name}'
            )
            
            logger.info(f"تم منح {points} نقطة للعضو {subscription.member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في منح نقاط الاشتراك: {str(e)}")
