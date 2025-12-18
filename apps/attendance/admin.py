from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django.utils import timezone

from .models import Attendance, GuestVisit


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """لوحة إدارة سجلات الحضور والحضور"""
    
    list_display = [
        'get_member_info', 'get_sport_badge', 'trainer',
        'get_check_in_display', 'get_check_out_display',
        'get_duration_badge', 'get_entry_type_badge'
    ]
    list_filter = [
        'sport', 'trainer', 'is_manual_entry',
        ('check_in', admin.DateFieldListFilter),
        ('check_in__date', admin.AllValuesFieldListFilter)
    ]
    search_fields = [
        'member__user__phone', 'member__user__first_name',
        'member__user__last_name', 'member__member_id'
    ]
    readonly_fields = [
        'created_at', 'member', 'subscription',
        'get_member_subscription_status',
        'get_duration_detailed', 'get_member_stats'
    ]
    date_hierarchy = 'check_in'
    ordering = ['-check_in']
    
    fieldsets = (
        (_('معلومات الحضور'), {
            'fields': ('member', 'get_member_subscription_status')
        }),
        (_('الرياضة والمدرب'), {
            'fields': ('sport', 'trainer', 'subscription')
        }),
        (_('أوقات الحضور'), {
            'fields': ('check_in', 'check_out', 'get_duration_detailed')
        }),
        (_('معلومات الإدخال'), {
            'fields': ('is_manual_entry', 'notes')
        }),
        (_('إحصائيات العضو'), {
            'fields': ('get_member_stats',),
            'classes': ('collapse',)
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
        member_phone = obj.member.user.phone
        
        return format_html(
            '<strong>{}</strong><br/>'
            '<small>{} | {}</small>',
            member_name, member_id, member_phone
        )
    get_member_info.short_description = _('العضو')
    get_member_info.admin_order_field = 'member__user__first_name'
    
    def get_sport_badge(self, obj):
        """شارة الرياضة"""
        colors = {
            'gym': '#0d6efd',
            'swimming': '#0dcaf0',
            'yoga': '#198754',
            'boxing': '#dc3545',
            'karate': '#fd7e14',
            'zumba': '#d63384'
        }
        
        # استخدام slug الرياضة إن أمكن
        sport_slug = getattr(obj.sport, 'slug', '').lower()
        color = colors.get(sport_slug, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.sport.name
        )
    get_sport_badge.short_description = _('الرياضة')
    
    def get_check_in_display(self, obj):
        """عرض وقت الدخول"""
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #6c757d;">{}</small>',
            obj.check_in.strftime('%H:%M'),
            obj.check_in.strftime('%d-%m-%Y')
        )
    get_check_in_display.short_description = _('الدخول')
    
    def get_check_out_display(self, obj):
        """عرض وقت الخروج"""
        if obj.check_out:
            return format_html(
                '<strong>{}</strong><br/>'
                '<small style="color: #6c757d;">{}</small>',
                obj.check_out.strftime('%H:%M'),
                obj.check_out.strftime('%d-%m-%Y')
            )
        return format_html(
            '<span style="color: #ffc107; font-weight: bold;">⏳ مازال موجود</span>'
        )
    get_check_out_display.short_description = _('الخروج')
    
    def get_duration_badge(self, obj):
        """شارة المدة"""
        if obj.check_out and obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            
            # ألوان بناءً على المدة
            if obj.duration_minutes < 30:
                color = '#6c757d'
            elif obj.duration_minutes < 60:
                color = '#0dcaf0'
            elif obj.duration_minutes < 120:
                color = '#198754'
            else:
                color = '#0d6efd'
            
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; '
                'border-radius: 10px; font-weight: bold;">{}h {}m</span>',
                color, hours, minutes
            )
        elif obj.check_out:
            return '—'
        else:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">⏱️ جاري</span>'
            )
    get_duration_badge.short_description = _('المدة')
    
    def get_entry_type_badge(self, obj):
        """شارة نوع الإدخال"""
        if obj.is_manual_entry:
            return format_html(
                '<span style="background-color: #fd7e14; color: white; padding: 3px 10px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">📝 يدوي</span>'
            )
        return format_html(
            '<span style="background-color: #198754; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">🔑 تلقائي</span>'
        )
    get_entry_type_badge.short_description = _('النوع')
    
    def get_duration_detailed(self, obj):
        """عرض مفصل للمدة"""
        if obj.check_out and obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            seconds = 0  # يمكن إضافتها من الـ model
            
            return format_html(
                '<strong>{} ساعة و {} دقيقة</strong><br/>'
                '<small>(إجمالي: {} دقيقة)</small>',
                hours, minutes, obj.duration_minutes
            )
        elif not obj.check_out:
            # حساب المدة حتى الآن
            current_duration = (timezone.now() - obj.check_in).total_seconds() / 60
            hours = int(current_duration // 60)
            minutes = int(current_duration % 60)
            
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">'
                '⏱️ جاري: {} ساعة و {} دقيقة</span>',
                hours, minutes
            )
        return 'بدون خروج'
    get_duration_detailed.short_description = _('المدة المفصلة')
    
    def get_member_subscription_status(self, obj):
        """حالة اشتراك العضو"""
        if obj.subscription:
            status_colors = {
                'active': '#198754',
                'frozen': '#0dcaf0',
                'expired': '#dc3545',
                'pending': '#ffc107'
            }
            color = status_colors.get(obj.subscription.status, '#6c757d')
            
            days_remaining = obj.subscription.days_remaining
            
            return format_html(
                '<strong style="background-color: {}; color: white; padding: 5px 10px; '
                'border-radius: 5px; display: inline-block;">{}</strong><br/>'
                '<small>متبقي: {} أيام</small>',
                color, obj.subscription.get_status_display(), days_remaining
            )
        return format_html(
            '<span style="color: red;">لا يوجد اشتراك نشط</span>'
        )
    get_member_subscription_status.short_description = _('حالة الاشتراك')
    
    def get_member_stats(self, obj):
        """إحصائيات العضو"""
        # عدد الزيارات هذا الشهر
        this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_visits = Attendance.objects.filter(
            member=obj.member,
            check_in__gte=this_month_start
        ).count()
        
        # عدد الزيارات هذا الأسبوع
        week_start = timezone.now() - timedelta(days=7)
        week_visits = Attendance.objects.filter(
            member=obj.member,
            check_in__gte=week_start
        ).count()
        
        # إجمالي الزيارات
        total_visits = Attendance.objects.filter(member=obj.member).count()
        
        return format_html(
            '<strong>إجمالي الزيارات:</strong> {}<br/>'
            '<strong>هذا الشهر:</strong> {} 📅<br/>'
            '<strong>هذا الأسبوع:</strong> {} 📊',
            total_visits, this_month_visits, week_visits
        )
    get_member_stats.short_description = _('إحصائيات')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'member__user', 'sport', 'trainer__user', 'subscription'
        )
    
    actions = ['mark_checked_out', 'export_attendance_csv']
    
    @admin.action(description=_('🔚 تسجيل الخروج للحاضرين (بدون خروج)'))
    def mark_checked_out(self, request, queryset):
        """إجراء: تسجيل خروج تلقائي"""
        count = queryset.filter(check_out__isnull=True).update(
            check_out=timezone.now()
        )
        self.message_user(request, f'🔚 تم تسجيل خروج {count} عضو')
    
    @admin.action(description=_('📥 تصدير إلى CSV'))
    def export_attendance_csv(self, request, queryset):
        """إجراء: تصدير الحضور إلى CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'العضو', 'الهاتف', 'الرياضة', 'المدرب',
            'وقت الدخول', 'وقت الخروج', 'المدة (دقيقة)', 'النوع'
        ])
        
        for attendance in queryset:
            writer.writerow([
                attendance.member.user.get_full_name(),
                attendance.member.user.phone,
                attendance.sport.name,
                attendance.trainer.user.get_full_name() if attendance.trainer else '—',
                attendance.check_in.strftime('%H:%M %d-%m-%Y'),
                attendance.check_out.strftime('%H:%M') if attendance.check_out else '—',
                attendance.duration_minutes or '—',
                'يدوي' if attendance.is_manual_entry else 'تلقائي'
            ])
        
        return response
    export_attendance_csv.short_description = _('تصدير إلى CSV')


@admin.register(GuestVisit)
class GuestVisitAdmin(admin.ModelAdmin):
    """لوحة إدارة زيارات الضيوف والضيوف"""
    
    list_display = [
        'get_guest_info', 'get_host_member_info',
        'get_visit_date_badge', 'get_check_in_display',
        'get_check_out_display', 'get_duration_badge'
    ]
    list_filter = [
        ('visit_date', admin.DateFieldListFilter),
        ('host_member', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'guest_name', 'guest_phone',
        'host_member__user__phone', 'host_member__user__first_name',
        'host_member__user__last_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at',
        'get_duration_detailed', 'get_host_subscription_status'
    ]
    date_hierarchy = 'visit_date'
    ordering = ['-visit_date']
    
    fieldsets = (
        (_('معلومات الضيف'), {
            'fields': ('guest_name', 'guest_phone')
        }),
        (_('العضو المضيف'), {
            'fields': ('host_member', 'get_host_subscription_status')
        }),
        (_('وقت الزيارة'), {
            'fields': ('visit_date', 'check_in', 'check_out', 'get_duration_detailed')
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
    
    def get_guest_info(self, obj):
        """معلومات الضيف"""
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #6c757d;">{}</small>',
            obj.guest_name, obj.guest_phone
        )
    get_guest_info.short_description = _('الضيف')
    
    def get_host_member_info(self, obj):
        """معلومات العضو المضيف"""
        member_name = obj.host_member.user.get_full_name()
        member_id = obj.host_member.member_id
        
        return format_html(
            '<strong>{}</strong><br/>'
            '<small style="color: #6c757d;">{}</small>',
            member_name, member_id
        )
    get_host_member_info.short_description = _('المضيف')
    get_host_member_info.admin_order_field = 'host_member__user__first_name'
    
    def get_visit_date_badge(self, obj):
        """شارة تاريخ الزيارة"""
        today = timezone.now().date()
        
        if obj.visit_date == today:
            return format_html(
                '<span style="background-color: #0d6efd; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">📅 اليوم</span>'
            )
        elif obj.visit_date == today - timedelta(days=1):
            return format_html(
                '<span style="background-color: #0dcaf0; color: white; padding: 4px 12px; '
                'border-radius: 15px; font-weight: bold;">📅 أمس</span>'
            )
        
        return obj.visit_date.strftime('%d-%m-%Y')
    get_visit_date_badge.short_description = _('التاريخ')
    
    def get_check_in_display(self, obj):
        """عرض وقت الدخول"""
        if obj.check_in:
            return format_html(
                '<strong>{}</strong>',
                obj.check_in.strftime('%H:%M')
            )
        return '—'
    get_check_in_display.short_description = _('الدخول')
    
    def get_check_out_display(self, obj):
        """عرض وقت الخروج"""
        if obj.check_out:
            return format_html(
                '<strong>{}</strong>',
                obj.check_out.strftime('%H:%M')
            )
        return format_html(
            '<span style="color: #ffc107; font-weight: bold;">⏳ مازال موجود</span>'
        )
    get_check_out_display.short_description = _('الخروج')
    
    def get_duration_badge(self, obj):
        """شارة المدة"""
        if obj.check_out and obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 3px 10px; '
                'border-radius: 10px; font-weight: bold;">{}h {}m</span>',
                hours, minutes
            )
        elif obj.check_out:
            return '—'
        else:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">⏱️ جاري</span>'
            )
    get_duration_badge.short_description = _('المدة')
    
    def get_duration_detailed(self, obj):
        """عرض مفصل للمدة"""
        if obj.check_out and obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            
            return format_html(
                '<strong>{} ساعة و {} دقيقة</strong>',
                hours, minutes
            )
        elif not obj.check_out:
            current_duration = (timezone.now() - obj.check_in).total_seconds() / 60
            hours = int(current_duration // 60)
            minutes = int(current_duration % 60)
            
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">'
                '⏱️ جاري: {} ساعة و {} دقيقة</span>',
                hours, minutes
            )
        return 'بدون خروج'
    get_duration_detailed.short_description = _('المدة المفصلة')
    
    def get_host_subscription_status(self, obj):
        """حالة اشتراك المضيف"""
        active_subscription = obj.host_member.subscriptions.filter(
            status='active'
        ).first()
        
        if active_subscription:
            guest_passes = active_subscription.guest_passes_remaining
            
            return format_html(
                '<strong style="color: green;">✓ اشتراك نشط</strong><br/>'
                '<small>باقي ضيوف: {} 👥</small>',
                guest_passes
            )
        
        return format_html(
            '<span style="color: red;">❌ لا يوجد اشتراك نشط</span>'
        )
    get_host_subscription_status.short_description = _('اشتراك المضيف')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'host_member__user'
        ).prefetch_related('host_member__subscriptions')
    
    actions = ['mark_checked_out_guests']
    
    @admin.action(description=_('🔚 تسجيل خروج الضيوف (المتواجدين)'))
    def mark_checked_out_guests(self, request, queryset):
        """إجراء: تسجيل خروج الضيوف"""
        count = queryset.filter(check_out__isnull=True).update(
            check_out=timezone.now()
        )
        self.message_user(request, f'🔚 تم تسجيل خروج {count} ضيف')
    
    mark_checked_out_guests.short_description = _('تسجيل الخروج')
