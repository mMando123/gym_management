from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """تكوين تطبيق المدفوعات"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'المدفوعات'
    
    def ready(self):
        """استدعاء الإشارات عند تحميل التطبيق"""
        import apps.payments.signals  # noqa
