# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('members/', include('apps.members.urls', namespace='members')),
    path('subscriptions/', include('apps.subscriptions.urls', namespace='subscriptions')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('trainers/', include('apps.trainers.urls', namespace='trainers')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('rewards/', include('apps.rewards.urls', namespace='rewards')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)