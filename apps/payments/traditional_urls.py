from django.urls import path
from . import traditional_views

app_name = 'payments'

urlpatterns = [
    # Payments Management
    path('', traditional_views.payment_list, name='list'),
    path('create/', traditional_views.payment_create, name='create'),
    path('<int:pk>/', traditional_views.payment_detail, name='detail'),
    path('stats/', traditional_views.payment_stats, name='stats'),
    
    # Invoices Management
    path('invoices/', traditional_views.invoice_list, name='invoice_list'),
    path('invoices/create/', traditional_views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', traditional_views.invoice_detail, name='invoice_detail'),
    
    # Installment Plans Management
    path('installments/', traditional_views.installment_list, name='installment_list'),
    path('installments/create/', traditional_views.installment_create, name='installment_create'),
    path('installments/<int:pk>/', traditional_views.installment_detail, name='installment_detail'),
    
    # AJAX Endpoints
    path('api/<int:member_id>/payments/', traditional_views.member_payments_api, name='member_payments_api'),
]
