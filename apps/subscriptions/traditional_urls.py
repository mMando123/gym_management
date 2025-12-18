from django.urls import path
from . import traditional_views

app_name = 'subscriptions'

urlpatterns = [
    path('', traditional_views.subscription_list, name='list'),
    path('create/', traditional_views.subscription_create, name='create'),
    path('<int:pk>/update/', traditional_views.subscription_update, name='update'),
]
