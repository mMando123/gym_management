from django import forms
from .models import Attendance
from apps.members.models import Member


class AttendanceCheckInForm(forms.Form):
    """نموذج تسجيل حضور العضو"""
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(user__is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'اختر العضو',
            'id': 'member-select',
            'data-search': 'true'
        }),
        label='العضو'
    )
    
    class Meta:
        model = Attendance
        fields = ['member']


class AttendanceSearchForm(forms.Form):
    """نموذج البحث والفلترة للحضور"""
    member = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'اختر العضو'
        }),
        label='العضو'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'من التاريخ'
        }),
        label='من التاريخ'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'إلى التاريخ'
        }),
        label='إلى التاريخ'
    )


class AttendanceStatsForm(forms.Form):
    """نموذج للحصول على إحصائيات الحضور"""
    period = forms.ChoiceField(
        choices=[
            ('week', 'أسبوع'),
            ('month', 'شهر'),
            ('year', 'سنة'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='الفترة'
    )
    
    member = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='العضو (اختياري)'
    )
