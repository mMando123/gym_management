# apps/rewards/serializers.py
from rest_framework import serializers
from .models import RewardRule, PointTransaction, Reward, RewardRedemption


class RewardRuleSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = RewardRule
        fields = [
            'id', 'name', 'action_type', 'action_type_display',
            'points', 'description', 'is_active',
            'created_at', 'updated_at'
        ]


class PointTransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)

    class Meta:
        model = PointTransaction
        fields = [
            'id', 'member', 'member_name', 'transaction_type',
            'transaction_type_display', 'points', 'balance_after',
            'rule', 'description', 'created_at'
        ]


class RewardSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reward
        fields = [
            'id', 'name', 'description', 'image', 'points_required',
            'quantity_available', 'is_active', 'is_available',
            'valid_from', 'valid_until', 'created_at', 'updated_at'
        ]


class RewardRedemptionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    reward_name = serializers.CharField(source='reward.name', read_only=True)

    class Meta:
        model = RewardRedemption
        fields = [
            'id', 'member', 'member_name', 'reward', 'reward_name',
            'points_used', 'status', 'status_display',
            'redeemed_at', 'delivered_at', 'notes',
            'created_at', 'updated_at'
        ]