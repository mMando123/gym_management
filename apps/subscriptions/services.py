from decimal import Decimal
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.members.models import Member
from apps.sports.models import Sport
from .models import (
    Subscription, 
    SubscriptionPlan, 
    Package, 
    PlanSportPrice,
    SubscriptionFreeze
)


class SubscriptionService:
    """خدمات إدارة الاشتراكات"""
    
    @staticmethod
    def calculate_price(
        plan: SubscriptionPlan,
        sports: List[Sport],
        package: Optional[Package] = None,
        promo_code: Optional[str] = None
    ) -> Dict[str, Decimal]:
        """
        حساب سعر الاشتراك
        """
        original_price = Decimal('0.00')
        
        # حساب سعر كل رياضة
        for sport in sports:
            try:
                sport_price = PlanSportPrice.objects.get(
                    plan=plan, 
                    sport=sport
                )
                original_price += sport_price.price
            except PlanSportPrice.DoesNotExist:
                raise ValidationError(f"لا يوجد سعر محدد لـ {sport.name} في هذه الخطة")
        
        discount_amount = Decimal('0.00')
        
        # خصم الخطة
        if plan.discount_percentage > 0:
            discount_amount += original_price * (plan.discount_percentage / 100)
        
        # خصم الباقة
        if package and len(sports) > 1:
            package_discount = original_price * (package.discount_percentage / 100)
            discount_amount += package_discount
        
        # خصم كود الترويج
        promo_discount = Decimal('0.00')
        if promo_code:
            promo_discount = SubscriptionService._apply_promo_code(
                promo_code, 
                original_price
            )
            discount_amount += promo_discount
        
        final_price = original_price - discount_amount
        
        return {
            'original_price': original_price,
            'discount_amount': discount_amount,
            'final_price': max(final_price, Decimal('0.00')),
            'promo_discount': promo_discount
        }
    
    @staticmethod
    def _apply_promo_code(code: str, amount: Decimal) -> Decimal:
        """تطبيق كود الترويج"""
        # يمكن إضافة نموذج PromoCode لاحقاً
        # هذا مثال بسيط
        promo_codes = {
            'WELCOME10': Decimal('10'),  # 10%
            'SUMMER20': Decimal('20'),   # 20%
            'VIP30': Decimal('30'),      # 30%
        }
        
        if code.upper() in promo_codes:
            return amount * (promo_codes[code.upper()] / 100)
        return Decimal('0.00')
    
    @staticmethod
    @transaction.atomic
    def create_subscription(
        member: Member,
        plan: SubscriptionPlan,
        sports: List[Sport],
        package: Optional[Package] = None,
        start_date: Optional[date] = None,
        promo_code: Optional[str] = None,
        payment_method: str = 'cash',
        notes: str = ''
    ) -> Subscription:
        """
        إنشاء اشتراك جديد
        """
        # التحقق من عدم وجود اشتراك نشط لنفس الرياضات
        active_subscriptions = Subscription.objects.filter(
            member=member,
            status=Subscription.Status.ACTIVE,
            sports__in=sports
        ).distinct()
        
        if active_subscriptions.exists():
            raise ValidationError("يوجد اشتراك نشط لبعض هذه الرياضات")
        
        # تحديد تاريخ البداية
        if not start_date:
            start_date = timezone.now().date()
        
        # حساب تاريخ الانتهاء
        end_date = start_date + timedelta(days=plan.duration_days)
        
        # حساب السعر
        pricing = SubscriptionService.calculate_price(
            plan=plan,
            sports=sports,
            package=package,
            promo_code=promo_code
        )
        
        # إنشاء الاشتراك
        subscription = Subscription.objects.create(
            member=member,
            plan=plan,
            package=package,
            start_date=start_date,
            end_date=end_date,
            original_price=pricing['original_price'],
            discount_amount=pricing['discount_amount'],
            final_price=pricing['final_price'],
            freeze_days_remaining=plan.freeze_days_allowed,
            guest_passes_remaining=plan.guest_passes,
            pt_sessions_remaining=plan.personal_training_sessions,
            status=Subscription.Status.PENDING,
            notes=notes
        )
        
        # إضافة الرياضات
        subscription.sports.set(sports)
        
        return subscription
    
    @staticmethod
    @transaction.atomic
    def renew_subscription(
        subscription: Subscription,
        payment_method: str = 'cash'
    ) -> Subscription:
        """
        تجديد الاشتراك
        """
        # حساب تاريخ البداية الجديد
        if subscription.status == Subscription.Status.ACTIVE:
            new_start_date = subscription.end_date + timedelta(days=1)
        else:
            new_start_date = timezone.now().date()
        
        # إنشاء اشتراك جديد بنفس الإعدادات
        new_subscription = SubscriptionService.create_subscription(
            member=subscription.member,
            plan=subscription.plan,
            sports=list(subscription.sports.all()),
            package=subscription.package,
            start_date=new_start_date,
            payment_method=payment_method,
            notes=f"تجديد للاشتراك رقم {subscription.subscription_number}"
        )
        
        # نقاط إضافية للتجديد
        days_before_expiry = (subscription.end_date - timezone.now().date()).days
        
        return new_subscription
    
    @staticmethod
    @transaction.atomic
    def freeze_subscription(
        subscription: Subscription,
        days: int,
        reason: str,
        notes: str = ''
    ) -> SubscriptionFreeze:
        """
        تجميد الاشتراك
        """
        if subscription.status != Subscription.Status.ACTIVE:
            raise ValidationError("لا يمكن تجميد اشتراك غير نشط")
        
        if days > subscription.freeze_days_remaining:
            raise ValidationError(
                f"عدد أيام التجميد المتبقية: {subscription.freeze_days_remaining}"
            )
        
        if days < 1:
            raise ValidationError("يجب أن يكون عدد الأيام 1 على الأقل")
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days)
        
        # إنشاء سجل التجميد
        freeze = SubscriptionFreeze.objects.create(
            subscription=subscription,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
            notes=notes
        )
        
        # تحديث الاشتراك
        subscription.status = Subscription.Status.FROZEN
        subscription.freeze_days_used += days
        subscription.freeze_days_remaining -= days
        subscription.end_date += timedelta(days=days)
        subscription.save()
        
        return freeze
    
    @staticmethod
    @transaction.atomic
    def unfreeze_subscription(subscription: Subscription) -> Subscription:
        """
        إلغاء تجميد الاشتراك
        """
        if subscription.status != Subscription.Status.FROZEN:
            raise ValidationError("الاشتراك غير مجمد")
        
        # حساب الأيام غير المستخدمة من التجميد
        active_freeze = subscription.freezes.filter(
            end_date__gte=timezone.now().date()
        ).first()
        
        if active_freeze:
            unused_days = (active_freeze.end_date - timezone.now().date()).days
            subscription.freeze_days_remaining += unused_days
            subscription.freeze_days_used -= unused_days
            subscription.end_date -= timedelta(days=unused_days)
            
            # تحديث سجل التجميد
            active_freeze.end_date = timezone.now().date()
            active_freeze.days -= unused_days
            active_freeze.save()
        
        subscription.status = Subscription.Status.ACTIVE
        subscription.save()
        
        return subscription
    
    @staticmethod
    def check_expired_subscriptions():
        """
        فحص وتحديث الاشتراكات المنتهية
        يتم تشغيله يومياً عبر Celery
        """
        today = timezone.now().date()
        
        # الاشتراكات المنتهية
        expired = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            end_date__lt=today
        )
        
        for subscription in expired:
            subscription.status = Subscription.Status.EXPIRED
            subscription.save()
        
        # الاشتراكات التي ستنتهي قريباً (تذكير)
        expiring_soon = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            end_date__range=[today, today + timedelta(days=7)]
        )
        
        return {
            'expired_count': expired.count(),
            'expiring_soon_count': expiring_soon.count()
        }
    
    @staticmethod
    def unfreeze_due_subscriptions():
        """
        إلغاء تجميد الاشتراكات التي انتهى تجميدها
        يتم تشغيله يومياً عبر Celery
        """
        today = timezone.now().date()
        
        frozen_subscriptions = Subscription.objects.filter(
            status=Subscription.Status.FROZEN
        )
        
        unfrozen_count = 0
        for subscription in frozen_subscriptions:
            active_freeze = subscription.freezes.filter(
                end_date__lte=today
            ).order_by('-end_date').first()
            
            if active_freeze and active_freeze.end_date <= today:
                subscription.status = Subscription.Status.ACTIVE
                subscription.save()
                unfrozen_count += 1
        
        return {'unfrozen_count': unfrozen_count}
    
    @staticmethod
    def get_member_active_subscription(
        member: Member, 
        sport: Optional[Sport] = None
    ) -> Optional[Subscription]:
        """
        الحصول على الاشتراك النشط للعضو
        """
        queryset = Subscription.objects.filter(
            member=member,
            status=Subscription.Status.ACTIVE
        )
        
        if sport:
            queryset = queryset.filter(sports=sport)
        
        return queryset.first()
    
    @staticmethod
    def can_member_attend(member: Member, sport: Sport) -> Dict[str, Any]:
        """
        التحقق من إمكانية حضور العضو
        """
        subscription = SubscriptionService.get_member_active_subscription(
            member, 
            sport
        )
        
        if not subscription:
            return {
                'can_attend': False,
                'reason': 'لا يوجد اشتراك نشط لهذه الرياضة'
            }
        
        if subscription.status == Subscription.Status.FROZEN:
            return {
                'can_attend': False,
                'reason': 'الاشتراك مجمد'
            }
        
        if subscription.end_date < timezone.now().date():
            return {
                'can_attend': False,
                'reason': 'الاشتراك منتهي'
            }
        
        return {
            'can_attend': True,
            'subscription': subscription,
            'days_remaining': subscription.days_remaining
        }
