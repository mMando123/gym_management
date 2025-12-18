from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from datetime import date, timedelta

from .models import Member, MemberBodyMetrics
from .forms import MemberForm, MemberBodyMetricsForm, UserProfileForm, MemberSearchForm
from apps.subscriptions.models import Subscription
from apps.attendance.models import Attendance
from apps.payments.models import Payment


@login_required(login_url='login')
def member_list(request):
    """قائمة الأعضاء مع الفلترة والبحث"""
    
    members = Member.objects.select_related('user').all().order_by('-created_at')
    form = MemberSearchForm(request.GET)
    
    # البحث
    search = request.GET.get('search', '')
    if search:
        members = members.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__phone__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # الفلترة حسب النوع
    gender = request.GET.get('gender', '')
    if gender:
        members = members.filter(gender=gender)
    
    # الفلترة حسب الحالة
    status = request.GET.get('status', '')
    if status == 'active':
        members = members.filter(is_active=True)
    elif status == 'inactive':
        members = members.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(members, 15)
    page = request.GET.get('page', 1)
    
    try:
        members_page = paginator.page(page)
    except PageNotAnInteger:
        members_page = paginator.page(1)
    except EmptyPage:
        members_page = paginator.page(paginator.num_pages)
    
    context = {
        'members': members_page,
        'page_obj': members_page,
        'form': form,
        'total_count': Member.objects.count(),
        'active_count': Member.objects.filter(is_active=True).count(),
        'inactive_count': Member.objects.filter(is_active=False).count(),
        'search': search,
    }
    
    return render(request, 'members/list.html', context)


@login_required(login_url='login')
def member_detail(request, pk):
    """تفاصيل العضو"""
    
    member = get_object_or_404(Member, pk=pk)
    
    # آخر القياسات
    latest_metrics = member.body_metrics.order_by('-date').first()
    
    # الاشتراكات النشطة
    active_subscriptions = member.subscriptions.filter(
        status='ACTIVE',
        end_date__gte=timezone.now().date()
    )
    
    # سجل الحضور (آخر 10 جلسات)
    recent_attendance = member.attendance_set.order_by('-date')[:10]
    
    # إحصائيات
    stats = {
        'total_visits': member.attendance_set.count(),
        'this_month': member.attendance_set.filter(
            date__month=timezone.now().month,
            date__year=timezone.now().year
        ).count(),
        'total_paid': Payment.objects.filter(
            member=member,
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # الأعضاء الجدد (لتوصيات)
    friend_visits = member.guest_visits.all()
    
    context = {
        'member': member,
        'latest_metrics': latest_metrics,
        'active_subscriptions': active_subscriptions,
        'recent_attendance': recent_attendance,
        'stats': stats,
        'friend_visits': friend_visits,
    }
    
    return render(request, 'members/detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def member_create(request):
    """إضافة عضو جديد"""
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        user_form = UserProfileForm(request.POST)
        
        if form.is_valid() and user_form.is_valid():
            try:
                # الحصول على المستخدم من session أو إنشاء واحد جديد
                # هنا نفترض أن لديك طريقة للمستخدم
                member = form.save(commit=False)
                
                # ربط المستخدم (قد تحتاج لتعديل حسب تطبيقك)
                if hasattr(request, 'user') and request.user.is_authenticated:
                    member.user = request.user
                
                member.save()
                
                messages.success(request, f'تم إضافة العضو {member.user.get_full_name()} بنجاح!')
                return redirect('member_detail', pk=member.pk)
            
            except Exception as e:
                messages.error(request, f'حدث خطأ: {str(e)}')
    else:
        form = MemberForm()
        user_form = UserProfileForm()
    
    context = {
        'form': form,
        'user_form': user_form,
        'title': 'إضافة عضو جديد',
    }
    
    return render(request, 'members/form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def member_edit(request, pk):
    """تعديل بيانات العضو"""
    
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        user_form = UserProfileForm(request.POST, instance=member.user)
        
        if form.is_valid() and user_form.is_valid():
            try:
                form.save()
                user_form.save()
                messages.success(request, 'تم تحديث بيانات العضو بنجاح!')
                return redirect('member_detail', pk=member.pk)
            except Exception as e:
                messages.error(request, f'حدث خطأ: {str(e)}')
    else:
        form = MemberForm(instance=member)
        user_form = UserProfileForm(instance=member.user)
    
    context = {
        'form': form,
        'user_form': user_form,
        'member': member,
        'title': f'تعديل بيانات {member.user.get_full_name()}',
    }
    
    return render(request, 'members/form.html', context)


@login_required(login_url='login')
def member_delete(request, pk):
    """حذف العضو"""
    
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        try:
            name = member.user.get_full_name()
            member.delete()
            messages.success(request, f'تم حذف العضو {name} بنجاح!')
            return redirect('member_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    context = {'member': member}
    return render(request, 'members/delete_confirm.html', context)


@login_required(login_url='login')
def member_metrics(request, pk):
    """قياسات جسم العضو"""
    
    member = get_object_or_404(Member, pk=pk)
    metrics = member.body_metrics.order_by('-date')
    
    # Pagination
    paginator = Paginator(metrics, 10)
    page = request.GET.get('page', 1)
    
    try:
        metrics_page = paginator.page(page)
    except PageNotAnInteger:
        metrics_page = paginator.page(1)
    except EmptyPage:
        metrics_page = paginator.page(paginator.num_pages)
    
    context = {
        'member': member,
        'metrics': metrics_page,
    }
    
    return render(request, 'members/metrics.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def member_metrics_add(request, pk):
    """إضافة قياسات جديدة"""
    
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberBodyMetricsForm(request.POST)
        
        if form.is_valid():
            try:
                metrics = form.save(commit=False)
                metrics.member = member
                metrics.date = timezone.now().date()
                metrics.save()
                
                messages.success(request, 'تم تسجيل القياسات بنجاح!')
                return redirect('member_metrics', pk=member.pk)
            except Exception as e:
                messages.error(request, f'حدث خطأ: {str(e)}')
    else:
        form = MemberBodyMetricsForm()
    
    context = {
        'member': member,
        'form': form,
        'title': 'إضافة قياسات جديدة',
    }
    
    return render(request, 'members/metrics_form.html', context)


@login_required(login_url='login')
def member_attendance(request, pk):
    """سجل الحضور"""
    
    member = get_object_or_404(Member, pk=pk)
    attendance = member.attendance_set.select_related('sport').order_by('-date')
    
    # الفلترة
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if from_date:
        attendance = attendance.filter(date__gte=from_date)
    if to_date:
        attendance = attendance.filter(date__lte=to_date)
    
    # Pagination
    paginator = Paginator(attendance, 20)
    page = request.GET.get('page', 1)
    
    try:
        attendance_page = paginator.page(page)
    except PageNotAnInteger:
        attendance_page = paginator.page(1)
    except EmptyPage:
        attendance_page = paginator.page(paginator.num_pages)
    
    context = {
        'member': member,
        'attendance': attendance_page,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'members/attendance.html', context)


@login_required(login_url='login')
def member_subscriptions(request, pk):
    """الاشتراكات"""
    
    member = get_object_or_404(Member, pk=pk)
    subscriptions = member.subscriptions.order_by('-start_date')
    
    context = {
        'member': member,
        'subscriptions': subscriptions,
        'active_subscriptions': subscriptions.filter(status='ACTIVE'),
        'expired_subscriptions': subscriptions.filter(status='EXPIRED'),
    }
    
    return render(request, 'members/subscriptions.html', context)


@login_required(login_url='login')
def member_payments(request, pk):
    """سجل الدفعات"""
    
    member = get_object_or_404(Member, pk=pk)
    payments = member.payments.order_by('-created_at')
    
    context = {
        'member': member,
        'payments': payments,
        'total_paid': payments.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0,
        'total_pending': payments.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    return render(request, 'members/payments.html', context)


# AJAX Endpoints

@login_required(login_url='login')
def member_quick_info(request, pk):
    """معلومات سريعة عن العضو (AJAX)"""
    
    member = get_object_or_404(Member, pk=pk)
    
    active_subscription = member.subscriptions.filter(
        status='ACTIVE',
        end_date__gte=timezone.now().date()
    ).first()
    
    data = {
        'id': member.pk,
        'name': member.user.get_full_name(),
        'phone': member.user.phone,
        'age': member.age,
        'has_active_subscription': bool(active_subscription),
        'subscription_end_date': active_subscription.end_date.isoformat() if active_subscription else None,
    }
    
    return JsonResponse(data)


@login_required(login_url='login')
def member_search(request):
    """البحث السريع (AJAX)"""
    
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    members = Member.objects.select_related('user').filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__phone__icontains=query)
    )[:10]
    
    results = [
        {
            'id': m.pk,
            'name': m.user.get_full_name(),
            'phone': m.user.phone,
            'url': f'/members/{m.pk}/'
        }
        for m in members
    ]
    
    return JsonResponse({'results': results})
