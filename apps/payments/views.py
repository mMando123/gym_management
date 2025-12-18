from rest_framework import viewsets
from .models import Payment, Invoice, Installment, InstallmentPlan
from .serializers import (
    PaymentSerializer,
    InvoiceSerializer,
    InstallmentSerializer,
    InstallmentPlanSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('member', 'subscription').all()
    serializer_class = PaymentSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('payment').all()
    serializer_class = InvoiceSerializer


class InstallmentViewSet(viewsets.ModelViewSet):
    queryset = Installment.objects.select_related('payment').all()
    serializer_class = InstallmentSerializer


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPlan.objects.select_related('member').all()
    serializer_class = InstallmentPlanSerializer
