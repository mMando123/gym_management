from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count, Avg, Q
from datetime import timedelta
from django.utils import timezone

from .models import Trainer, TrainerAvailability


class TrainerAvailabilityInline(admin.TabularInline):
    """أوقات التوفر والجدول الأسبوعي (جدول مدمج)"""
    
    model = TrainerAvailability
    extra = 0
    fields = ['day_of_week', 'start_time', 'end_time']
    ordering = ['day_of_week', 'start_time']


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    """لوحة إدارة المدربين والمتدربين"""
    
    list_display = [
        'trainer_id', 'get_full_name', 'get_phone_display',
        'get_specializations_badge', 'get_rating_stars',
        'get_experience_badge', 'get_active_status',
        'photo_thumbnail'
    ]
    list_filter = [
        'is_active', 'specializations', 'hire_date',
        ('created_at', admin.DateFieldListFilter)
    ]
    search_fields = [
        'trainer_id', 'user__phone', 'user__first_name',
        'user__last_name', 'user__email', 'certifications'
    ]
    filter_horizontal = ['specializations']
    readonly_fields = [
        'rating', 'total_ratings', 'photo_preview_large',
        'created_at', 'updated_at', 'get_trainer_stats',
        'get_salary_info'
    ]
    ordering = ['-hire_date']
    date_hierarchy = 'hire_date'
    
    inlines = [TrainerAvailabilityInline]
    
    fieldsets = (
        (_('معلومات المدرب'), {
            'fields': ('user', 'trainer_id', 'photo', 'photo_preview_large')
        }),
        (_('التخصصات والخبرة'), {
            'fields': (
                'specializations', 'years_of_experience',
                'certifications', 'bio'
            ),
            'description': 'المؤهلات والخبرات المهنية'
        }),
        (_('التقييمات والأداء'), {
            'fields': ('rating', 'total_ratings', 'get_trainer_stats'),
            'classes': ('collapse',)
        }),
        (_('معلومات التوظيف'), {
            'fields': ('hire_date', 'is_active'),
            'description': 'تاريخ التوظيف والحالة'
        }),
        (_('الراتب والعمولة'), {
            'fields': ('salary', 'commission_percentage', 'get_salary_info'),
            'description': 'بيانات الراتب والعمولة'
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """الاسم الكامل للمدرب"""
        full_name = obj.user.get_full_name()
        return full_name if full_name else obj.user.phone
    get_full_name.short_description = _('الاسم')
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_phone_display(self, obj):
        """رقم الهاتف"""
        return obj.user.phone
    get_phone_display.short_description = _('الهاتف')
    get_phone_display.admin_order_field = 'user__phone'
    
    def get_specializations_badge(self, obj):
        """شارات التخصصات"""
        specializations = obj.specializations.all()
        if not specializations:
            return '—'
        
        if specializations.count() == 1:
            return format_html(
                '<span style="background-color: #0d6efd; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">{}</span>',
                specializations.first().name
            )
        
        # عرض عدد التخصصات
        return format_html(
            '<span style="background-color: #0d6efd; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold; cursor: pointer;" title="{}">'
            '{} تخصصات</span>',
            ', '.join([s.name for s in specializations]),
            specializations.count()
        )
    get_specializations_badge.short_description = _('التخصصات')
    
    def get_rating_stars(self, obj):
        """عرض التقييم بنجوم"""
        if obj.rating == 0:
            stars = '☆☆☆☆☆'
            color = '#6c757d'
        elif obj.rating <= 2:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            color = '#dc3545'
        elif obj.rating <= 3:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            color = '#ffc107'
        else:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            color = '#198754'
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{}</span><br/>'
            '<small>({:.1f}/5 - {} تقييم)</small>',
            color, stars, obj.rating, obj.total_ratings
        )
    get_rating_stars.short_description = _('التقييم')
    get_rating_stars.admin_order_field = 'rating'
    
    def get_experience_badge(self, obj):
        """شارة الخبرة"""
        if obj.years_of_experience >= 5:
            color = '#198754'
            label = 'خبرة عالية'
        elif obj.years_of_experience >= 3:
            color = '#0dcaf0'
            label = 'خبرة متوسطة'
        elif obj.years_of_experience >= 1:
            color = '#0d6efd'
            label = 'خبرة جديد'
        else:
            color = '#6c757d'
            label = 'خبرة ضئيلة'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{} ({} سنة)</span>',
            color, label, obj.years_of_experience
        )
    get_experience_badge.short_description = _('الخبرة')
    
    def get_active_status(self, obj):
        """حالة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">🟢 نشط</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">🔴 معطل</span>'
        )
    get_active_status.short_description = _('الحالة')
    
    def photo_thumbnail(self, obj):
        """معاينة صغيرة للصورة"""
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return '—'
    photo_thumbnail.short_description = _('الصورة')
    
    def photo_preview_large(self, obj):
        """معاينة كبيرة للصورة"""
        if obj.photo:
            return format_html(
                '<img src="{}" width="200" height="200" '
                'style="border-radius: 10px; object-fit: cover; margin: 10px 0;" />',
                obj.photo.url
            )
        return format_html('<em>لا توجد صورة</em>')
    photo_preview_large.short_description = _('معاينة الصورة')
    
    def get_trainer_stats(self, obj):
        """إحصائيات المدرب"""
        # عدد الجلسات
        sessions = obj.classchedule_set.count()
        
        # عدد الأعضاء المتدربين
        members = obj.attendance_set.values('member').distinct().count()
        
        # متوسط التقييم
        avg_rating = obj.rating or 0
        
        return format_html(
            '<strong>الجلسات:</strong> {}<br/>'
            '<strong>الأعضاء:</strong> {}<br/>'
            '<strong>التقييم:</strong> {:.1f}/5',
            sessions, members, avg_rating
        )
    get_trainer_stats.short_description = _('الإحصائيات')
    
    def get_salary_info(self, obj):
        """معلومات الراتب والعمولة"""
        commission_amount = (obj.salary * obj.commission_percentage / 100) if obj.commission_percentage else 0
        total_income = obj.salary + commission_amount
        
        return format_html(
            '<strong>الراتب الأساسي:</strong> {} ر.س<br/>'
            '<strong>العمولة:</strong> {}% ({} ر.س)<br/>'
            '<strong>الإجمالي:</strong> {} ر.س',
            obj.salary, obj.commission_percentage, commission_amount, total_income
        )
    get_salary_info.short_description = _('الراتب والعمولة')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'user'
        ).prefetch_related('specializations')
    
    actions = [
        'activate_trainers', 'deactivate_trainers',
        'export_trainers_csv'
    ]
    
    @admin.action(description=_('✓ تفعيل المدربين'))
    def activate_trainers(self, request, queryset):
        """إجراء: تفعيل المدربين"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'✓ تم تفعيل {count} مدرب')
    
    @admin.action(description=_('✗ تعطيل المدربين'))
    def deactivate_trainers(self, request, queryset):
        """إجراء: تعطيل المدربين"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'✗ تم تعطيل {count} مدرب')
    
    @admin.action(description=_('📥 تصدير إلى CSV'))
    def export_trainers_csv(self, request, queryset):
        """إجراء: تصدير المدربين إلى CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="trainers.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'معرف المدرب', 'الاسم', 'الهاتف', 'البريد الإلكتروني',
            'التخصصات', 'التقييم', 'الخبرة', 'الراتب', 'العمولة', 'الحالة'
        ])
        
        for trainer in queryset:
            specializations = ', '.join([s.name for s in trainer.specializations.all()])
            
            writer.writerow([
                trainer.trainer_id,
                trainer.user.get_full_name(),
                trainer.user.phone,
                trainer.user.email,
                specializations,
                trainer.rating,
                trainer.years_of_experience,
                trainer.salary,
                trainer.commission_percentage,
                'نشط' if trainer.is_active else 'معطل'
            ])
        
        return response
    export_trainers_csv.short_description = _('تصدير إلى CSV')


@admin.register(TrainerAvailability)
class TrainerAvailabilityAdmin(admin.ModelAdmin):
    """لوحة إدارة أوقات توفر المدربين"""
    
    list_display = [
        'trainer_name', 'get_day_badge', 'get_time_range',
        'created_at'
    ]
    list_filter = [
        'day_of_week',
        ('trainer', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'trainer__trainer_id', 'trainer__user__phone',
        'trainer__user__first_name'
    ]
    readonly_fields = ['created_at']
    ordering = ['trainer', 'day_of_week', 'start_time']
    
    fieldsets = (
        (_('معلومات المدرب'), {
            'fields': ('trainer',)
        }),
        (_('الجدول الأسبوعي'), {
            'fields': ('day_of_week', 'start_time', 'end_time')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def trainer_name(self, obj):
        """اسم المدرب"""
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #6c757d;">{}</small>',
            obj.trainer.user.get_full_name(),
            obj.trainer.trainer_id
        )
    trainer_name.short_description = _('المدرب')
    trainer_name.admin_order_field = 'trainer__user__first_name'
    
    def get_day_badge(self, obj):
        """شارة يوم الأسبوع"""
        days_labels = {
            0: 'الإثنين',
            1: 'الثلاثاء',
            2: 'الأربعاء',
            3: 'الخميس',
            4: 'الجمعة',
            5: 'السبت',
            6: 'الأحد'
        }
        
        colors = [
            '#0d6efd', '#0dcaf0', '#198754', '#ffc107',
            '#fd7e14', '#dc3545', '#6f42c1'
        ]
        
        label = days_labels.get(obj.day_of_week, '—')
        color = colors[obj.day_of_week]
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{}</span>',
            color, label
        )
    get_day_badge.short_description = _('اليوم')
    
    def get_time_range(self, obj):
        """نطاق الوقت"""
        return format_html(
            '<strong>{}</strong> - <strong>{}</strong>',
            obj.start_time.strftime('%H:%M'),
            obj.end_time.strftime('%H:%M')
        )
    get_time_range.short_description = _('الوقت')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related('trainer__user')
    
    actions = []
