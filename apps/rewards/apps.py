from django.apps import AppConfig


class RewardsConfig(AppConfig):
    """تكوين تطبيق المكافآت والنقاط"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rewards'
    verbose_name = 'المكافآت والنقاط'
    
    def ready(self):
        """استدعاء الإشارات عند تحميل التطبيق"""
        import apps.rewards.signals  # noqa
