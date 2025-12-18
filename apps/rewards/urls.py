from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'rewards'

router = DefaultRouter()
router.register('rules', views.RewardRuleViewSet, basename='rule')
router.register('transactions', views.PointTransactionViewSet, basename='transaction')
router.register('redemptions', views.RewardRedemptionViewSet, basename='redemption')
router.register('', views.RewardViewSet, basename='reward')

urlpatterns = [
    path('', include(router.urls)),
]
