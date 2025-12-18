from django import forms
from .models import Locker, LockerRental
from apps.members.models import Member


class LockerForm(forms.ModelForm):
    """فورم إضافة/تعديل خزانة"""
    
    class Meta:
        model = Locker
        fields = ['locker_number', 'size', 'location', 'daily_rate', 'monthly_rate', 'status', 'notes']
        widgets = {
            'locker_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: L001'
            }),
            'size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: الطابق الأول - قسم الرجال'
            }),
            'daily_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'monthly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية...'
            }),
        }


class LockerRentalForm(forms.ModelForm):
    """فورم تأجير خزانة"""
    
    class Meta:
        model = LockerRental
        fields = ['locker', 'member', 'rental_type', 'start_date', 'end_date', 'price']
        widgets = {
            'locker': forms.Select(attrs={
                'class': 'form-select'
            }),
            'member': forms.Select(attrs={
                'class': 'form-select'
            }),
            'rental_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'rental-type'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'rental-price'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # فقط الخزائن المتاحة
        self.fields['locker'].queryset = Locker.objects.filter(status=Locker.Status.AVAILABLE)
        # فقط الأعضاء النشطين
        self.fields['member'].queryset = Member.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        locker = cleaned_data.get('locker')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

        # التحقق من عدم وجود إيجار نشط لنفس الخزانة في نفس الفترة
        if locker and start_date and end_date:
            overlapping = LockerRental.objects.filter(
                locker=locker,
                is_active=True,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            if overlapping.exists():
                raise forms.ValidationError('يوجد إيجار نشط لهذه الخزانة في هذه الفترة')

        return cleaned_data


class QuickRentalForm(forms.Form):
    """فورم سريع لتأجير خزانة من صفحة الخزائن"""
    
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(is_active=True),
        label='العضو',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    rental_type = forms.ChoiceField(
        choices=LockerRental.RentalType.choices,
        label='نوع الإيجار',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        label='تاريخ البداية',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
