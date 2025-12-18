from django import forms
from .models import Member, MemberBodyMetrics
from django.contrib.auth import get_user_model

User = get_user_model()


class MemberForm(forms.ModelForm):
    """نموذج إضافة/تعديل العضو"""
    
    class Meta:
        model = Member
        fields = [
            'date_of_birth',
            'gender',
            'national_id',
            'address',
            'height',
            'weight',
            'blood_type',
            'medical_conditions',
            'emergency_contact_name',
            'emergency_contact_phone',
            'photo',
            'is_active',
            'notes',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'تاريخ الميلاد'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'اختر النوع'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهوية (اختياري)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'الطول (سم)'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'الوزن (كجم)'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'فصيلة الدم'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'الحالات الصحية'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم جهة الاتصال للطوارئ'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم هاتف الطوارئ'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'id': 'id_photo',
                'data-preview-id': 'imagePreview',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }


class MemberBodyMetricsForm(forms.ModelForm):
    """نموذج تسجيل قياسات جسم العضو"""
    
    class Meta:
        model = MemberBodyMetrics
        fields = ['weight', 'chest', 'waist', 'hips', 'notes']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الوزن (كج)',
                'step': '0.1'
            }),
            'chest': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'محيط الصدر (سم)',
                'step': '0.1',
                'required': False
            }),
            'waist': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'محيط الخصر (سم)',
                'step': '0.1',
                'required': False
            }),
            'hips': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'محيط الأرداف (سم)',
                'step': '0.1',
                'required': False
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ملاحظات',
                'required': False
            }),
        }


class UserProfileForm(forms.ModelForm):
    """نموذج تحديث بيانات المستخدم"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم العائلة'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '05xxxxxxxx'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
        }


class MemberSearchForm(forms.Form):
    """نموذج البحث والفلترة"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث بالاسم أو الهاتف...'
        })
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[('', '--- جميع الأنواع ---'), ('M', 'ذكور'), ('F', 'إناث')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', '--- جميع الحالات ---'), ('active', 'نشط'), ('inactive', 'غير نشط')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
