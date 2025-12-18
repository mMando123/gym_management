from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """تخصيص لوحة إدارة المستخدمين"""
    
    list_display = [
        'phone', 'get_full_name_display', 'get_user_type_badge',
        'get_verification_status', 'get_active_status', 'created_at'
    ]
    list_filter = [
        'user_type', 'is_verified', 'is_active', 'is_staff',
        'created_at', 'last_login'
    ]
    search_fields = ['phone', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('بيانات المستخدم'), {
            'fields': ('phone', 'password')
        }),
        (_('المعلومات الشخصية'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('نوع المستخدم والصلاحيات'), {
            'fields': ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        (_('المجموعات والصلاحيات التفصيلية'), {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('last_login', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (_('معلومات المستخدم الجديد'), {
            'classes': ('wide',),
            'fields': (
                'phone', 'first_name', 'last_name', 'email',
                'password1', 'password2', 'user_type'
            ),
            'description': 'أدخل رقم الهاتف وكلمة المرور لإنشاء مستخدم جديد'
        }),
    )
    
    readonly_fields = ['created_at', 'last_login', 'get_member_link']
    
    def get_full_name_display(self, obj):
        """اسم المستخدم الكامل أو الهاتف"""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.phone
    get_full_name_display.short_description = 'الاسم'
    
    def get_user_type_badge(self, obj):
        """شارة نوع المستخدم"""
        colors = {
            'admin': '#dc3545',      # أحمر
            'staff': '#fd7e14',      # برتقالي
            'trainer': '#0dcaf0',    # سماوي
            'member': '#198754'      # أخضر
        }
        color = colors.get(obj.user_type, '#6c757d')
        labels = {
            'admin': 'مسؤول',
            'staff': 'موظف',
            'trainer': 'مدرب',
            'member': 'عضو'
        }
        label = labels.get(obj.user_type, obj.user_type)
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    get_user_type_badge.short_description = 'نوع المستخدم'
    
    def get_verification_status(self, obj):
        """حالة التحقق"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ موثق</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ غير موثق</span>'
        )
    get_verification_status.short_description = 'التحقق'
    
    def get_active_status(self, obj):
        """حالة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">🟢 نشط</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">🔴 معطل</span>'
        )
    get_active_status.short_description = 'الحالة'
    
    def get_member_link(self, obj):
        """رابط إلى ملف العضو إن وجد"""
        if hasattr(obj, 'member_profile'):
            member = obj.member_profile
            url = reverse('admin:members_member_change', args=[member.id])
            return format_html(
                '<a href="{}" target="_blank">عرض ملف العضو</a>',
                url
            )
        return 'لا يوجد ملف عضو'
    get_member_link.short_description = 'ملف العضو'
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        qs = super().get_queryset(request)
        return qs.select_related('member_profile')
    
    actions = ['make_verified', 'make_unverified', 'deactivate_users']
    
    def make_verified(self, request, queryset):
        """إجراء: تحديد كمستخدمين موثقين"""
        count = queryset.update(is_verified=True)
        self.message_user(request, f'تم توثيق {count} مستخدم')
    make_verified.short_description = 'توثيق المستخدمين المختارين'
    
    def make_unverified(self, request, queryset):
        """إجراء: إلغاء التوثيق"""
        count = queryset.update(is_verified=False)
        self.message_user(request, f'تم إلغاء توثيق {count} مستخدم')
    make_unverified.short_description = 'إلغاء توثيق المستخدمين المختارين'
    
    def deactivate_users(self, request, queryset):
        """إجراء: تعطيل المستخدمين"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {count} مستخدم')
    deactivate_users.short_description = 'تعطيل المستخدمين المختارين'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """لوحة إدارة رموز التحقق (OTP)"""
    
    list_display = [
        'user_phone', 'code', 'get_status_badge',
        'get_expiry_status', 'created_at', 'expires_at'
    ]
    list_filter = [
        'is_used', 'created_at',
        ('expires_at', admin.RelatedFieldListFilter)
    ]
    search_fields = ['user__phone', 'code']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('معلومات OTP'), {
            'fields': ('user', 'code', 'is_used')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'expires_at', 'get_time_remaining'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'code', 'created_at', 'expires_at', 'user',
        'get_time_remaining'
    ]
    
    def user_phone(self, obj):
        """رقم هاتف المستخدم"""
        return obj.user.phone
    user_phone.short_description = 'الهاتف'
    
    def get_status_badge(self, obj):
        """شارة حالة الاستخدام"""
        if obj.is_used:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 10px; border-radius: 3px;">مستخدم</span>'
            )
        return format_html(
            '<span style="background-color: #198754; color: white; '
            'padding: 3px 10px; border-radius: 3px;">جديد</span>'
        )
    get_status_badge.short_description = 'الحالة'
    
    def get_expiry_status(self, obj):
        """حالة انتهاء الصلاحية"""
        if obj.is_expired():
            return format_html(
                '<span style="color: red; font-weight: bold;">منتهي الصلاحية</span>'
            )
        
        remaining = obj.expires_at - timezone.now()
        minutes = int(remaining.total_seconds() / 60)
        
        if minutes < 2:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} دقيقة</span>',
                minutes
            )
        
        return format_html(
            '<span style="color: green; font-weight: bold;">صحيح</span>'
        )
    get_expiry_status.short_description = 'الصلاحية'
    
    def get_time_remaining(self, obj):
        """الوقت المتبقي"""
        if obj.is_expired():
            return format_html(
                '<span style="color: red;">انتهت الصلاحية</span>'
            )
        
        remaining = obj.expires_at - timezone.now()
        minutes = int(remaining.total_seconds() / 60)
        seconds = int(remaining.total_seconds() % 60)
        
        return format_html(
            '<span style="font-weight: bold;">{} دقيقة و {} ثانية</span>',
            minutes, seconds
        )
    get_time_remaining.short_description = 'الوقت المتبقي'
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related('user')
    
    actions = ['mark_as_used', 'delete_expired']
    
    def mark_as_used(self, request, queryset):
        """إجراء: تحديد كمستخدمة"""
        count = queryset.update(is_used=True)
        self.message_user(request, f'تم تحديد {count} كود كمستخدم')
    mark_as_used.short_description = 'تحديد الأكواد كمستخدمة'
    
    def delete_expired(self, request, queryset):
        """إجراء: حذف الأكواد منتهية الصلاحية"""
        expired = queryset.filter(
            expires_at__lt=timezone.now()
        )
        count = expired.count()
        expired.delete()
        self.message_user(request, f'تم حذف {count} كود منتهي الصلاحية')
    delete_expired.short_description = 'حذف الأكواد منتهية الصلاحية'
    
    def has_add_permission(self, request):
        """منع إضافة OTP يدويّة (تُنشأ تلقائياً فقط)"""
        return False
