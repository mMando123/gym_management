from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    """تكوين تطبيق الحضور"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attendance'
    verbose_name = 'الحضور'
    
    def ready(self):
        """استدعاء الإشارات عند تحميل التطبيق"""
        import apps.attendance.signals  # noqa
