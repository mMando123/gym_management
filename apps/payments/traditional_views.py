from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from apps.payments.models import Payment, Invoice, InstallmentPlan
from apps.members.models import Member
from .forms import PaymentForm, PaymentSearchForm, InvoiceForm, InstallmentPlanForm


@login_required(login_url='login')
def payment_list(request):
    """عرض قائمة المدفوعات مع الفلترة والبحث"""
    payments = Payment.objects.select_related('member__user').all().order_by('-created_at')
    
    # البحث والفلترة
    search = request.GET.get('search', '')
    member_id = request.GET.get('member', '')
    payment_method = request.GET.get('payment_method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search:
        payments = payments.filter(
            Q(member__user__first_name__icontains=search) |
            Q(member__user__last_name__icontains=search)
        )
    
    if member_id:
        payments = payments.filter(member_id=member_id)
    
    if payment_method:
        payments = payments.filter(payment_method=payment_method)
    
    if date_from:
        payments = payments.filter(created_at__date__gte=date_from)
    
    if date_to:
        payments = payments.filter(created_at__date__lte=date_to)
    
    # الإحصائيات
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # التصفح
    paginator = Paginator(payments, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    form = PaymentSearchForm(request.GET)
    
    context = {
        'payments': page_obj,
        'form': form,
        'total_count': paginator.count,
        'total_amount': total_amount
    }
    
    return render(request, 'payments/list.html', context)


@login_required(login_url='login')
def payment_create(request):
    """إضافة دفعة جديدة"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, 'تم تسجيل الدفعة بنجاح')
            return redirect('payments:detail', pk=payment.pk)
    else:
        form = PaymentForm()
    
    context = {'form': form}
    return render(request, 'payments/form.html', context)


@login_required(login_url='login')
def payment_detail(request, pk):
    """عرض تفاصيل دفعة"""
    payment = get_object_or_404(
        Payment.objects.select_related('member__user'),
        pk=pk
    )
    
    context = {'payment': payment}
    return render(request, 'payments/detail.html', context)


@login_required(login_url='login')
def invoice_list(request):
    """عرض قائمة الفواتير"""
    invoices = Invoice.objects.select_related('member__user').all().order_by('-issue_date')
    
    # الفلترة
    member_id = request.GET.get('member', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    
    if member_id:
        invoices = invoices.filter(member_id=member_id)
    
    if status:
        invoices = invoices.filter(status=status)
    
    if date_from:
        invoices = invoices.filter(issue_date__gte=date_from)
    
    # التصفح
    paginator = Paginator(invoices, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'invoices': page_obj,
        'total_count': paginator.count
    }
    
    return render(request, 'payments/invoice_list.html', context)


@login_required(login_url='login')
def invoice_create(request):
    """إنشاء فاتورة جديدة"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, 'تم إنشاء الفاتورة بنجاح')
            return redirect('payments:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    
    context = {'form': form}
    return render(request, 'payments/invoice_form.html', context)


@login_required(login_url='login')
def invoice_detail(request, pk):
    """عرض تفاصيل الفاتورة"""
    invoice = get_object_or_404(
        Invoice.objects.select_related('member__user'),
        pk=pk
    )
    
    context = {'invoice': invoice}
    return render(request, 'payments/invoice_detail.html', context)


@login_required(login_url='login')
def installment_list(request):
    """عرض قائمة خطط التقسيط"""
    installments = InstallmentPlan.objects.select_related('member__user').all().order_by('-start_date')
    
    # الفلترة
    member_id = request.GET.get('member', '')
    status = request.GET.get('status', '')
    
    if member_id:
        installments = installments.filter(member_id=member_id)
    
    if status:
        installments = installments.filter(status=status)
    
    # التصفح
    paginator = Paginator(installments, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'installments': page_obj,
        'total_count': paginator.count
    }
    
    return render(request, 'payments/installment_list.html', context)


@login_required(login_url='login')
def installment_create(request):
    """إنشاء خطة تقسيط"""
    if request.method == 'POST':
        form = InstallmentPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, 'تم إنشاء خطة التقسيط بنجاح')
            return redirect('payments:installment_detail', pk=plan.pk)
    else:
        form = InstallmentPlanForm()
    
    context = {'form': form}
    return render(request, 'payments/installment_form.html', context)


@login_required(login_url='login')
def installment_detail(request, pk):
    """عرض تفاصيل خطة التقسيط"""
    installment = get_object_or_404(
        InstallmentPlan.objects.select_related('member__user'),
        pk=pk
    )
    
    # الأقساط المرتبطة
    from apps.payments.models import Installment
    installment_items = Installment.objects.filter(plan=installment).order_by('due_date')
    
    context = {
        'installment': installment,
        'installment_items': installment_items
    }
    
    return render(request, 'payments/installment_detail.html', context)


@login_required(login_url='login')
def payment_stats(request):
    """إحصائيات المدفوعات"""
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    # حساب الفترة الزمنية
    if period == 'week':
        date_from = today - timedelta(days=7)
    elif period == 'year':
        date_from = today - timedelta(days=365)
    else:  # month
        date_from = today - timedelta(days=30)
    
    # الاستعلام
    payments = Payment.objects.filter(
        created_at__date__gte=date_from
    )
    
    # الإحصائيات
    stats = {
        'total_revenue': payments.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_payments': payments.count(),
        'average_payment': 0,
        'by_method': {}
    }
    
    if stats['total_payments'] > 0:
        stats['average_payment'] = stats['total_revenue'] / stats['total_payments']
    
    # توزيع الدفعات
    by_method = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    for item in by_method:
        stats['by_method'][item['payment_method']] = {
            'total': item['total'],
            'count': item['count']
        }
    
    context = {
        'stats': stats,
        'period': period
    }
    
    return render(request, 'payments/stats.html', context)


@login_required(login_url='login')
@require_http_methods(['GET'])
def member_payments_api(request, member_id):
    """بيانات المدفوعات للعضو - AJAX"""
    try:
        member = Member.objects.get(pk=member_id)
        
        payments = Payment.objects.filter(member=member)
        total = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        data = {
            'success': True,
            'member_name': f"{member.user.first_name} {member.user.last_name}",
            'total_payments': payments.count(),
            'total_amount': float(total),
            'last_payment': str(payments.last().created_at) if payments.exists() else None
        }
    except Member.DoesNotExist:
        data = {'success': False, 'error': 'العضو غير موجود'}
    
    return JsonResponse(data)
