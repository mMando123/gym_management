from django.urls import path
from . import traditional_views

app_name = 'trainers'

urlpatterns = [
    # Trainers Management
    path('', traditional_views.trainer_list, name='list'),
    path('create/', traditional_views.trainer_create, name='create'),
    path('<int:pk>/', traditional_views.trainer_detail, name='detail'),
    path('<int:pk>/edit/', traditional_views.trainer_edit, name='edit'),
    path('<int:pk>/delete/', traditional_views.trainer_delete, name='delete'),
    
    # Trainer Availability
    path('<int:trainer_pk>/availability/', traditional_views.availability_list, name='availability_list'),
    path('<int:trainer_pk>/availability/add/', traditional_views.availability_create, name='availability_create'),
    path('availability/<int:pk>/delete/', traditional_views.availability_delete, name='availability_delete'),
    
    # Trainer Sessions
    path('<int:trainer_pk>/sessions/', traditional_views.session_list, name='session_list'),
    path('<int:trainer_pk>/session/book/', traditional_views.session_book, name='session_book'),
    
    # AJAX Endpoints
    path('api/<int:trainer_id>/availability/', traditional_views.trainer_availability_api, name='availability_api'),
]
