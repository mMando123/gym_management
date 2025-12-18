from django import forms
from .models import Payment, Invoice, InstallmentPlan
from apps.members.models import Member


class PaymentForm(forms.ModelForm):
    """نموذج إضافة دفعة جديدة"""
    
    class Meta:
        model = Payment
        fields = ['member', 'amount', 'payment_method', 'notes']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'اختر العضو'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'المبلغ',
                'min': '0',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            })
        }


class PaymentSearchForm(forms.Form):
    """نموذج البحث والفلترة للدفعات"""
    member = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='العضو'
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'نقد'),
            ('card', 'بطاقة'),
            ('bank', 'تحويل بنكي'),
            ('check', 'شيك'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='طريقة الدفع'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='من التاريخ'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='إلى التاريخ'
    )


class InvoiceForm(forms.ModelForm):
    """نموذج إنشاء فاتورة"""
    
    class Meta:
        model = Invoice
        fields = [
            'payment',
            'due_date',
            'subtotal',
            'discount',
            'tax',
            'total',
            'is_paid'
        ]
        widgets = {
            'payment': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'subtotal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'tax': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class InstallmentPlanForm(forms.ModelForm):
    """نموذج خطة التقسيط"""
    
    class Meta:
        model = InstallmentPlan
        fields = ['member', 'total_amount', 'installment_count', 'start_date', 'notes']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'installment_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '24'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
