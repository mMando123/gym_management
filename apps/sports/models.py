from django.db import models


class SportCategory(models.Model):
    """تصنيفات الألعاب"""
    
    name = models.CharField('اسم التصنيف', max_length=100)
    description = models.TextField('الوصف', blank=True, null=True)
    icon = models.CharField('الأيقونة', max_length=50, blank=True, null=True)
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تصنيف رياضة'
        verbose_name_plural = 'تصنيفات الرياضات'
    
    def __str__(self):
        return self.name


class Sport(models.Model):
    """نموذج الرياضة/اللعبة"""
    
    category = models.ForeignKey(
        SportCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sports',
        verbose_name='التصنيف'
    )
    name = models.CharField('اسم الرياضة', max_length=100)
    slug = models.SlugField('الرابط', unique=True, allow_unicode=True)
    description = models.TextField('الوصف', blank=True, null=True)
    image = models.ImageField('الصورة', upload_to='sports/', blank=True, null=True)
    
    # تفاصيل
    max_members_per_session = models.PositiveIntegerField('الحد الأقصى للمتدربين في الحصة', default=20)
    session_duration_minutes = models.PositiveIntegerField('مدة الحصة (دقيقة)', default=60)
    
    # التسعير
    has_belt_system = models.BooleanField('نظام الأحزمة', default=False)  # للكاراتيه مثلاً
    requires_equipment = models.BooleanField('يتطلب معدات', default=False)
    
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'رياضة'
        verbose_name_plural = 'الرياضات'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Belt(models.Model):
    """نظام الأحزمة (للكاراتيه وغيرها)"""
    
    sport = models.ForeignKey(
        Sport, 
        on_delete=models.CASCADE, 
        related_name='belts',
        verbose_name='الرياضة'
    )
    name = models.CharField('اسم الحزام', max_length=50)
    color = models.CharField('اللون', max_length=20)
    order = models.PositiveIntegerField('الترتيب')
    requirements = models.TextField('المتطلبات', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'حزام'
        verbose_name_plural = 'الأحزمة'
        ordering = ['sport', 'order']
        unique_together = ['sport', 'order']
    
    def __str__(self):
        return f"{self.sport.name} - {self.name}"
