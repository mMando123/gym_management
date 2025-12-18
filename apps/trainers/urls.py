from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'trainers'

router = DefaultRouter()
router.register('availability', views.TrainerAvailabilityViewSet, basename='availability')
router.register('', views.TrainerViewSet, basename='trainer')

urlpatterns = [
    path('', include('apps.trainers.traditional_urls')),
    path('api/v1/', include(router.urls)),
]
