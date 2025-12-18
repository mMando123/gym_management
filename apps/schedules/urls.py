from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'schedules'

router = DefaultRouter()
router.register('bookings', views.ClassBookingViewSet, basename='booking')
router.register('sessions', views.ClassSessionViewSet, basename='session')
router.register('', views.ClassScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
]
