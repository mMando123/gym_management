from django.urls import path
from . import views

app_name = 'lockers'

urlpatterns = [
    # الخزائن
    path('', views.locker_list, name='locker_list'),
    path('create/', views.locker_create, name='locker_create'),
    path('<int:pk>/', views.locker_detail, name='locker_detail'),
    path('<int:pk>/update/', views.locker_update, name='locker_update'),
    path('<int:pk>/delete/', views.locker_delete, name='locker_delete'),
    path('<int:locker_pk>/quick-rent/', views.quick_rent, name='quick_rent'),
    path('<int:pk>/price/', views.get_locker_price, name='get_locker_price'),
    
    # الإيجارات
    path('rentals/', views.rental_list, name='rental_list'),
    path('rentals/create/', views.rental_create, name='rental_create'),
    path('rentals/<int:pk>/', views.rental_detail, name='rental_detail'),
    path('rentals/<int:pk>/end/', views.rental_end, name='rental_end'),
]
