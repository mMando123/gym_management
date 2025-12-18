from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django.utils import timezone

from .models import RewardRule, PointTransaction, Reward, RewardRedemption


@admin.register(RewardRule)
class RewardRuleAdmin(admin.ModelAdmin):
    """لوحة إدارة قواعد كسب النقاط والمكافآت"""
    
    list_display = [
        'name', 'get_action_badge', 'get_points_badge',
        'description', 'is_active_badge'
    ]
    list_filter = [
        'action_type', 'is_active',
        ('created_at', admin.DateFieldListFilter)
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['action_type']
    
    fieldsets = (
        (_('معلومات القاعدة'), {
            'fields': ('name', 'description')
        }),
        (_('نوع الإجراء والنقاط'), {
            'fields': ('action_type', 'points')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_action_badge(self, obj):
        """شارة نوع الإجراء"""
        action_map = {
            'attendance': ('حضور', '#198754'),
            'subscription': ('اشتراك', '#0d6efd'),
            'early_renewal': ('تجديد مبكر', '#0dcaf0'),
            'referral': ('إحالة', '#fd7e14'),
            'birthday': ('عيد ميلاد', '#d63384')
        }
        
        label, color = action_map.get(obj.action_type, ('أخرى', '#6c757d'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{}</span>',
            color, label
        )
    get_action_badge.short_description = _('النوع')
    
    def get_points_badge(self, obj):
        """شارة النقاط"""
        return format_html(
            '<span style="background-color: #ffc107; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">+{} نقطة</span>',
            obj.points
        )
    get_points_badge.short_description = _('النقاط')
    
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
        return super().get_queryset(request)


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """لوحة إدارة حركات النقاط والرصيد"""
    
    list_display = [
        'get_member_info', 'get_transaction_type_badge',
        'get_points_display', 'balance_after',
        'description', 'created_at'
    ]
    list_filter = [
        'transaction_type',
        ('created_at', admin.DateFieldListFilter),
        ('member', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'member__user__phone', 'member__user__first_name',
        'member__user__last_name', 'member__member_id',
        'description'
    ]
    readonly_fields = [
        'created_at', 'member', 'get_member_current_balance'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات العضو'), {
            'fields': ('member', 'get_member_current_balance')
        }),
        (_('حركة النقاط'), {
            'fields': ('transaction_type', 'points', 'balance_after')
        }),
        (_('الوصف'), {
            'fields': ('description',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_info(self, obj):
        """معلومات العضو"""
        member_name = obj.member.user.get_full_name()
        member_id = obj.member.member_id
        
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #6c757d;">{}</small>',
            member_name, member_id
        )
    get_member_info.short_description = _('العضو')
    get_member_info.admin_order_field = 'member__user__first_name'
    
    def get_transaction_type_badge(self, obj):
        """شارة نوع الحركة"""
        type_map = {
            'earned': ('اكتسبت', '#198754', '+'),
            'redeemed': ('استبدلت', '#dc3545', '−'),
            'expired': ('انتهت صلاحيتها', '#6c757d', '✗'),
            'adjusted': ('تعديل', '#0d6efd', '~')
        }
        
        label, color, icon = type_map.get(obj.transaction_type, ('أخرى', '#6c757d', '•'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{} {}</span>',
            color, icon, label
        )
    get_transaction_type_badge.short_description = _('النوع')
    
    def get_points_display(self, obj):
        """عرض النقاط بألوان"""
        if obj.transaction_type == 'earned':
            color = '#198754'
            icon = '✓'
            symbol = '+'
        elif obj.transaction_type == 'redeemed':
            color = '#dc3545'
            icon = '✗'
            symbol = '−'
        else:
            color = '#6c757d'
            icon = '•'
            symbol = '='
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">'
            '{}{} {}</span>',
            color, symbol, icon, abs(obj.points)
        )
    get_points_display.short_description = _('النقاط')
    
    def get_member_current_balance(self, obj):
        """الرصيد الحالي للعضو"""
        current_balance = obj.member.reward_points
        
        return format_html(
            '<strong style="font-size: 14px;">الرصيد الحالي: {} نقطة</strong>',
            current_balance
        )
    get_member_current_balance.short_description = _('الرصيد الحالي')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related('member__user')
    
    def has_add_permission(self, request):
        """منع الإضافة اليدوية (تُضاف تلقائياً)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """منع الحذف"""
        return False


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    """لوحة إدارة المكافآت والجوائز"""
    
    list_display = [
        'name', 'get_points_required_badge', 'get_quantity_badge',
        'get_validity_badge', 'image_thumbnail', 'is_active_badge'
    ]
    list_filter = [
        'is_active', 'valid_from', 'valid_until',
        ('created_at', admin.DateFieldListFilter)
    ]
    search_fields = ['name', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'image_preview_large',
        'get_redemption_count'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات المكافأة'), {
            'fields': ('name', 'description', 'image', 'image_preview_large')
        }),
        (_('التفاصيل والنقاط'), {
            'fields': ('points_required', 'quantity_available')
        }),
        (_('فترة الصلاحية'), {
            'fields': ('valid_from', 'valid_until')
        }),
        (_('الحالة'), {
            'fields': ('is_active',)
        }),
        (_('الإحصائيات'), {
            'fields': ('get_redemption_count',),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_points_required_badge(self, obj):
        """شارة النقاط المطلوبة"""
        return format_html(
            '<span style="background-color: #ffc107; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{} نقطة</span>',
            obj.points_required
        )
    get_points_required_badge.short_description = _('النقاط المطلوبة')
    
    def get_quantity_badge(self, obj):
        """شارة الكمية المتاحة"""
        if obj.quantity_available is None:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">غير محدود</span>'
            )
        elif obj.quantity_available <= 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">مستنفذ</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #0d6efd; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">{} متوفر</span>',
                obj.quantity_available
            )
    get_quantity_badge.short_description = _('الكمية')
    
    def get_validity_badge(self, obj):
        """شارة صلاحية المكافأة"""
        today = timezone.now().date()
        
        if obj.valid_until and obj.valid_until < today:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">منتهية الصلاحية</span>'
            )
        elif obj.valid_from and obj.valid_from > today:
            return format_html(
                '<span style="background-color: #ffc107; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">قريباً</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">صالحة</span>'
            )
    get_validity_badge.short_description = _('الصلاحية')
    
    def image_thumbnail(self, obj):
        """معاينة صغيرة للصورة"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="border-radius: 5px; object-fit: cover;" />',
                obj.image.url
            )
        return '—'
    image_thumbnail.short_description = _('الصورة')
    
    def image_preview_large(self, obj):
        """معاينة كبيرة للصورة"""
        if obj.image:
            return format_html(
                '<img src="{}" width="200" height="200" '
                'style="border-radius: 10px; object-fit: cover; margin: 10px 0;" />',
                obj.image.url
            )
        return format_html('<em>لا توجد صورة</em>')
    image_preview_large.short_description = _('معاينة الصورة')
    
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
    
    def get_redemption_count(self, obj):
        """عدد الاستبدالات"""
        count = obj.redemptions.filter(status='delivered').count()
        
        return format_html(
            '<strong>عدد الاستبدالات:</strong> {}<br/>',
            count
        )
    get_redemption_count.short_description = _('الاستبدالات')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).prefetch_related('redemptions')


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    """لوحة إدارة استبدالات المكافآت والجوائز"""
    
    list_display = [
        'get_member_info', 'reward', 'get_points_used_badge',
        'get_status_badge', 'redeemed_at'
    ]
    list_filter = [
        'status',
        ('redeemed_at', admin.DateFieldListFilter),
        ('member', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'member__user__phone', 'member__user__first_name',
        'member__user__last_name', 'reward__name'
    ]
    readonly_fields = [
        'redeemed_at', 'delivered_at',
        'member', 'reward'
    ]
    date_hierarchy = 'redeemed_at'
    ordering = ['-redeemed_at']
    
    fieldsets = (
        (_('معلومات الاستبدال'), {
            'fields': ('member', 'reward')
        }),
        (_('النقاط والحالة'), {
            'fields': ('points_used', 'status')
        }),
        (_('التواريخ'), {
            'fields': ('redeemed_at', 'delivered_at', 'rejected_at')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_info(self, obj):
        """معلومات العضو"""
        member_name = obj.member.user.get_full_name()
        member_id = obj.member.member_id
        
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #6c757d;">{}</small>',
            member_name, member_id
        )
    get_member_info.short_description = _('العضو')
    get_member_info.admin_order_field = 'member__user__first_name'
    
    def get_points_used_badge(self, obj):
        """شارة النقاط المستخدمة"""
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">−{} نقطة</span>',
            obj.points_used
        )
    get_points_used_badge.short_description = _('النقاط')
    
    def get_status_badge(self, obj):
        """شارة الحالة"""
        status_map = {
            'pending': ('قيد الانتظار', '#ffc107'),
            'approved': ('موافق عليه', '#0d6efd'),
            'delivered': ('تم التسليم', '#198754'),
            'rejected': ('مرفوض', '#dc3545')
        }
        
        label, color = status_map.get(obj.status, ('غير معروف', '#6c757d'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{}</span>',
            color, label
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'member__user', 'reward'
        )
    
    actions = [
        'approve_redemptions', 'mark_as_delivered',
        'reject_redemptions'
    ]
    
    @admin.action(description=_('✓ الموافقة على الاستبدالات'))
    def approve_redemptions(self, request, queryset):
        """إجراء: الموافقة على الاستبدالات"""
        count = queryset.filter(status='pending').update(status='approved')
        self.message_user(
            request,
            f'✓ تمت الموافقة على {count} استبدال'
        )
    
    @admin.action(description=_('📦 تحديد كـ "تم التسليم"'))
    def mark_as_delivered(self, request, queryset):
        """إجراء: تحديد كـ تم التسليم"""
        count = queryset.filter(status='approved').update(
            status='delivered',
            delivered_at=timezone.now()
        )
        self.message_user(
            request,
            f'📦 تم تحديث {count} استبدال كـ "تم التسليم"'
        )
    
    @admin.action(description=_('✗ رفض الاستبدالات'))
    def reject_redemptions(self, request, queryset):
        """إجراء: رفض الاستبدالات"""
        # استرجاع النقاط إلى الأعضاء
        for redemption in queryset.filter(status='pending'):
            redemption.member.reward_points += redemption.points_used
            redemption.member.save()
        
        count = queryset.filter(status='pending').update(
            status='rejected',
            rejected_at=timezone.now()
        )
        self.message_user(
            request,
            f'✗ تم رفض {count} استبدال واسترجاع النقاط'
        )
