from decimal import Decimal
from datetime import timedelta, date
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.members.models import Member
from apps.subscriptions.models import Subscription
from .models import Payment, Invoice, Installment


class PaymentService:
    """خدمات المدفوعات"""
    
    @staticmethod
    @transaction.atomic
    def create_payment(
        member: Member,
        subscription: Optional[Subscription] = None,
        amount: Decimal = Decimal('0.00'),
        payment_method: str = 'cash',
        payment_type: str = 'subscription',
        processed_by=None,
        notes: str = ''
    ) -> Payment:
        """
        إنشاء دفعة جديدة
        """
        # حساب الضريبة (15% VAT كمثال)
        tax_rate = Decimal('0.15')
        tax = amount * tax_rate
        total = amount + tax
        
        payment = Payment.objects.create(
            member=member,
            subscription=subscription,
            payment_type=payment_type,
            payment_method=payment_method,
            status=Payment.PaymentStatus.PENDING,
            amount=amount,
            tax=tax,
            total=total,
            processed_by=processed_by,
            notes=notes
        )
        
        # إذا كان الدفع نقدي، نعتبره مكتملاً مباشرة
        if payment_method == 'cash':
            PaymentService.complete_payment(payment)
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def complete_payment(
        payment: Payment, 
        transaction_id: Optional[str] = None
    ) -> Payment:
        """
        إكمال عملية الدفع
        """
        if payment.status == Payment.PaymentStatus.COMPLETED:
            raise ValidationError("هذه الدفعة مكتملة بالفعل")
        
        payment.status = Payment.PaymentStatus.COMPLETED
        payment.amount_paid = payment.total
        payment.amount_remaining = Decimal('0.00')
        payment.transaction_id = transaction_id
        payment.save()
        
        # إنشاء الفاتورة
        PaymentService.create_invoice(payment)
        
        return payment
    
    @staticmethod
    def create_invoice(payment: Payment) -> Invoice:
        """
        إنشاء فاتورة
        """
        invoice = Invoice.objects.create(
            payment=payment,
            subtotal=payment.amount,
            discount=payment.discount,
            tax=payment.tax,
            total=payment.total,
            is_paid=payment.status == Payment.PaymentStatus.COMPLETED
        )
        
        # توليد رقم الفاتورة
        invoice.invoice_number = f"INV{invoice.id:08d}"
        invoice.save()
        
        return invoice
    
    @staticmethod
    @transaction.atomic
    def create_installment_payment(
        member: Member,
        subscription: Optional[Subscription] = None,
        total_amount: Decimal = Decimal('0.00'),
        num_installments: int = 3,
        payment_method: str = 'card',
        first_payment_amount: Optional[Decimal] = None
    ) -> Payment:
        """
        إنشاء دفع بالتقسيط
        """
        if num_installments < 2:
            raise ValidationError("عدد الأقساط يجب أن يكون 2 على الأقل")
        
        # حساب الضريبة
        tax_rate = Decimal('0.15')
        tax = total_amount * tax_rate
        total = total_amount + tax
        
        # الدفعة الأولى (المقدم)
        if first_payment_amount:
            if first_payment_amount >= total:
                raise ValidationError("الدفعة الأولى لا يمكن أن تكون أكبر من الإجمالي")
        else:
            first_payment_amount = total / num_installments
        
        # إنشاء الدفعة الرئيسية
        payment = Payment.objects.create(
            member=member,
            subscription=subscription,
            payment_type='subscription',
            payment_method=payment_method,
            status=Payment.PaymentStatus.PARTIAL,
            amount=total_amount,
            tax=tax,
            total=total,
            amount_paid=first_payment_amount,
            amount_remaining=total - first_payment_amount
        )
        
        # حساب قيمة كل قسط
        remaining_after_first = total - first_payment_amount
        remaining_installments = num_installments - 1
        installment_amount = remaining_after_first / remaining_installments
        
        # إنشاء الأقساط
        today = timezone.now().date()
        
        # القسط الأول (المدفوع)
        Installment.objects.create(
            payment=payment,
            installment_number=1,
            amount=first_payment_amount,
            due_date=today,
            paid_date=today,
            is_paid=True
        )
        
        # باقي الأقساط
        for i in range(2, num_installments + 1):
            due_date = today + timedelta(days=30 * (i - 1))
            Installment.objects.create(
                payment=payment,
                installment_number=i,
                amount=installment_amount,
                due_date=due_date,
                is_paid=False
            )
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def pay_installment(installment: Installment) -> Installment:
        """
        دفع قسط
        """
        if installment.is_paid:
            raise ValidationError("هذا القسط مدفوع بالفعل")
        
        installment.is_paid = True
        installment.paid_date = timezone.now().date()
        installment.save()
        
        # تحديث الدفعة الرئيسية
        payment = installment.payment
        payment.amount_paid += installment.amount
        payment.amount_remaining -= installment.amount
        
        # التحقق من اكتمال جميع الأقساط
        unpaid_installments = payment.installments.filter(is_paid=False)
        if not unpaid_installments.exists():
            payment.status = Payment.PaymentStatus.COMPLETED
        
        payment.save()
        
        return installment
    
    @staticmethod
    @transaction.atomic
    def refund_payment(
        payment: Payment,
        amount: Optional[Decimal] = None,
        reason: str = ''
    ) -> Payment:
        """
        استرداد دفعة
        """
        if payment.status == Payment.PaymentStatus.REFUNDED:
            raise ValidationError("هذه الدفعة مستردة بالفعل")
        
        refund_amount = amount or payment.total
        
        if refund_amount > payment.amount_paid:
            raise ValidationError("مبلغ الاسترداد أكبر من المبلغ المدفوع")
        
        # إنشاء سجل الاسترداد (يمكن إنشاء نموذج Refund منفصل)
        payment.status = Payment.PaymentStatus.REFUNDED
        payment.notes = f"{payment.notes}\n\nاسترداد: {refund_amount} - السبب: {reason}"
        payment.save()
        
        return payment
    
    @staticmethod
    def get_member_payment_history(
        member: Member,
        limit: int = 10
    ) -> List[Payment]:
        """
        سجل مدفوعات العضو
        """
        return Payment.objects.filter(
            member=member
        ).select_related(
            'subscription', 
            'invoice'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_overdue_installments() -> List[Installment]:
        """
        الأقساط المتأخرة
        """
        today = timezone.now().date()
        return Installment.objects.filter(
            is_paid=False,
            due_date__lt=today
        ).select_related('payment__member')
    
    @staticmethod
    def get_payment_statistics(
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        إحصائيات المدفوعات
        """
        from django.db.models import Sum, Count, Avg
        
        queryset = Payment.objects.filter(
            status=Payment.PaymentStatus.COMPLETED
        )
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        stats = queryset.aggregate(
            total_revenue=Sum('total'),
            total_tax=Sum('tax'),
            payment_count=Count('id'),
            average_payment=Avg('total')
        )
        
        # تفصيل حسب طريقة الدفع
        by_method = queryset.values('payment_method').annotate(
            total=Sum('total'),
            count=Count('id')
        )
        
        # تفصيل حسب نوع الدفع
        by_type = queryset.values('payment_type').annotate(
            total=Sum('total'),
            count=Count('id')
        )
        
        return {
            **stats,
            'by_payment_method': list(by_method),
            'by_payment_type': list(by_type)
        }
    
    @staticmethod
    def daily_revenue(date_obj: Optional[date] = None) -> Decimal:
        """
        إيرادات اليوم
        """
        if not date_obj:
            date_obj = timezone.now().date()
        
        from django.db.models import Sum
        
        total = Payment.objects.filter(
            status=Payment.PaymentStatus.COMPLETED,
            created_at__date=date_obj
        ).aggregate(total=Sum('total'))['total']
        
        return total or Decimal('0.00')
