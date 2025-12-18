from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Q
from datetime import date

from .models import Member, MemberBodyMetrics


class MemberBodyMetricsInline(admin.TabularInline):
    """عرض قياسات الجسم ضمن العضو (جدول مدمج)"""
    
    model = MemberBodyMetrics
    extra = 0
    readonly_fields = ['date', 'get_bmi', 'created_at']
    ordering = ['-date']
    fields = ['date', 'weight', 'get_bmi', 'chest', 'waist', 'hips', 'arms', 'thighs', 'notes']
    
    def get_bmi(self, obj):
        """حساب وعرض BMI"""
        if obj.member.height and obj.weight:
            bmi = (obj.weight / ((obj.member.height / 100) ** 2))
            color = '#28a745'  # أخضر
            
            if bmi < 18.5:
                category = 'ناقص وزن'
            elif bmi < 25:
                category = 'وزن طبيعي'
                color = '#198754'
            elif bmi < 30:
                category = 'زيادة وزن'
                color = '#ffc107'
            else:
                category = 'سمنة'
                color = '#dc3545'
            
            return format_html(
                '<span style="background-color: {}; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
                '{:.1f} ({})</span>',
                color, bmi, category
            )
        return '—'
    get_bmi.short_description = 'BMI'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """لوحة إدارة الأعضاء - عرض وتحديث بيانات الأعضاء"""
    
    list_display = [
        'member_id', 'get_full_name', 'get_phone_display',
        'get_gender_badge', 'get_age_display', 'get_active_status',
        'reward_points', 'join_date', 'photo_thumbnail'
    ]
    list_filter = [
        'gender', 'is_active', 'blood_type', 'join_date',
        ('created_at', admin.DateFieldListFilter)
    ]
    search_fields = [
        'member_id', 'user__phone', 'user__first_name',
        'user__last_name', 'user__email', 'national_id'
    ]
    readonly_fields = [
        'member_id', 'join_date', 'created_at', 'updated_at',
        'photo_preview_large', 'get_bmi_current', 'get_current_weight'
    ]
    ordering = ['-join_date']
    date_hierarchy = 'join_date'
    
    fieldsets = (
        (_('معلومات العضوية'), {
            'fields': ('user', 'member_id', 'join_date', 'photo', 'photo_preview_large')
        }),
        (_('البيانات الشخصية'), {
            'fields': ('gender', 'date_of_birth', 'national_id', 'address', 'notes')
        }),
        (_('البيانات الصحية'), {
            'fields': (
                'height', 'get_current_weight', 'blood_type',
                'medical_conditions', 'get_bmi_current'
            ),
            'description': 'البيانات الصحية للعضو'
        }),
        (_('جهة الاتصال للطوارئ'), {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        (_('النقاط والحالة'), {
            'fields': ('is_active', 'reward_points')
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MemberBodyMetricsInline]
    
    def get_full_name(self, obj):
        """اسم العضو الكامل"""
        full_name = obj.user.get_full_name()
        return full_name if full_name else obj.user.phone
    get_full_name.short_description = _('الاسم')
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_phone_display(self, obj):
        """رقم الهاتف"""
        return obj.user.phone
    get_phone_display.short_description = _('الهاتف')
    get_phone_display.admin_order_field = 'user__phone'
    
    def get_gender_badge(self, obj):
        """شارة النوع"""
        if obj.gender == 'male':
            return format_html(
                '<span style="background-color: #0dcaf0; color: white; '
                'padding: 3px 10px; border-radius: 3px; font-weight: bold;">👨 ذكر</span>'
            )
        elif obj.gender == 'female':
            return format_html(
                '<span style="background-color: #d63384; color: white; '
                'padding: 3px 10px; border-radius: 3px; font-weight: bold;">👩 أنثى</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 10px; border-radius: 3px;">غير محدد</span>'
        )
    get_gender_badge.short_description = _('النوع')
    
    def get_age_display(self, obj):
        """عمر العضو"""
        if obj.age:
            return format_html(
                '<span style="font-weight: bold;">{} سنة</span>',
                obj.age
            )
        return '—'
    get_age_display.short_description = _('العمر')
    
    def get_active_status(self, obj):
        """حالة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">🟢 نشط</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">🔴 معطل</span>'
        )
    get_active_status.short_description = _('الحالة')
    
    def get_current_weight(self, obj):
        """أحدث وزن"""
        latest_metric = obj.body_metrics.latest('date')
        if latest_metric and latest_metric.weight:
            return format_html(
                '<strong>{} كغ</strong> <br/><small>({}</small>',
                latest_metric.weight,
                latest_metric.date.strftime('%d-%m-%Y')
            )
        return 'لا توجد بيانات'
    get_current_weight.short_description = _('الوزن الحالي')
    
    def get_bmi_current(self, obj):
        """BMI الحالي"""
        latest_metric = obj.body_metrics.latest('date')
        if latest_metric and latest_metric.height and latest_metric.weight:
            bmi = (latest_metric.weight / ((latest_metric.height / 100) ** 2))
            
            if bmi < 18.5:
                category = 'ناقص وزن'
                color = '#0dcaf0'
            elif bmi < 25:
                category = 'وزن طبيعي'
                color = '#198754'
            elif bmi < 30:
                category = 'زيادة وزن'
                color = '#ffc107'
            else:
                category = 'سمنة'
                color = '#dc3545'
            
            return format_html(
                '<span style="background-color: {}; color: white; '
                'padding: 5px 10px; border-radius: 5px; font-weight: bold;">'
                '{:.1f} - {}</span>',
                color, bmi, category
            )
        return 'لا توجد بيانات'
    get_bmi_current.short_description = _('BMI الحالي')
    
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
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('body_metrics')
    
    actions = [
        'activate_members', 'deactivate_members',
        'reset_reward_points', 'export_members_csv'
    ]
    
    def activate_members(self, request, queryset):
        """إجراء: تفعيل الأعضاء"""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f'✓ تم تفعيل {count} عضو'
        )
    activate_members.short_description = _('تفعيل الأعضاء المختارين')
    
    def deactivate_members(self, request, queryset):
        """إجراء: تعطيل الأعضاء"""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'✓ تم تعطيل {count} عضو'
        )
    deactivate_members.short_description = _('تعطيل الأعضاء المختارين')
    
    def reset_reward_points(self, request, queryset):
        """إجراء: إعادة تعيين نقاط المكافأة"""
        count = queryset.update(reward_points=0)
        self.message_user(
            request,
            f'✓ تم إعادة تعيين نقاط {count} عضو'
        )
    reset_reward_points.short_description = _('إعادة تعيين النقاط')
    
    def export_members_csv(self, request, queryset):
        """إجراء: تصدير إلى CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="members.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'معرف العضو', 'الاسم', 'الهاتف', 'البريد الإلكتروني',
            'النوع', 'العمر', 'تاريخ الانضمام', 'النقاط', 'الحالة'
        ])
        
        for member in queryset:
            writer.writerow([
                member.member_id,
                member.user.get_full_name(),
                member.user.phone,
                member.user.email,
                member.get_gender_display(),
                member.age or '—',
                member.join_date.strftime('%d-%m-%Y'),
                member.reward_points,
                'نشط' if member.is_active else 'معطل'
            ])
        
        return response
    export_members_csv.short_description = _('تصدير إلى CSV')


@admin.register(MemberBodyMetrics)
class MemberBodyMetricsAdmin(admin.ModelAdmin):
    """لوحة إدارة قياسات الجسم"""
    
    list_display = [
        'member_name', 'date', 'weight',
        'get_bmi_badge', 'chest', 'waist'
    ]
    list_filter = ['date', ('member', admin.RelatedFieldListFilter)]
    search_fields = ['member__member_id', 'member__user__phone']
    readonly_fields = ['created_at', 'updated_at', 'get_bmi_display']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('بيانات الجسم'), {
            'fields': ('member', 'date', 'weight', 'get_bmi_display')
        }),
        (_('القياسات الإضافية'), {
            'fields': ('chest', 'waist', 'hips', 'arms', 'thighs', 'body_fat_percentage', 'muscle_mass')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_name(self, obj):
        """اسم العضو"""
        return obj.member.user.get_full_name()
    member_name.short_description = _('العضو')
    member_name.admin_order_field = 'member__user__first_name'
    
    def get_bmi_badge(self, obj):
        """شارة BMI"""
        if obj.member.height and obj.weight:
            bmi = (obj.weight / ((obj.member.height / 100) ** 2))
            
            if bmi < 18.5:
                category = 'ناقص'
                color = '#0dcaf0'
            elif bmi < 25:
                category = 'طبيعي'
                color = '#198754'
            elif bmi < 30:
                category = 'زيادة'
                color = '#ffc107'
            else:
                category = 'سمنة'
                color = '#dc3545'
            
            return format_html(
                '<span style="background-color: {}; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
                '{:.1f}</span>',
                color, bmi
            )
        return '—'
    get_bmi_badge.short_description = _('BMI')
    
    def get_bmi_display(self, obj):
        """عرض مفصل للـ BMI"""
        if obj.member.height and obj.weight:
            bmi = (obj.weight / ((obj.member.height / 100) ** 2))
            
            if bmi < 18.5:
                category = 'ناقص وزن'
            elif bmi < 25:
                category = 'وزن طبيعي'
            elif bmi < 30:
                category = 'زيادة وزن'
            else:
                category = 'سمنة'
            
            return format_html(
                '<strong>BMI: {:.1f}</strong> ({}) <br/>'
                '<small>الطول: {} سم | الوزن: {} كغ</small>',
                bmi, category, obj.member.height, obj.weight
            )
        return 'بيانات غير كافية لحساب BMI'
    get_bmi_display.short_description = _('مؤشر كتلة الجسم')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related('member__user')
