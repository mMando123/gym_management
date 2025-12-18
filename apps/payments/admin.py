from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Sum, Q
from datetime import timedelta
from django.utils import timezone

from .models import Payment, Invoice, Installment


class InstallmentInline(admin.TabularInline):
    """الأقساط ضمن الدفعة (جدول مدمج)"""
    
    model = Installment
    extra = 0
    readonly_fields = ['paid_date', 'due_date', 'get_status_badge']
    fields = [
        'installment_number', 'amount', 'due_date',
        'paid_date', 'get_status_badge'
    ]
    ordering = ['installment_number']

    def get_status_badge(self, obj):
        """شارة حالة القسط"""
        if obj.is_paid:
            return format_html(
                '<span style="background-color: #198754; color: white; '
                'padding: 3px 10px; border-radius: 10px; font-weight: bold;">✓ مدفوع</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 10px; border-radius: 10px; font-weight: bold;">✗ غير مدفوع</span>'
        )
    get_status_badge.short_description = _('الحالة')


class InvoiceInline(admin.StackedInline):
    """الفاتورة ضمن الدفعة (عرض مكدس)"""
    
    model = Invoice
    extra = 0
    readonly_fields = ['invoice_number', 'issued_date', 'total']
    fields = [
        'invoice_number', 'subtotal', 'discount', 'tax', 'total', 'is_paid',
        'issued_date', 'due_date'
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """لوحة إدارة المدفوعات والدفعات"""
    
    list_display = [
        'payment_number', 'get_member_info', 'get_type_badge',
        'get_payment_method_badge', 'get_status_badge',
        'get_amount_display', 'get_payment_percentage', 'created_at'
    ]
    list_filter = [
        'status', 'payment_type', 'payment_method',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = [
        'payment_number', 'member__user__phone',
        'member__user__first_name', 'member__user__last_name',
        'transaction_id', 'receipt_number'
    ]
    readonly_fields = [
        'payment_number', 'created_at', 'updated_at',
        'get_payment_info', 'get_tax_info'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    inlines = [InvoiceInline, InstallmentInline]
    
    fieldsets = (
        (_('معلومات الدفعة'), {
            'fields': ('payment_number', 'member', 'subscription')
        }),
        (_('نوع وطريقة الدفع'), {
            'fields': ('payment_type', 'payment_method', 'status')
        }),
        (_('بيانات المعاملة'), {
            'fields': ('transaction_id', 'receipt_number', 'processed_by')
        }),
        (_('المبالغ'), {
            'fields': (
                'amount', 'discount', 'get_tax_info', 'total',
                'amount_paid', 'amount_remaining', 'get_payment_info'
            ),
            'description': 'تفاصيل المبالغ المالية'
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
    
    def get_type_badge(self, obj):
        """شارة نوع الدفعة"""
        types = {
            'subscription': 'اشتراك',
            'trainer': 'مدرب',
            'locker': 'خزنة',
            'other': 'أخرى'
        }
        colors = {
            'subscription': '#0d6efd',
            'trainer': '#0dcaf0',
            'locker': '#198754',
            'other': '#6c757d'
        }
        
        label = types.get(obj.payment_type, obj.payment_type)
        color = colors.get(obj.payment_type, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-weight: bold;">{}</span>',
            color, label
        )
    get_type_badge.short_description = _('النوع')
    
    def get_payment_method_badge(self, obj):
        """شارة طريقة الدفع"""
        methods = {
            'cash': 'نقدي',
            'card': 'بطاقة',
            'bank_transfer': 'تحويل بنكي',
            'online': 'دفع إلكتروني'
        }
        colors = {
            'cash': '#198754',
            'card': '#0dcaf0',
            'bank_transfer': '#0d6efd',
            'online': '#fd7e14'
        }
        
        label = methods.get(obj.payment_method, obj.payment_method)
        color = colors.get(obj.payment_method, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px;">{}</span>',
            color, label
        )
    get_payment_method_badge.short_description = _('الطريقة')
    
    def get_status_badge(self, obj):
        """شارة الحالة"""
        status_map = {
            'completed': ('أكمل', '#198754'),
            'pending': ('في الانتظار', '#ffc107'),
            'partial': ('جزئي', '#0dcaf0'),
            'failed': ('فشل', '#dc3545'),
            'refunded': ('مسترجع', '#6f42c1')
        }
        
        label, color = status_map.get(obj.status, ('غير محدد', '#6c757d'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 15px; font-weight: bold;">{}</span>',
            color, label
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'
    
    def get_amount_display(self, obj):
        """عرض المبلغ"""
        if obj.discount > 0:
            return format_html(
                '<del style="color: gray; text-decoration: line-through;">{} ر.س</del>'
                '<br/><strong>{} ر.س</strong>',
                obj.amount, obj.total
            )
        return format_html('<strong>{} ر.س</strong>', obj.total)
    get_amount_display.short_description = _('المبلغ')
    
    def get_payment_percentage(self, obj):
        """نسبة الدفع"""
        if obj.total > 0:
            percentage = (obj.amount_paid / obj.total) * 100
            
            if percentage == 0:
                color = '#dc3545'
                emoji = '0%'
            elif percentage < 50:
                color = '#ffc107'
                emoji = '⏳'
            elif percentage < 100:
                color = '#0dcaf0'
                emoji = '⌛'
            else:
                color = '#198754'
                emoji = '✓'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} ({:.0f}%)</span>',
                color, emoji, percentage
            )
        return '—'
    get_payment_percentage.short_description = _('التقدم')
    
    def get_tax_info(self, obj):
        """معلومات الضريبة"""
        if obj.tax > 0:
            tax_percentage = (obj.tax / obj.amount * 100) if obj.amount > 0 else 0
            return format_html(
                '<strong>{} ر.س</strong> ({:.1f}% ضريبة القيمة المضافة)',
                obj.tax, tax_percentage
            )
        return 'لا توجد ضريبة'
    get_tax_info.short_description = _('الضريبة')
    
    def get_payment_info(self, obj):
        """معلومات الدفع"""
        return format_html(
            '<strong>مدفوع:</strong> {} ر.س<br/>'
            '<strong>متبقي:</strong> {} ر.س',
            obj.amount_paid, obj.amount_remaining
        )
    get_payment_info.short_description = _('معلومات الدفع')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'member__user', 'subscription', 'invoice'
        ).prefetch_related('installments')
    
    actions = [
        'mark_as_completed', 'mark_as_pending',
        'mark_as_partial', 'generate_invoices'
    ]
    
    @admin.action(description=_('✓ تحديد كمكتمل'))
    def mark_as_completed(self, request, queryset):
        """إجراء: تحديد كمكتمل"""
        count = queryset.filter(
            Q(status__in=['pending', 'partial'])
        ).update(status='completed')
        self.message_user(request, f'✓ تم تحديد {count} دفعة كمكتملة')
    
    @admin.action(description=_('⏳ تحديد كمعلقة'))
    def mark_as_pending(self, request, queryset):
        """إجراء: تحديد كمعلقة"""
        count = queryset.update(status='pending')
        self.message_user(request, f'⏳ تم تحديد {count} دفعة كمعلقة')
    
    @admin.action(description=_('⌛ تحديد كجزئية'))
    def mark_as_partial(self, request, queryset):
        """إجراء: تحديد كجزئية"""
        count = queryset.filter(
            amount_paid__gt=0, amount_remaining__gt=0
        ).update(status='partial')
        self.message_user(request, f'⌛ تم تحديد {count} دفعة كجزئية')
    
    @admin.action(description=_('📄 إنشاء فواتير'))
    def generate_invoices(self, request, queryset):
        """إجراء: إنشاء فواتير"""
        count = 0
        for payment in queryset:
            if not hasattr(payment, 'invoice'):
                Invoice.objects.create(
                    payment=payment,
                    subtotal=payment.amount,
                    discount=payment.discount,
                    tax=payment.tax,
                    total=payment.total,
                    is_paid=payment.status == Payment.PaymentStatus.COMPLETED
                )
                count += 1
        
        self.message_user(request, f'📄 تم إنشاء {count} فاتورة')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """لوحة إدارة الفواتير والإيصالات"""
    
    list_display = [
        'invoice_number', 'get_member_info', 'total',
        'get_paid_status', 'issued_date', 'get_date_info'
    ]
    list_filter = [
        'is_paid', 'issued_date',
        ('payment__status', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'invoice_number', 'payment__member__user__phone',
        'payment__member__user__first_name', 'payment__member__user__last_name'
    ]
    readonly_fields = [
        'invoice_number', 'issued_date', 'created_at',
        'get_payment_link', 'get_invoice_preview'
    ]
    ordering = ['-issued_date']
    date_hierarchy = 'issued_date'
    
    fieldsets = (
        (_('معلومات الفاتورة'), {
            'fields': ('invoice_number', 'payment', 'total', 'is_paid')
        }),
        (_('معلومات العضو'), {
            'fields': ('get_payment_link',)
        }),
        (_('التواريخ'), {
            'fields': ('issued_date', 'created_at')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_info(self, obj):
        """معلومات العضو"""
        member = obj.payment.member
        member_name = member.user.get_full_name()
        member_id = member.member_id
        
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            member_name, member_id
        )
    get_member_info.short_description = _('العضو')
    get_member_info.admin_order_field = 'payment__member__user__first_name'
    
    def get_paid_status(self, obj):
        """حالة الدفع"""
        if obj.is_paid:
            return format_html(
                '<span style="background-color: #198754; color: white; '
                'padding: 4px 12px; border-radius: 15px; font-weight: bold;">✓ مدفوعة</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 4px 12px; border-radius: 15px; font-weight: bold;">✗ غير مدفوعة</span>'
        )
    get_paid_status.short_description = _('الحالة')
    
    def get_date_info(self, obj):
        """معلومات التاريخ"""
        days_ago = (timezone.now().date() - obj.issued_date).days
        
        if days_ago == 0:
            return format_html('<span style="color: #0d6efd; font-weight: bold;">اليوم</span>')
        elif days_ago == 1:
            return format_html('<span style="color: #0dcaf0;">أمس</span>')
        elif days_ago < 7:
            return format_html('<span style="color: #6c757d;">{} أيام</span>', days_ago)
        
        return obj.issued_date.strftime('%d-%m-%Y')
    get_date_info.short_description = _('التاريخ')
    
    def get_payment_link(self, obj):
        """رابط إلى الدفعة"""
        url = reverse('admin:payments_payment_change', args=[obj.payment.id])
        return format_html(
            '<a href="{}" target="_blank">عرض الدفعة: {}</a>',
            url, obj.payment.payment_number
        )
    get_payment_link.short_description = _('الدفعة')
    
    def get_invoice_preview(self, obj):
        """معاينة الفاتورة"""
        return format_html(
            '<strong>الفاتورة رقم:</strong> {}<br/>'
            '<strong>المبلغ:</strong> {} ر.س<br/>'
            '<strong>الحالة:</strong> {}<br/>',
            obj.invoice_number,
            obj.total,
            'مدفوعة ✓' if obj.is_paid else 'معلقة'
        )
    get_invoice_preview.short_description = _('معاينة الفاتورة')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'payment__member__user'
        )


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    """لوحة إدارة الأقساط والدفعات المقسطة"""
    
    list_display = [
        'installment_number', 'get_payment_info', 'amount',
        'get_due_date_badge', 'get_paid_status', 'paid_date'
    ]
    list_filter = [
        'is_paid', 'due_date',
        ('payment__member', admin.RelatedFieldListFilter)
    ]
    search_fields = [
        'payment__payment_number',
        'payment__member__user__phone',
        'installment_number'
    ]
    readonly_fields = ['installment_number', 'created_at']
    ordering = ['-due_date']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        (_('معلومات القسط'), {
            'fields': ('installment_number', 'payment', 'amount')
        }),
        (_('التواريخ'), {
            'fields': ('due_date', 'paid_date', 'is_paid')
        }),
        (_('ملاحظات'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_payment_info(self, obj):
        """معلومات الدفعة"""
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.payment.payment_number,
            obj.payment.member.user.get_full_name()
        )
    get_payment_info.short_description = _('الدفعة/العضو')
    
    def get_due_date_badge(self, obj):
        """شارة تاريخ الاستحقاق"""
        today = timezone.now().date()
        days_diff = (obj.due_date - today).days
        
        if days_diff < 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 10px; font-weight: bold;">'
                'متأخر {} أيام</span>',
                abs(days_diff)
            )
        elif days_diff == 0:
            return format_html(
                '<span style="background-color: #ffc107; color: white; '
                'padding: 3px 10px; border-radius: 10px; font-weight: bold;">اليوم</span>'
            )
        elif days_diff <= 7:
            return format_html(
                '<span style="background-color: #ffc107; color: white; '
                'padding: 3px 10px; border-radius: 10px; font-weight: bold;">'
                'متبقي {} أيام</span>',
                days_diff
            )
        
        return obj.due_date.strftime('%d-%m-%Y')
    get_due_date_badge.short_description = _('الاستحقاق')
    
    def get_paid_status(self, obj):
        """حالة الدفع"""
        if obj.is_paid:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ مدفوع</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ غير مدفوع</span>'
        )
    get_paid_status.short_description = _('الحالة')
    
    def get_queryset(self, request):
        """تحسين الـ Query"""
        return super().get_queryset(request).select_related(
            'payment__member__user'
        )
    
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    @admin.action(description=_('✓ تحديد كمدفوع'))
    def mark_as_paid(self, request, queryset):
        """إجراء: تحديد كمدفوع"""
        count = queryset.filter(is_paid=False).update(
            is_paid=True,
            paid_date=timezone.now()
        )
        self.message_user(request, f'✓ تم تحديد {count} قسط كمدفوع')
    
    @admin.action(description=_('✗ تحديد كغير مدفوع'))
    def mark_as_unpaid(self, request, queryset):
        """إجراء: تحديد كغير مدفوع"""
        count = queryset.filter(is_paid=True).update(
            is_paid=False,
            paid_date=None
        )
        self.message_user(request, f'✗ تم تحديد {count} قسط كغير مدفوع')
