from typing import Optional, List, Dict, Any
from django.db import transaction, models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.members.models import Member
from apps.subscriptions.models import Subscription
from .models import RewardRule, PointTransaction, Reward, RewardRedemption


class RewardService:
    """خدمات نظام المكافآت"""
    
    @staticmethod
    @transaction.atomic
    def add_points(
        member: Member,
        points: int,
        rule: Optional[RewardRule] = None,
        description: str = ''
    ) -> PointTransaction:
        """
        إضافة نقاط للعضو
        """
        new_balance = member.reward_points + points
        
        transaction_record = PointTransaction.objects.create(
            member=member,
            transaction_type=PointTransaction.TransactionType.EARNED,
            points=points,
            balance_after=new_balance,
            rule=rule,
            description=description or (rule.name if rule else 'إضافة نقاط')
        )
        
        member.reward_points = new_balance
        member.save()
        
        return transaction_record
    
    @staticmethod
    @transaction.atomic
    def deduct_points(
        member: Member,
        points: int,
        description: str = ''
    ) -> PointTransaction:
        """
        خصم نقاط من العضو
        """
        if points > member.reward_points:
            raise ValidationError("رصيد النقاط غير كافٍ")
        
        new_balance = member.reward_points - points
        
        transaction_record = PointTransaction.objects.create(
            member=member,
            transaction_type=PointTransaction.TransactionType.REDEEMED,
            points=-points,
            balance_after=new_balance,
            description=description
        )
        
        member.reward_points = new_balance
        member.save()
        
        return transaction_record
    
    @staticmethod
    def add_points_for_attendance(member: Member) -> Optional[PointTransaction]:
        """
        إضافة نقاط للحضور
        """
        try:
            rule = RewardRule.objects.get(
                action_type=RewardRule.ActionType.ATTENDANCE,
                is_active=True
            )
            return RewardService.add_points(
                member=member,
                points=rule.points,
                rule=rule,
                description=f"نقاط الحضور - {timezone.now().date()}"
            )
        except RewardRule.DoesNotExist:
            return None
    
    @staticmethod
    def add_points_for_subscription(
        member: Member, 
        subscription: Subscription
    ) -> Optional[PointTransaction]:
        """
        إضافة نقاط للاشتراك
        """
        try:
            rule = RewardRule.objects.get(
                action_type=RewardRule.ActionType.RENEWAL,
                is_active=True
            )
            # النقاط تتناسب مع قيمة الاشتراك
            bonus_points = int(subscription.final_price / 10)  # 1 نقطة لكل 10 ريال
            total_points = rule.points + bonus_points
            
            return RewardService.add_points(
                member=member,
                points=total_points,
                rule=rule,
                description=f"نقاط اشتراك جديد - {subscription.subscription_number}"
            )
        except RewardRule.DoesNotExist:
            return None
    
    @staticmethod
    def add_points_for_early_renewal(member: Member) -> Optional[PointTransaction]:
        """
        نقاط إضافية للتجديد المبكر
        """
        try:
            rule = RewardRule.objects.get(
                action_type=RewardRule.ActionType.EARLY_RENEWAL,
                is_active=True
            )
            return RewardService.add_points(
                member=member,
                points=rule.points,
                rule=rule,
                description="مكافأة التجديد المبكر"
            )
        except RewardRule.DoesNotExist:
            return None
    
    @staticmethod
    def add_points_for_referral(
        referrer: Member, 
        referred: Member
    ) -> Optional[PointTransaction]:
        """
        نقاط إحالة صديق
        """
        try:
            rule = RewardRule.objects.get(
                action_type=RewardRule.ActionType.REFERRAL,
                is_active=True
            )
            return RewardService.add_points(
                member=referrer,
                points=rule.points,
                rule=rule,
                description=f"إحالة صديق - {referred.user.get_full_name()}"
            )
        except RewardRule.DoesNotExist:
            return None
    
    @staticmethod
    def add_birthday_points(member: Member) -> Optional[PointTransaction]:
        """
        نقاط عيد الميلاد
        """
        try:
            rule = RewardRule.objects.get(
                action_type=RewardRule.ActionType.BIRTHDAY,
                is_active=True
            )
            return RewardService.add_points(
                member=member,
                points=rule.points,
                rule=rule,
                description=f"مكافأة عيد الميلاد 🎂"
            )
        except RewardRule.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def redeem_reward(member: Member, reward: Reward) -> RewardRedemption:
        """
        استبدال مكافأة
        """
        # التحقق من توفر النقاط
        if member.reward_points < reward.points_required:
            raise ValidationError(
                f"النقاط غير كافية. تحتاج {reward.points_required} نقطة"
            )
        
        # التحقق من توفر الكمية
        if reward.quantity_available is not None:
            if reward.quantity_available <= 0:
                raise ValidationError("هذه المكافأة غير متوفرة حالياً")
        
        # التحقق من صلاحية المكافأة
        today = timezone.now().date()
        if reward.valid_from and reward.valid_from > today:
            raise ValidationError("هذه المكافأة غير متاحة بعد")
        if reward.valid_until and reward.valid_until < today:
            raise ValidationError("انتهت صلاحية هذه المكافأة")
        
        # خصم النقاط
        RewardService.deduct_points(
            member=member,
            points=reward.points_required,
            description=f"استبدال مكافأة: {reward.name}"
        )
        
        # إنشاء سجل الاستبدال
        redemption = RewardRedemption.objects.create(
            member=member,
            reward=reward,
            points_used=reward.points_required,
            status=RewardRedemption.Status.PENDING
        )
        
        # تقليل الكمية المتاحة
        if reward.quantity_available is not None:
            reward.quantity_available -= 1
            reward.save()
        
        return redemption
    
    @staticmethod
    def get_available_rewards(member: Member) -> List[Dict[str, Any]]:
        """
        المكافآت المتاحة للعضو
        """
        today = timezone.now().date()
        
        rewards = Reward.objects.filter(
            is_active=True
        ).filter(
            models.Q(valid_from__isnull=True) | models.Q(valid_from__lte=today)
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today)
        ).filter(
            models.Q(quantity_available__isnull=True) | models.Q(quantity_available__gt=0)
        )
        
        result = []
        for reward in rewards:
            result.append({
                'reward': reward,
                'can_redeem': member.reward_points >= reward.points_required,
                'points_needed': max(0, reward.points_required - member.reward_points)
            })
        
        return result
    
    @staticmethod
    def get_points_history(
        member: Member, 
        limit: int = 20
    ) -> List[PointTransaction]:
        """
        سجل حركات النقاط
        """
        return PointTransaction.objects.filter(
            member=member
        ).select_related('rule').order_by('-created_at')[:limit]
    
    @staticmethod
    def check_birthday_rewards():
        """
        فحص وإرسال نقاط أعياد الميلاد
        يتم تشغيله يومياً عبر Celery
        """
        today = timezone.now().date()
        
        birthday_members = Member.objects.filter(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day,
            is_active=True
        )
        
        sent_count = 0
        for member in birthday_members:
            # التحقق من عدم إرسال النقاط مسبقاً هذا العام
            existing = PointTransaction.objects.filter(
                member=member,
                rule__action_type=RewardRule.ActionType.BIRTHDAY,
                created_at__year=today.year
            ).exists()
            
            if not existing:
                RewardService.add_birthday_points(member)
                sent_count += 1
        
        return {'birthday_rewards_sent': sent_count}
