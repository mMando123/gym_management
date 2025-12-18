from django.urls import path
from . import traditional_views

app_name = 'dashboard'

urlpatterns = [
    path('', traditional_views.dashboard, name='dashboard'),
    path('members/stats/', traditional_views.dashboard_members_stats, name='members_stats'),
    path('revenue/stats/', traditional_views.dashboard_revenue_stats, name='revenue_stats'),
]
