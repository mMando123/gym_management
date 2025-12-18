from rest_framework import serializers
from .models import Payment, Invoice, Installment, InstallmentPlan


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'payment_number',
            'member',
            'subscription',
            'amount',
            'payment_method',
            'status',
            'total',
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id',
            'payment',
            'invoice_number',
            'due_date',
            'subtotal',
            'discount',
            'tax',
            'total',
            'is_paid',
        ]


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = [
            'id',
            'payment',
            'installment_number',
            'amount',
            'due_date',
            'paid_date',
            'is_paid',
        ]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        fields = [
            'id',
            'member',
            'total_amount',
            'installment_count',
            'start_date',
            'status',
        ]
