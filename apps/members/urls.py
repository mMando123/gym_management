from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import traditional_views

app_name = 'members'

router = DefaultRouter()
router.register('', views.MemberViewSet, basename='member')

urlpatterns = [
    path('', traditional_views.member_list, name='list'),
    path('create/', traditional_views.member_create, name='create'),
    path('web/', include('apps.members.traditional_urls')),
    path('api/v1/', include(router.urls)),
]
