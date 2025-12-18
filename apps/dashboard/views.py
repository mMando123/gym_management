# apps/dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.members.models import Member
from apps.subscriptions.models import Subscription
from apps.attendance.models import Attendance
from apps.payments.models import Payment
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta

@login_required
def dashboard(request):
    today = timezone.now().date()
    
    # Get statistics
    total_members = Member.objects.filter(is_active=True).count()
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(check_in__date=today).count()
    
    # Expiring subscriptions (within 7 days)
    expiring_soon = Subscription.objects.filter(
        status='active',
        end_date__lte=today + timedelta(days=7),
        end_date__gte=today
    ).count()
    
    # Today's revenue
    today_revenue = Payment.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Recent members
    recent_members = Member.objects.order_by('-created_at')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.filter(status='completed').order_by('-created_at')[:5]
    
    context = {
        'total_members': total_members,
        'today_attendance': today_attendance,
        'expiring_soon': expiring_soon,
        'today_revenue': today_revenue,
        'recent_members': recent_members,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'dashboard/index.html', context)