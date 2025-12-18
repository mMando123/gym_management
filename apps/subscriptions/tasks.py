from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_expired_subscriptions():
    """
    فحص الاشتراكات المنتهية الصلاحية
    يتم تشغيله يومياً الساعة 8 صباحاً
    """
    try:
        from .services import SubscriptionService
        
        result = SubscriptionService.check_expired_subscriptions()
        logger.info(f"✓ فحص الاشتراكات المنتهية: {result}")
        return result
    
    except Exception as e:
        logger.error(f"✗ خطأ في فحص الاشتراكات المنتهية: {str(e)}")
        raise


@shared_task
def unfreeze_due_subscriptions():
    """
    إلغاء تجميد الاشتراكات المستحقة
    يتم تشغيله يومياً الساعة 7 صباحاً
    """
    try:
        from .services import SubscriptionService
        
        result = SubscriptionService.unfreeze_due_subscriptions()
        logger.info(f"✓ إلغاء تجميد الاشتراكات: {result}")
        return result
    
    except Exception as e:
        logger.error(f"✗ خطأ في إلغاء تجميد الاشتراكات: {str(e)}")
        raise
