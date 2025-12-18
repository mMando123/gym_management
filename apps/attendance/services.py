from datetime import datetime, timedelta, time
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate, TruncHour

from apps.members.models import Member
from apps.sports.models import Sport
from apps.trainers.models import Trainer
from apps.subscriptions.services import SubscriptionService
from apps.rewards.services import RewardService
from .models import Attendance, GuestVisit


class AttendanceService:
    """خدمات الحضور"""
    
    @staticmethod
    @transaction.atomic
    def check_in(
        member: Member,
        sport: Sport,
        trainer: Optional[Trainer] = None,
        is_manual: bool = False
    ) -> Attendance:
        """
        تسجيل دخول العضو
        """
        # التحقق من إمكانية الحضور
        can_attend = SubscriptionService.can_member_attend(member, sport)
        
        if not can_attend['can_attend']:
            raise ValidationError(can_attend['reason'])
        
        subscription = can_attend['subscription']
        
        # التحقق من عدم وجود تسجيل دخول سابق بدون خروج
        existing_attendance = Attendance.objects.filter(
            member=member,
            check_out__isnull=True
        ).first()
        
        if existing_attendance:
            raise ValidationError(
                f"يجب تسجيل الخروج أولاً من الحضور السابق ({existing_attendance.sport.name})"
            )
        
        # إنشاء سجل الحضور
        attendance = Attendance.objects.create(
            member=member,
            subscription=subscription,
            sport=sport,
            trainer=trainer,
            check_in=timezone.now(),
            is_manual_entry=is_manual
        )
        
        # إضافة نقاط الحضور
        RewardService.add_points_for_attendance(member)
        
        return attendance
    
    @staticmethod
    @transaction.atomic
    def check_out(
        member: Member = None, 
        attendance: Attendance = None
    ) -> Attendance:
        """
        تسجيل خروج العضو
        """
        if not attendance and member:
            attendance = Attendance.objects.filter(
                member=member,
                check_out__isnull=True
            ).first()
        
        if not attendance:
            raise ValidationError("لا يوجد تسجيل دخول سابق")
        
        if attendance.check_out:
            raise ValidationError("تم تسجيل الخروج مسبقاً")
        
        attendance.check_out = timezone.now()
        attendance.save()
        
        return attendance
    
    @staticmethod
    def get_current_attendees(sport: Optional[Sport] = None) -> List[Attendance]:
        """
        الأعضاء الموجودون حالياً
        """
        queryset = Attendance.objects.filter(
            check_out__isnull=True
        ).select_related('member', 'sport', 'trainer')
        
        if sport:
            queryset = queryset.filter(sport=sport)
        
        return list(queryset)
    
    @staticmethod
    def get_member_attendance_history(
        member: Member,
        start_date=None,
        end_date=None,
        sport: Optional[Sport] = None,
        limit: int = 50
    ) -> List[Attendance]:
        """
        سجل حضور العضو
        """
        queryset = Attendance.objects.filter(
            member=member
        ).select_related('sport', 'trainer')
        
        if start_date:
            queryset = queryset.filter(check_in__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_in__date__lte=end_date)
        if sport:
            queryset = queryset.filter(sport=sport)
        
        return list(queryset.order_by('-check_in')[:limit])
    
    @staticmethod
    def get_attendance_statistics(
        start_date=None,
        end_date=None,
        sport: Optional[Sport] = None
    ) -> Dict[str, Any]:
        """
        إحصائيات الحضور
        """
        queryset = Attendance.objects.all()
        
        if start_date:
            queryset = queryset.filter(check_in__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_in__date__lte=end_date)
        if sport:
            queryset = queryset.filter(sport=sport)
        
        # إجمالي الحضور
        total = queryset.count()
        
        # الحضور اليومي
        daily = queryset.annotate(
            date=TruncDate('check_in')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # الحضور حسب الساعة
        hourly = queryset.annotate(
            hour=TruncHour('check_in')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        # الحضور حسب الرياضة
        by_sport = queryset.values(
            'sport__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # متوسط مدة التدريب
        completed = queryset.filter(check_out__isnull=False)
        
        return {
            'total_attendance': total,
            'daily_attendance': list(daily),
            'hourly_distribution': list(hourly),
            'by_sport': list(by_sport),
            'average_duration_minutes': AttendanceService._calculate_avg_duration(completed)
        }
    
    @staticmethod
    def _calculate_avg_duration(queryset) -> Optional[float]:
        """
        حساب متوسط مدة التدريب
        """
        total_duration = 0
        count = 0
        
        for attendance in queryset:
            if attendance.duration_minutes:
                total_duration += attendance.duration_minutes
                count += 1
        
        return round(total_duration / count, 2) if count > 0 else None
    
    @staticmethod
    def get_peak_hours(
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        ساعات الذروة
        """
        start_date = timezone.now() - timedelta(days=days)
        
        hourly = Attendance.objects.filter(
            check_in__gte=start_date
        ).annotate(
            hour=TruncHour('check_in')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return list(hourly)
    
    @staticmethod
    @transaction.atomic
    def record_guest_visit(
        host_member: Member,
        guest_name: str,
        guest_phone: str
    ) -> GuestVisit:
        """
        تسجيل زيارة ضيف
        """
        # التحقق من أن العضو لديه تذاكر ضيوف
        active_subscription = SubscriptionService.get_member_active_subscription(
            host_member
        )
        
        if not active_subscription:
            raise ValidationError("لا يوجد اشتراك نشط")
        
        if active_subscription.guest_passes_remaining <= 0:
            raise ValidationError("لا توجد تذاكر ضيوف متبقية")
        
        # إنشاء سجل الزيارة
        visit = GuestVisit.objects.create(
            host_member=host_member,
            guest_name=guest_name,
            guest_phone=guest_phone,
            visit_date=timezone.now().date(),
            check_in=timezone.now()
        )
        
        # خصم تذكرة من الاشتراك
        active_subscription.guest_passes_remaining -= 1
        active_subscription.save()
        
        return visit
    
    @staticmethod
    @transaction.atomic
    def checkout_guest(visit: GuestVisit) -> GuestVisit:
        """
        تسجيل خروج الضيف
        """
        if visit.check_out:
            raise ValidationError("تم تسجيل الخروج مسبقاً")
        
        visit.check_out = timezone.now()
        visit.save()
        
        return visit
    
    @staticmethod
    def auto_checkout_expired():
        """
        تسجيل خروج تلقائي للجلسات المفتوحة لفترة طويلة
        يتم تشغيله عبر Celery
        """
        # الجلسات المفتوحة لأكثر من 4 ساعات
        threshold = timezone.now() - timedelta(hours=4)
        
        expired_attendances = Attendance.objects.filter(
            check_out__isnull=True,
            check_in__lt=threshold
        )
        
        count = 0
        for attendance in expired_attendances:
            attendance.check_out = attendance.check_in + timedelta(hours=2)  # نفترض ساعتين
            attendance.notes = "تسجيل خروج تلقائي"
            attendance.save()
            count += 1
        
        return {'auto_checkouts': count}
    
    @staticmethod
    def get_member_daily_attendance(member: Member) -> int:
        """
        عدد مرات حضور العضو اليوم
        """
        today = timezone.now().date()
        
        return Attendance.objects.filter(
            member=member,
            check_in__date=today
        ).count()
    
    @staticmethod
    def get_attendance_rate(
        member: Member,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        معدل حضور العضو
        """
        start_date = timezone.now().date() - timedelta(days=days)
        
        attendance_count = Attendance.objects.filter(
            member=member,
            check_in__date__gte=start_date
        ).count()
        
        attendance_rate = round((attendance_count / days) * 100, 2) if days > 0 else 0
        
        return {
            'total_attendance': attendance_count,
            'days_period': days,
            'attendance_rate_percentage': attendance_rate,
            'average_per_week': round(attendance_count / (days / 7), 2)
        }
