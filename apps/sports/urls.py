from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'sports'

router = DefaultRouter()
router.register('categories', views.SportCategoryViewSet, basename='category')
router.register('', views.SportViewSet, basename='sport')

urlpatterns = [
    path('', include(router.urls)),
]
