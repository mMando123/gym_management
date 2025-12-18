from django.urls import path
from . import traditional_views

app_name = 'members'

urlpatterns = [
    # Traditional Views (Web Interface)
    path('', traditional_views.member_list, name='member_list'),
    path('<int:pk>/', traditional_views.member_detail, name='member_detail'),
    path('add/', traditional_views.member_create, name='member_create'),
    path('<int:pk>/edit/', traditional_views.member_edit, name='member_edit'),
    path('<int:pk>/delete/', traditional_views.member_delete, name='member_delete'),
    
    # Member Details
    path('<int:pk>/metrics/', traditional_views.member_metrics, name='member_metrics'),
    path('<int:pk>/metrics/add/', traditional_views.member_metrics_add, name='member_metrics_add'),
    path('<int:pk>/attendance/', traditional_views.member_attendance, name='member_attendance'),
    path('<int:pk>/subscriptions/', traditional_views.member_subscriptions, name='member_subscriptions'),
    path('<int:pk>/payments/', traditional_views.member_payments, name='member_payments'),
    
    # AJAX Endpoints
    path('api/search/', traditional_views.member_search, name='member_search'),
    path('api/<int:pk>/info/', traditional_views.member_quick_info, name='member_quick_info'),
]
