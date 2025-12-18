from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'subscriptions'

router = DefaultRouter()
router.register('plans', views.SubscriptionPlanViewSet, basename='plan')
router.register('packages', views.PackageViewSet, basename='package')
router.register('', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include('apps.subscriptions.traditional_urls')),
    path('api/v1/', include(router.urls)),
]
