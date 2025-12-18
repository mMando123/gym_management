from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Payment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """إشارة بعد حفظ الدفعة"""
    
    try:
        if created:
            # 1. إرسال إشعار بالدفعة
            _send_payment_notification(instance)
            
            logger.info(f"تم تسجيل دفعة جديدة: {instance.payment_number}")
        
        else:
            # معالجة تغييرات الحالة
            _handle_payment_status_change(instance)
    
    except Exception as e:
        logger.error(f"خطأ في payment_post_save: {str(e)}")


def _send_payment_notification(payment):
    """إرسال إشعار بالدفعة"""
    try:
        from apps.notifications.models import Notification
        
        status_labels = {
            'completed': 'تم استقبالها',
            'pending': 'قيد الانتظار',
            'partial': 'تم استقبال جزء منها',
            'failed': 'فشلت',
            'refunded': 'تم استسترجاعها'
        }
        
        status_label = status_labels.get(payment.status, 'مسجلة')
        
        Notification.objects.create(
            user=payment.member.user,
            title=f"دفعة {status_label} ✓",
            body=f"تم تسجيل دفعة بقيمة {payment.total} ر.س ({payment.get_payment_type_display()})",
            notification_type='payment'
        )
        
        logger.info(f"تم إرسال إشعار دفعة للعضو {payment.member.member_id}")
    
    except Exception as e:
        logger.error(f"خطأ في إرسال إشعار الدفعة: {str(e)}")


def _handle_payment_status_change(payment):
    """معالجة تغيير حالة الدفعة"""
    try:
        from apps.notifications.models import Notification
        
        # الحصول على النسخة السابقة
        old_payment = Payment.objects.get(pk=payment.pk)
        
        # إذا تغيرت الحالة
        if old_payment.status != payment.status:
            status_messages = {
                'completed': ('تم استقبال الدفعة ✓', 'تم استقبال دفعتك بنجاح'),
                'failed': ('فشلت الدفعة ✗', 'فشل معالجة دفعتك. يرجى المحاولة مرة أخرى'),
                'refunded': ('تم استسترجاع المبلغ', 'تم استسترجاع مبلغ الدفعة إلى حسابك'),
            }
            
            if payment.status in status_messages:
                title, body = status_messages[payment.status]
                
                Notification.objects.create(
                    user=payment.member.user,
                    title=title,
                    body=body,
                    notification_type='payment_status'
                )
                
                logger.info(f"تم إرسال إشعار تغيير حالة دفعة للعضو {payment.member.member_id}")
    
    except Payment.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"خطأ في معالجة تغيير حالة الدفعة: {str(e)}")
