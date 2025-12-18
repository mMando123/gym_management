from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django.utils import timezone

from .models import (
    SubscriptionPlan,
    PlanSportPrice,
    Package,
    Subscription,
    SubscriptionFreeze
)


class PlanSportPriceInline(admin.TabularInline):
    """أسعار الرياضات ضمن الخطة (جدول مدمج)"""
    
    model = PlanSportPrice
    extra = 1
    fields = ['sport', 'price']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['sport']
        return []


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """لوحة إدارة خطط الاشتراك"""
    
    list_display = [
        'name', 'get_duration_badge', 'get_discount_badge',
        'freeze_days_allowed', 'get_features_count', 'is_active_badge'
    ]
    list_filter = ['duration_type', 'is_active', 'created_at']
    search_fields = ['name']
    ordering = ['duration_days']
    
    inlines = [PlanSportPriceInline]
    
    fieldsets = (
        (_('معلومات الخطة'), {
            'fields': ('name', 'duration_type', 'duration_days', 'is_active')
        }),
        (_('التسعير والخصومات'), {
            'fields': ('discount_percentage',)
        }),
        (_('المميزات والفوائد'), {
            'fields': (
                'freeze_days_allowed', 'guest_passes', 'locker_included',
                'towel_service', 'personal_training_sessions'
            ),
            'description': 'المميزات المتضمنة في هذه الخطة'
        }),
    )
    
    def get_duration_badge(self, obj):
        """شارة المدة"""
        duration_labels = {
            'monthly': 'شهري',
            'quarterly': 'ربع سنوي',
            'semi_annual': 'نصف سنوي',
            'annual': 'سنوي'
        }
        
        colors = {
            'monthly': '#0d6efd',
            'quarterly': '#198754',
            'semi_annual': '#0dcaf0',
            'annual': '#fd7e14'
        }
        
        label = duration_labels.get(obj.duration_type, obj.duration_type)
        color = colors.get(obj.duration_type, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{} ({} أيام)</span>',
            color, label, obj.duration_days
        )
    get_duration_badge.short_description = _('المدة')
    
    def get_discount_badge(self, obj):
        """شارة الخصم"""
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">خصم {}%</span>',
                obj.discount_percentage
            )
        return '—'
    get_discount_badge.short_description = _('الخصم')
    
    def get_features_count(self, obj):
        """عدد المميزات"""
        count = 0
        if obj.guest_passes: count += 1
        if obj.locker_included: count += 1
        if obj.towel_service: count += 1
        if obj.personal_training_sessions: count += 1
        
        return format_html(
            '<span style="font-weight: bold; color: #0d6efd;">{} مميزة</span>',
            count
        )
    get_features_count.short_description = _('المميزات')
    
    def is_active_badge(self, obj):
        """شارة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ نشط</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ معطل</span>'
        )
    is_active_badge.short_description = _('الحالة')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).prefetch_related('plan_sport_prices')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    """لوحة إدارة الباقات المتعددة الرياضات"""
    
    list_display = [
        'name', 'get_sports_list', 'get_sport_count',
        'get_discount_badge', 'is_active_badge'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['sports']
    
    fieldsets = (
        (_('معلومات الباقة'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('الرياضات المتضمنة'), {
            'fields': ('sports',),
            'description': 'اختر الرياضات المتضمنة في هذه الباقة'
        }),
        (_('الخصومات والفوائد'), {
            'fields': ('discount_percentage',)
        }),
    )
    
    def get_sports_list(self, obj):
        """قائمة الرياضات"""
        sports = obj.sports.all()
        if sports.count() > 2:
            return format_html(
                '<span title="{}">{} رياضات</span>',
                ', '.join([s.name for s in sports]),
                sports.count()
            )
        return ", ".join([s.name for s in sports]) or "—"
    get_sports_list.short_description = _('الرياضات')
    
    def get_sport_count(self, obj):
        """عدد الرياضات"""
        count = obj.sports.count()
        return format_html(
            '<span style="background-color: #0d6efd; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-weight: bold;">{}</span>',
            count
        )
    get_sport_count.short_description = _('العدد')
    
    def get_discount_badge(self, obj):
        """شارة الخصم"""
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">خصم {}%</span>',
                obj.discount_percentage
            )
        return '—'
    get_discount_badge.short_description = _('الخصم')
    
    def is_active_badge(self, obj):
        """شارة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ نشط</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ معطل</span>'
        )
    is_active_badge.short_description = _('الحالة')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).prefetch_related('sports')


class SubscriptionFreezeInline(admin.TabularInline):
    """سجل التجميد ضمن الاشتراك (جدول مدمج)"""
    
    model = SubscriptionFreeze
    extra = 0
    readonly_fields = ['created_at', 'get_freeze_info']
    ordering = ['-created_at']
    fields = ['reason', 'days', 'start_date', 'end_date', 'get_freeze_info', 'created_at']
    
    def get_freeze_info(self, obj):
        """معلومات التجميد"""
        return f"من {obj.start_date} إلى {obj.end_date}"
    get_freeze_info.short_description = _('الفترة')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """لوحة إدارة الاشتراكات"""
    
    list_display = [
        'subscription_number', 'get_member_info', 'get_plan_badge',
        'get_status_badge', 'get_date_info', 'get_price_info'
    ]
    list_filter = [
        'status', 'plan', 'start_date', 'end_date',
        ('status', admin.ChoicesFieldListFilter),
        ('created_at', admin.DateFieldListFilter)
    ]
    search_fields = [
        'subscription_number', 'member__user__phone',
        'member__user__first_name', 'member__member_id', 'member__user__last_name'
    ]
    readonly_fields = [
        'subscription_number', 'original_price', 'discount_amount',
        'final_price', 'created_at', 'get_freeze_summary',
        'get_days_remaining_info'
    ]
    filter_horizontal = ['sports']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    
    inlines = [SubscriptionFreezeInline]
    
    fieldsets = (
        (_('معلومات الاشتراك'), {
            'fields': (
                'subscription_number', 'member', 'plan', 'package',
                'sports', 'status'
            )
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date', 'get_days_remaining_info')
        }),
        (_('بيانات التجميد'), {
            'fields': ('freeze_days_used', 'freeze_days_remaining', 'get_freeze_summary'),
            'classes': ('collapse',)
        }),
        (_('التسعير'), {
            'fields': (
                'original_price', 'discount_amount', 'final_price'
            ),
            'description': 'تفاصيل السعر'
        }),
        (_('المميزات المتبقية'), {
            'fields': ('guest_passes_remaining', 'pt_sessions_remaining'),
            'classes': ('collapse',)
        }),
        (_('ملاحظات وسجلات'), {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_info(self, obj):
        """معلومات العضو"""
        member_name = obj.member.user.get_full_name()
        member_id = obj.member.member_id
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            member_name, member_id
        )
    get_member_info.short_description = _('العضو')
    get_member_info.admin_order_field = 'member__user__first_name'
    
    def get_plan_badge(self, obj):
        """شارة الخطة"""
        colors = {
            'monthly': '#0d6efd',
            'quarterly': '#198754',
            'yearly': '#fd7e14',
            'weekly': '#0dcaf0',
            'daily': '#6f42c1'
        }
        color = colors.get(obj.plan.duration_type, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.plan.name
        )
    get_plan_badge.short_description = _('الخطة')
    get_plan_badge.admin_order_field = 'plan__name'
    
    def get_status_badge(self, obj):
        """شارة الحالة"""
        status_colors = {
            'pending': '#ffc107',      # أصفر
            'active': '#198754',       # أخضر
            'frozen': '#0dcaf0',       # سماوي
            'expired': '#dc3545',      # أحمر
            'cancelled': '#6c757d'     # رمادي
        }
        status_labels = {
            'pending': 'في الانتظار',
            'active': 'نشط',
            'frozen': 'مجمد',
            'expired': 'منتهي',
            'cancelled': 'ملغى'
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{}</span>',
            color, label
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'
    
    def get_date_info(self, obj):
        """معلومات التواريخ"""
        start = obj.start_date.strftime('%d-%m-%Y')
        end = obj.end_date.strftime('%d-%m-%Y')
        
        if obj.status == 'active':
            days = obj.days_remaining
            if days <= 7:
                color = 'red'
                emoji = '⚠️'
            elif days <= 14:
                color = 'orange'
                emoji = '⏳'
            else:
                color = 'green'
                emoji = '✓'
            
            return format_html(
                '{} {} - {}<br/><span style="color: {}; font-weight: bold;">{} يوم متبقي</span>',
                emoji, start, end, color, days
            )
        
        return format_html('{} - {}', start, end)
    get_date_info.short_description = _('الفترة')
    
    def get_price_info(self, obj):
        """معلومات السعر"""
        if obj.discount_amount > 0:
            return format_html(
                '<del style="color: gray;">{} ر.س</del> {} ر.س<br/>'
                '<small style="color: green;">خصم: {} ر.س</small>',
                obj.original_price, obj.final_price, obj.discount_amount
            )
        return format_html('{} ر.س', obj.final_price)
    get_price_info.short_description = _('السعر')
    
    def get_days_remaining_info(self, obj):
        """معلومات الأيام المتبقية"""
        if obj.status == 'active':
            days = obj.days_remaining
            return format_html(
                '<span style="font-size: 14px; font-weight: bold;">{} يوم</span>',
                days
            )
        elif obj.status == 'frozen':
            return format_html(
                '<span style="color: #0dcaf0; font-weight: bold;">مجمد</span>'
            )
        elif obj.status == 'expired':
            return format_html(
                '<span style="color: red; font-weight: bold;">منتهي</span>'
            )
        return '—'
    get_days_remaining_info.short_description = _('معلومات الأيام')
    
    def get_freeze_summary(self, obj):
        """ملخص التجميد"""
        total_freezes = obj.freezes.count()
        if total_freezes > 0:
            return format_html(
                '<strong>{}</strong> عمليات تجميد<br/>'
                'مستخدم: {} يوم | متبقي: {} يوم',
                total_freezes, obj.freeze_days_used, obj.freeze_days_remaining
            )
        return 'لا توجد عمليات تجميد'
    get_freeze_summary.short_description = _('ملخص التجميد')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'member__user', 'plan', 'package'
        ).prefetch_related('sports', 'freezes')
    
    actions = [
        'activate_subscriptions', 'freeze_subscriptions',
        'expire_subscriptions', 'cancel_subscriptions',
        'extend_subscriptions'
    ]
    
    @admin.action(description=_('✓ تفعيل الاشتراكات المحددة'))
    def activate_subscriptions(self, request, queryset):
        """إجراء: تفعيل الاشتراكات"""
        count = queryset.filter(status__in=['pending']).update(status='active')
        self.message_user(request, f'✓ تم تفعيل {count} اشتراك')
    
    @admin.action(description=_('❄️ تجميد الاشتراكات المحددة'))
    def freeze_subscriptions(self, request, queryset):
        """إجراء: تجميد الاشتراكات"""
        count = queryset.filter(status='active').update(status='frozen')
        self.message_user(request, f'❄️ تم تجميد {count} اشتراك')
    
    @admin.action(description=_('⏱️ إنهاء الاشتراكات المحددة'))
    def expire_subscriptions(self, request, queryset):
        """إجراء: إنهاء الاشتراكات"""
        count = queryset.update(status='expired')
        self.message_user(request, f'⏱️ تم إنهاء {count} اشتراك')
    
    @admin.action(description=_('✗ إلغاء الاشتراكات المحددة'))
    def cancel_subscriptions(self, request, queryset):
        """إجراء: إلغاء الاشتراكات"""
        count = queryset.update(status='cancelled')
        self.message_user(request, f'✗ تم إلغاء {count} اشتراك')
    
    @admin.action(description=_('➕ تمديد الاشتراكات لمدة شهر'))
    def extend_subscriptions(self, request, queryset):
        """إجراء: تمديد الاشتراكات"""
        count = 0
        for sub in queryset:
            if sub.status in ['active', 'expired']:
                sub.end_date = sub.end_date + timedelta(days=30)
                sub.save()
                count += 1
        
        self.message_user(request, f'➕ تم تمديد {count} اشتراك')


@admin.register(SubscriptionFreeze)
class SubscriptionFreezeAdmin(admin.ModelAdmin):
    """لوحة إدارة سجلات التجميد"""
    
    list_display = [
        'get_subscription_info', 'get_member_info',
        'days', 'get_date_range', 'reason'
    ]
    list_filter = [
        'created_at',
        ('subscription__status', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'subscription__subscription_number',
        'subscription__member__user__phone',
        'reason'
    ]
    readonly_fields = ['created_at', 'subscription']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('معلومات التجميد'), {
            'fields': ('subscription', 'days', 'start_date', 'end_date', 'reason')
        }),
        (_('التفاصيل'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_subscription_info(self, obj):
        """معلومات الاشتراك"""
        return format_html(
            '<strong>{}</strong>',
            obj.subscription.subscription_number
        )
    get_subscription_info.short_description = _('الاشتراك')
    get_subscription_info.admin_order_field = 'subscription__subscription_number'
    
    def get_member_info(self, obj):
        """معلومات العضو"""
        member = obj.subscription.member
        return format_html(
            '{}<br/><small>{}</small>',
            member.user.get_full_name(),
            member.user.phone
        )
    get_member_info.short_description = _('العضو')
    
    def get_date_range(self, obj):
        """نطاق التواريخ"""
        start = obj.start_date
        end = obj.end_date
        return format_html(
            '{} → {}',
            start.strftime('%d-%m-%Y'),
            end.strftime('%d-%m-%Y')
        )
    get_date_range.short_description = _('الفترة')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'subscription__member__user'
        )
    
    def has_add_permission(self, request):
        """منع الإضافة اليدوية (تُضاف تلقائياً)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """منع الحذف"""
        return False
