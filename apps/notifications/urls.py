from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

router = DefaultRouter()
router.register('templates', views.NotificationTemplateViewSet, basename='template')
router.register('', views.NotificationViewSet, basename='notification')

urlpatterns = router.urls