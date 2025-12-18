from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone

from apps.trainers.models import Trainer, TrainerAvailability, Specialization, Session
from apps.members.models import Member
from .forms import (
    TrainerForm, TrainerAvailabilityForm, TrainerSearchForm, SessionBookingForm
)


@login_required(login_url='login')
def trainer_list(request):
    """عرض قائمة المدربين مع البحث والفلترة"""
    trainers = Trainer.objects.select_related('user').prefetch_related(
        'specialization'
    ).all().order_by('user__first_name')
    
    # البحث والفلترة
    search = request.GET.get('search', '')
    specialization = request.GET.get('specialization', '')
    
    if search:
        trainers = trainers.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if specialization:
        trainers = trainers.filter(specialization__id=specialization)
    
    # التصفح
    paginator = Paginator(trainers, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    form = TrainerSearchForm(request.GET)
    
    context = {
        'trainers': page_obj,
        'form': form,
        'total_count': paginator.count
    }
    
    return render(request, 'trainers/list.html', context)


@login_required(login_url='login')
def trainer_detail(request, pk):
    """عرض تفاصيل المدرب"""
    trainer = get_object_or_404(
        Trainer.objects.select_related('user').prefetch_related(
            'specialization', 'availability_set', 'session_set'
        ),
        pk=pk
    )
    
    # الإحصائيات
    total_sessions = trainer.session_set.count()
    this_month_sessions = trainer.session_set.filter(
        date__month=timezone.now().month,
        date__year=timezone.now().year
    ).count()
    
    # ساعات العمل
    availability = trainer.availability_set.all().order_by('day_of_week', 'start_time')
    
    context = {
        'trainer': trainer,
        'total_sessions': total_sessions,
        'this_month_sessions': this_month_sessions,
        'availability': availability
    }
    
    return render(request, 'trainers/detail.html', context)


@login_required(login_url='login')
def trainer_create(request):
    """إضافة مدرب جديد"""
    if request.method == 'POST':
        form = TrainerForm(request.POST)
        if form.is_valid():
            trainer = form.save()
            messages.success(request, 'تم إضافة المدرب بنجاح')
            return redirect('trainers:detail', pk=trainer.pk)
    else:
        form = TrainerForm()
    
    context = {'form': form}
    return render(request, 'trainers/form.html', context)


@login_required(login_url='login')
def trainer_edit(request, pk):
    """تعديل بيانات المدرب"""
    trainer = get_object_or_404(Trainer, pk=pk)
    
    if request.method == 'POST':
        form = TrainerForm(request.POST, instance=trainer)
        if form.is_valid():
            trainer = form.save()
            messages.success(request, 'تم تحديث بيانات المدرب بنجاح')
            return redirect('trainers:detail', pk=trainer.pk)
    else:
        form = TrainerForm(instance=trainer)
    
    context = {'form': form, 'trainer': trainer}
    return render(request, 'trainers/form.html', context)


@login_required(login_url='login')
def trainer_delete(request, pk):
    """حذف مدرب"""
    trainer = get_object_or_404(Trainer, pk=pk)
    
    if request.method == 'POST':
        trainer.delete()
        messages.success(request, 'تم حذف المدرب بنجاح')
        return redirect('trainers:list')
    
    context = {'trainer': trainer}
    return render(request, 'trainers/delete_confirm.html', context)


@login_required(login_url='login')
def availability_list(request, trainer_pk):
    """عرض ساعات عمل المدرب"""
    trainer = get_object_or_404(Trainer, pk=trainer_pk)
    availability = trainer.availability_set.all().order_by('day_of_week', 'start_time')
    
    context = {
        'trainer': trainer,
        'availability': availability
    }
    
    return render(request, 'trainers/availability.html', context)


@login_required(login_url='login')
def availability_create(request, trainer_pk):
    """إضافة ساعات عمل للمدرب"""
    trainer = get_object_or_404(Trainer, pk=trainer_pk)
    
    if request.method == 'POST':
        form = TrainerAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.trainer = trainer
            availability.save()
            messages.success(request, 'تم إضافة ساعات العمل بنجاح')
            return redirect('trainers:availability_list', trainer_pk=trainer.pk)
    else:
        form = TrainerAvailabilityForm(initial={'trainer': trainer})
    
    context = {'form': form, 'trainer': trainer}
    return render(request, 'trainers/availability_form.html', context)


@login_required(login_url='login')
def availability_delete(request, pk):
    """حذف ساعات عمل"""
    availability = get_object_or_404(TrainerAvailability, pk=pk)
    trainer = availability.trainer
    
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'تم حذف ساعات العمل بنجاح')
        return redirect('trainers:availability_list', trainer_pk=trainer.pk)
    
    context = {'availability': availability}
    return render(request, 'trainers/availability_delete.html', context)


@login_required(login_url='login')
def session_list(request, trainer_pk):
    """عرض جلسات التدريب للمدرب"""
    trainer = get_object_or_404(Trainer, pk=trainer_pk)
    sessions = trainer.session_set.select_related('member__user').all().order_by('-date')
    
    # الفلترة
    status = request.GET.get('status', '')
    if status:
        sessions = sessions.filter(status=status)
    
    # التصفح
    paginator = Paginator(sessions, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'trainer': trainer,
        'sessions': page_obj,
        'total_count': paginator.count
    }
    
    return render(request, 'trainers/session_list.html', context)


@login_required(login_url='login')
def session_book(request, trainer_pk):
    """حجز جلسة تدريب"""
    trainer = get_object_or_404(Trainer, pk=trainer_pk)
    
    if request.method == 'POST':
        form = SessionBookingForm(request.POST)
        if form.is_valid():
            session = Session.objects.create(
                trainer=form.cleaned_data['trainer'],
                member=request.user.member if hasattr(request.user, 'member') else None,
                date=form.cleaned_data['session_date'],
                time=form.cleaned_data['session_time'],
                duration=form.cleaned_data['duration'],
                notes=form.cleaned_data.get('notes', '')
            )
            messages.success(request, 'تم حجز الجلسة بنجاح')
            return redirect('trainers:detail', pk=trainer.pk)
    else:
        form = SessionBookingForm(initial={'trainer': trainer})
    
    context = {'form': form, 'trainer': trainer}
    return render(request, 'trainers/session_book.html', context)


@login_required(login_url='login')
@require_http_methods(['GET'])
def trainer_availability_api(request, trainer_id):
    """ساعات عمل المدرب - AJAX"""
    try:
        trainer = Trainer.objects.get(pk=trainer_id)
        
        availability = trainer.availability_set.all().values(
            'day_of_week', 'start_time', 'end_time'
        )
        
        data = {
            'success': True,
            'trainer_name': f"{trainer.user.first_name} {trainer.user.last_name}",
            'availability': list(availability),
            'hourly_rate': float(trainer.hourly_rate)
        }
    except Trainer.DoesNotExist:
        data = {'success': False, 'error': 'المدرب غير موجود'}
    
    return JsonResponse(data)
