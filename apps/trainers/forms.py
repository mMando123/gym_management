from django import forms
from .models import Trainer, TrainerAvailability, Specialization
from apps.subscriptions.models import SubscriptionPlan


class TrainerForm(forms.ModelForm):
    """نموذج إضافة/تعديل مدرب"""
    specialization = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='التخصصات'
    )

    class Meta:
        model = Trainer
        fields = ['user', 'specialization', 'certifications', 'years_of_experience', 'bio']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'الشهادات والدورات'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'نبذة عن المدرب'
            })
        }


class TrainerAvailabilityForm(forms.ModelForm):
    """نموذج ساعات عمل المدرب"""
    
    class Meta:
        model = TrainerAvailability
        fields = ['trainer', 'day_of_week', 'start_time', 'end_time']
        widgets = {
            'trainer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'day_of_week': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            })
        }


class TrainerSearchForm(forms.Form):
    """نموذج البحث عن مدرب"""
    name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث بالاسم'
        }),
        label='الاسم'
    )
    
    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='التخصص'
    )
    
    is_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='متاح فقط'
    )


class SessionBookingForm(forms.Form):
    """نموذج حجز جلسة تدريب"""
    trainer = forms.ModelChoiceField(
        queryset=Trainer.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='المدرب'
    )
    
    session_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='تاريخ الجلسة'
    )
    
    session_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        label='وقت الجلسة'
    )
    
    duration = forms.ChoiceField(
        choices=[(30, '30 دقيقة'), (45, '45 دقيقة'), (60, 'ساعة واحدة'), (90, 'ساعة ونصف')],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='مدة الجلسة'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ملاحظات إضافية'
        }),
        label='الملاحظات'
    )
