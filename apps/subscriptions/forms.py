from django import forms
from .models import Subscription, SubscriptionPlan, Package
from django.utils import timezone


class SubscriptionForm(forms.ModelForm):
    """نموذج إضافة اشتراك"""
    
    class Meta:
        model = Subscription
        fields = ['plan', 'start_date']
        widgets = {
            'plan': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'اختر الخطة'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'تاريخ البداية'
            }),
        }


class SubscriptionFreezeForm(forms.Form):
    """نموذج تجميد الاشتراك"""
    
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'السبب (اختياري)'
        })
    )
    freeze_days = forms.IntegerField(
        initial=7,
        min_value=1,
        max_value=90,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'عدد أيام التجميد'
        })
    )


class SubscriptionPlanForm(forms.ModelForm):
    """نموذج إدارة خطط الاشتراك"""
    
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'name_ar', 'description', 'price', 'duration_days', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم بالإنجليزية'}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم بالعربية'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'السعر'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مدة الاشتراك بالأيام'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
