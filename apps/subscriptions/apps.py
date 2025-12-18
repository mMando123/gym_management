from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    """تكوين تطبيق الاشتراكات"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.subscriptions'
    verbose_name = 'الاشتراكات'
    
    def ready(self):
        """استدعاء الإشارات عند تحميل التطبيق"""
        import apps.subscriptions.signals  # noqa
