from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import traditional_views

app_name = 'attendance'

router = DefaultRouter()
router.register('guests', views.GuestVisitViewSet, basename='guest')
router.register('', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('check-in/', traditional_views.attendance_check_in, name='checkin'),
    path('web/', include('apps.attendance.traditional_urls')),
    path('api/v1/', include(router.urls)),
]
