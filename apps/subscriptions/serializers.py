from rest_framework import serializers
from .models import (
    SubscriptionPlan, 
    PlanSportPrice, 
    Package, 
    Subscription,
    SubscriptionFreeze
)


class PlanSportPriceSerializer(serializers.ModelSerializer):
    """سيريلايزر سعر الرياضة في الخطة"""
    
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    
    class Meta:
        model = PlanSportPrice
        fields = ['sport', 'sport_name', 'price']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """سيريلايزر خطة الاشتراك"""
    
    sport_prices = PlanSportPriceSerializer(
        source='plansportprice_set', 
        many=True, 
        read_only=True
    )
    duration_type_display = serializers.CharField(
        source='get_duration_type_display', 
        read_only=True
    )
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'duration_type', 'duration_type_display',
            'duration_days', 'discount_percentage', 'freeze_days_allowed',
            'guest_passes', 'locker_included', 'towel_service',
            'personal_training_sessions', 'sport_prices', 'is_active'
        ]


class PackageSerializer(serializers.ModelSerializer):
    """سيريلايزر الباقة"""
    
    sports_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'name', 'description', 'sports',
            'sports_data', 'discount_percentage', 'is_active'
        ]
    
    def get_sports_data(self, obj):
        """الحصول على بيانات الرياضات"""
        return [{'id': s.id, 'name': s.name} for s in obj.sports.all()]


class SubscriptionFreezeSerializer(serializers.ModelSerializer):
    """سيريلايزر تجميد الاشتراك"""
    
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    
    class Meta:
        model = SubscriptionFreeze
        fields = [
            'id', 'start_date', 'end_date', 'days',
            'reason', 'reason_display', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class SubscriptionListSerializer(serializers.ModelSerializer):
    """سيريلايزر قائمة الاشتراكات (محسّن للأداء)"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_remaining = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'subscription_number', 'member_name', 'plan_name',
            'start_date', 'end_date', 'status', 'status_display',
            'final_price', 'days_remaining', 'is_expiring_soon'
        ]


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    """سيريلايزر تفاصيل الاشتراك"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    sports_data = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_remaining = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    freezes = SubscriptionFreezeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'subscription_number', 'member', 'member_name', 'member_id',
            'plan', 'plan_name', 'sports_data', 'package', 'start_date', 'end_date',
            'freeze_days_used', 'freeze_days_remaining', 'status', 'status_display',
            'original_price', 'discount_amount', 'final_price',
            'guest_passes_remaining', 'pt_sessions_remaining',
            'days_remaining', 'is_expiring_soon', 'freezes', 'notes', 'created_at'
        ]
        read_only_fields = [
            'subscription_number', 'freeze_days_used', 'original_price',
            'discount_amount', 'final_price', 'created_at'
        ]
    
    def get_sports_data(self, obj):
        """الحصول على بيانات الرياضات"""
        return [{'id': s.id, 'name': s.name} for s in obj.sports.all()]


class SubscriptionCreateSerializer(serializers.Serializer):
    """سيريلايزر إنشاء اشتراك"""
    
    member_id = serializers.IntegerField()
    plan_id = serializers.IntegerField()
    sport_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    package_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=['cash', 'card', 'bank_transfer', 'online'],
        default='cash'
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_member_id(self, value):
        from apps.members.models import Member
        try:
            Member.objects.get(id=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("العضو غير موجود")
        return value
    
    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("خطة الاشتراك غير موجودة أو غير نشطة")
        return value
    
    def validate_sport_ids(self, value):
        from apps.sports.models import Sport
        sports = Sport.objects.filter(id__in=value, is_active=True)
        if sports.count() != len(value):
            raise serializers.ValidationError("بعض الرياضات غير موجودة أو غير نشطة")
        return value


class SubscriptionFreezeCreateSerializer(serializers.Serializer):
    """سيريلايزر طلب تجميد"""
    
    days = serializers.IntegerField(min_value=1, max_value=30)
    reason = serializers.ChoiceField(choices=SubscriptionFreeze.FreezeReason.choices)
    notes = serializers.CharField(required=False, allow_blank=True)


class SubscriptionRenewSerializer(serializers.Serializer):
    """سيريلايزر تجديد الاشتراك"""
    
    payment_method = serializers.ChoiceField(
        choices=['cash', 'card', 'bank_transfer', 'online'],
        default='cash'
    )


class CalculatePriceSerializer(serializers.Serializer):
    """سيريلايزر حساب السعر"""
    
    plan_id = serializers.IntegerField()
    sport_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    package_id = serializers.IntegerField(required=False, allow_null=True)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("خطة الاشتراك غير موجودة")
        return value
    
    def validate_sport_ids(self, value):
        from apps.sports.models import Sport
        sports = Sport.objects.filter(id__in=value, is_active=True)
        if sports.count() != len(value):
            raise serializers.ValidationError("بعض الرياضات غير موجودة")
        return value
