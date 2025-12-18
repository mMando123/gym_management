from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from apps.attendance.models import Attendance
from apps.members.models import Member
from .forms import AttendanceCheckInForm, AttendanceSearchForm, AttendanceStatsForm


@login_required(login_url='login')
def attendance_list(request):
    """عرض سجل الحضور مع الفلترة والبحث"""
    attendances = Attendance.objects.select_related('member__user').all().order_by('-check_in_time')
    
    # البحث والفلترة
    search = request.GET.get('search', '')
    member_id = request.GET.get('member', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search:
        attendances = attendances.filter(
            Q(member__user__first_name__icontains=search) |
            Q(member__user__last_name__icontains=search) |
            Q(member__user__email__icontains=search)
        )
    
    if member_id:
        attendances = attendances.filter(member_id=member_id)
    
    if date_from:
        attendances = attendances.filter(check_in_time__date__gte=date_from)
    
    if date_to:
        attendances = attendances.filter(check_in_time__date__lte=date_to)
    
    # التصفح
    paginator = Paginator(attendances, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    form = AttendanceSearchForm(request.GET)
    
    context = {
        'attendances': page_obj,
        'form': form,
        'total_count': paginator.count
    }
    
    return render(request, 'attendance/list.html', context)


@login_required(login_url='login')
def attendance_check_in(request):
    """تسجيل حضور جديد"""
    if request.method == 'POST':
        form = AttendanceCheckInForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            
            # التحقق من وجود check-out قبل check-in
            last_attendance = Attendance.objects.filter(
                member=member
            ).exclude(check_out_time__isnull=True).last()
            
            # إنشاء سجل حضور جديد
            attendance = Attendance.objects.create(
                member=member,
                check_in_time=timezone.now()
            )
            
            messages.success(request, f'تم تسجيل حضور {member.user.first_name} بنجاح')
            return redirect('attendance:list')
    else:
        form = AttendanceCheckInForm()
    
    context = {'form': form}
    return render(request, 'attendance/check_in.html', context)


@login_required(login_url='login')
def attendance_check_out(request, pk):
    """تسجيل خروج العضو"""
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if attendance.check_out_time is None:
        attendance.check_out_time = timezone.now()
        attendance.save()
        messages.success(request, 'تم تسجيل الخروج بنجاح')
    else:
        messages.warning(request, 'تم تسجيل الخروج مسبقاً')
    
    return redirect('attendance:list')


@login_required(login_url='login')
def attendance_detail(request, pk):
    """عرض تفاصيل سجل حضور"""
    attendance = get_object_or_404(
        Attendance.objects.select_related('member__user'),
        pk=pk
    )
    
    # الإحصائيات
    member = attendance.member
    total_sessions = Attendance.objects.filter(member=member).count()
    this_month = Attendance.objects.filter(
        member=member,
        check_in_time__month=timezone.now().month,
        check_in_time__year=timezone.now().year
    ).count()
    
    context = {
        'attendance': attendance,
        'total_sessions': total_sessions,
        'this_month': this_month
    }
    
    return render(request, 'attendance/detail.html', context)


@login_required(login_url='login')
def attendance_stats(request):
    """عرض إحصائيات الحضور"""
    form = AttendanceStatsForm(request.GET)
    period = request.GET.get('period', 'month')
    member_id = request.GET.get('member', '')
    
    # حساب الفترة الزمنية
    today = timezone.now().date()
    
    if period == 'week':
        date_from = today - timedelta(days=7)
    elif period == 'year':
        date_from = today - timedelta(days=365)
    else:  # month
        date_from = today - timedelta(days=30)
    
    # الاستعلام
    query = Attendance.objects.filter(
        check_in_time__date__gte=date_from
    ).select_related('member__user')
    
    if member_id:
        query = query.filter(member_id=member_id)
    
    # الإحصائيات
    stats = {
        'total_sessions': query.count(),
        'unique_members': query.values('member').distinct().count(),
        'average_per_day': query.count() // max((today - date_from).days, 1),
        'busiest_day': None,
        'peak_hours': {}
    }
    
    # أكثر يوم ازدحاماً
    from django.db.models.functions import TruncDate
    busiest = query.annotate(
        date=TruncDate('check_in_time')
    ).values('date').annotate(count=Count('id')).order_by('-count').first()
    
    if busiest:
        stats['busiest_day'] = busiest['date']
    
    context = {
        'form': form,
        'stats': stats,
        'period': period
    }
    
    return render(request, 'attendance/stats.html', context)


@login_required(login_url='login')
@require_http_methods(['GET'])
def attendance_quick_info(request, member_id):
    """معلومات سريعة عن حضور العضو - AJAX"""
    try:
        member = Member.objects.get(pk=member_id)
        
        today = timezone.now().date()
        
        # هل تم التسجيل اليوم؟
        today_attendance = Attendance.objects.filter(
            member=member,
            check_in_time__date=today
        ).first()
        
        # الإحصائيات
        this_month = Attendance.objects.filter(
            member=member,
            check_in_time__month=today.month,
            check_in_time__year=today.year
        ).count()
        
        data = {
            'success': True,
            'member_name': f"{member.user.first_name} {member.user.last_name}",
            'today_checked_in': today_attendance is not None,
            'this_month_sessions': this_month,
            'check_in_time': today_attendance.check_in_time.isoformat() if today_attendance else None,
            'is_checked_out': today_attendance.check_out_time is not None if today_attendance else False
        }
    except Member.DoesNotExist:
        data = {'success': False, 'error': 'العضو غير موجود'}
    
    return JsonResponse(data)
