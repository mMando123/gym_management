from django.urls import path
from . import traditional_views

app_name = 'attendance'

urlpatterns = [
    # Attendance Management
    path('', traditional_views.attendance_list, name='list'),
    path('check-in/', traditional_views.attendance_check_in, name='check_in'),
    path('<int:pk>/check-out/', traditional_views.attendance_check_out, name='check_out'),
    path('<int:pk>/', traditional_views.attendance_detail, name='detail'),
    path('stats/', traditional_views.attendance_stats, name='stats'),
    
    # AJAX Endpoints
    path('api/<int:member_id>/quick-info/', traditional_views.attendance_quick_info, name='quick_info'),
]
