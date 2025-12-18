from django.apps import AppConfig


class MembersConfig(AppConfig):
    """تكوين تطبيق الأعضاء"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.members'
    verbose_name = 'الأعضاء'
    
    def ready(self):
        """استدعاء الإشارات عند تحميل التطبيق"""
        import apps.members.signals  # noqa
