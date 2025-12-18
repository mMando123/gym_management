from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

router = DefaultRouter()
router.register('invoices', views.InvoiceViewSet, basename='invoice')
router.register('installments', views.InstallmentViewSet, basename='installment')
router.register('', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include('apps.payments.traditional_urls')),
    path('api/v1/', include(router.urls)),
]
