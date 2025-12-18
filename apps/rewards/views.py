# apps/rewards/views.py
from rest_framework import viewsets
from .models import RewardRule, PointTransaction, Reward, RewardRedemption
from .serializers import (
    RewardRuleSerializer,
    PointTransactionSerializer,
    RewardSerializer,
    RewardRedemptionSerializer,
)


class RewardRuleViewSet(viewsets.ModelViewSet):
    queryset = RewardRule.objects.all()
    serializer_class = RewardRuleSerializer


class PointTransactionViewSet(viewsets.ModelViewSet):
    queryset = PointTransaction.objects.select_related('member', 'rule').all()
    serializer_class = PointTransactionSerializer


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer


class RewardRedemptionViewSet(viewsets.ModelViewSet):
    queryset = RewardRedemption.objects.select_related('member', 'reward').all()
    serializer_class = RewardRedemptionSerializer