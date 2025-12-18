from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Locker, LockerRental
from .forms import LockerForm, LockerRentalForm, QuickRentalForm


@login_required
def locker_list(request):
    lockers = Locker.objects.all()
    search = request.GET.get('search', '')
    if search:
        lockers = lockers.filter(
            Q(locker_number__icontains=search) |
            Q(location__icontains=search)
        )
    status = request.GET.get('status', '')
    if status:
        lockers = lockers.filter(status=status)
    size = request.GET.get('size', '')
    if size:
        lockers = lockers.filter(size=size)
    stats = {
        'total': Locker.objects.count(),
        'available': Locker.objects.filter(status=Locker.Status.AVAILABLE).count(),
        'occupied': Locker.objects.filter(status=Locker.Status.OCCUPIED).count(),
        'maintenance': Locker.objects.filter(status=Locker.Status.MAINTENANCE).count(),
    }
    paginator = Paginator(lockers, 12)
    page = request.GET.get('page')
    lockers = paginator.get_page(page)
    context = {
        'lockers': lockers,
        'stats': stats,
        'search': search,
        'current_status': status,
        'current_size': size,
        'status_choices': Locker.Status.choices,
        'size_choices': Locker.Size.choices,
    }
    return render(request, 'lockers/locker_list.html', context)


@login_required
def locker_detail(request, pk):
    locker = get_object_or_404(Locker, pk=pk)
    rentals = locker.rentals.all()[:10]
    context = {
        'locker': locker,
        'rentals': rentals,
    }
    return render(request, 'lockers/locker_detail.html', context)


@login_required
def locker_create(request):
    if request.method == 'POST':
        form = LockerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الخزانة بنجاح')
            return redirect('lockers:locker_list')
    else:
        form = LockerForm()
    return render(request, 'lockers/locker_form.html', {'form': form, 'title': 'إضافة خزانة جديدة'})


@login_required
def locker_update(request, pk):
    locker = get_object_or_404(Locker, pk=pk)
    if request.method == 'POST':
        form = LockerForm(request.POST, instance=locker)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الخزانة بنجاح')
            return redirect('lockers:locker_detail', pk=pk)
    else:
        form = LockerForm(instance=locker)
    return render(request, 'lockers/locker_form.html', {'form': form, 'title': 'تعديل الخزانة', 'locker': locker})


@login_required
def locker_delete(request, pk):
    locker = get_object_or_404(Locker, pk=pk)
    if request.method == 'POST':
        locker.delete()
        messages.success(request, 'تم حذف الخزانة بنجاح')
        return redirect('lockers:locker_list')
    return render(request, 'lockers/locker_confirm_delete.html', {'locker': locker})


@login_required
def rental_list(request):
    rentals = LockerRental.objects.select_related('locker', 'member').all()
    search = request.GET.get('search', '')
    if search:
        rentals = rentals.filter(
            Q(locker__locker_number__icontains=search) |
            Q(member__name__icontains=search)
        )
    status = request.GET.get('status', '')
    if status == 'active':
        rentals = rentals.filter(is_active=True)
    elif status == 'expired':
        today = timezone.now().date()
        rentals = rentals.filter(end_date__lt=today)
    elif status == 'expiring':
        today = timezone.now().date()
        week_later = today + timedelta(days=7)
        rentals = rentals.filter(end_date__gte=today, end_date__lte=week_later)
    paginator = Paginator(rentals, 20)
    page = request.GET.get('page')
    rentals = paginator.get_page(page)
    context = {
        'rentals': rentals,
        'search': search,
        'current_status': status,
    }
    return render(request, 'lockers/rental_list.html', context)


@login_required
def rental_create(request):
    if request.method == 'POST':
        form = LockerRentalForm(request.POST)
        if form.is_valid():
            rental = form.save()
            rental.locker.status = Locker.Status.OCCUPIED
            rental.locker.save()
            messages.success(request, 'تم تسجيل الإيجار بنجاح')
            return redirect('lockers:rental_list')
    else:
        form = LockerRentalForm()
    return render(request, 'lockers/rental_form.html', {'form': form, 'title': 'تسجيل إيجار جديد'})


@login_required
def rental_detail(request, pk):
    rental = get_object_or_404(LockerRental.objects.select_related('locker', 'member'), pk=pk)
    return render(request, 'lockers/rental_detail.html', {'rental': rental})


@login_required
def rental_end(request, pk):
    rental = get_object_or_404(LockerRental, pk=pk)
    if request.method == 'POST':
        rental.is_active = False
        rental.save()
        rental.locker.status = Locker.Status.AVAILABLE
        rental.locker.save()
        messages.success(request, 'تم إنهاء الإيجار بنجاح')
        return redirect('lockers:rental_list')
    return render(request, 'lockers/rental_end_confirm.html', {'rental': rental})


@login_required
def quick_rent(request, locker_pk):
    locker = get_object_or_404(Locker, pk=locker_pk)
    if not locker.is_available:
        messages.error(request, 'هذه الخزانة غير متاحة للإيجار')
        return redirect('lockers:locker_detail', pk=locker_pk)
    if request.method == 'POST':
        form = QuickRentalForm(request.POST)
        if form.is_valid():
            rental_type = form.cleaned_data['rental_type']
            start_date = form.cleaned_data['start_date']
            if rental_type == LockerRental.RentalType.DAILY:
                end_date = start_date + timedelta(days=1)
                price = locker.daily_rate
            else:
                end_date = start_date + timedelta(days=30)
                price = locker.monthly_rate
            rental = LockerRental.objects.create(
                locker=locker,
                member=form.cleaned_data['member'],
                rental_type=rental_type,
                start_date=start_date,
                end_date=end_date,
                price=price
            )
            locker.status = Locker.Status.OCCUPIED
            locker.save()
            messages.success(request, f'تم تأجير الخزانة {locker.locker_number} بنجاح')
            return redirect('lockers:locker_detail', pk=locker_pk)
    else:
        form = QuickRentalForm(initial={'start_date': timezone.now().date()})
    context = {
        'form': form,
        'locker': locker,
    }
    return render(request, 'lockers/quick_rent.html', context)


@login_required
def get_locker_price(request, pk):
    locker = get_object_or_404(Locker, pk=pk)
    return JsonResponse({
        'daily_rate': str(locker.daily_rate),
        'monthly_rate': str(locker.monthly_rate),
    })
