import django_filters
from datetime import date
from django.db.models import Q
from .models import Member


class MemberFilter(django_filters.FilterSet):
    """فلترة الأعضاء"""
    
    # الفلاتر الأساسية
    gender = django_filters.ChoiceFilter(
        choices=Member.Gender.choices,
        label='الجنس'
    )
    is_active = django_filters.BooleanFilter(label='نشط')
    blood_type = django_filters.ChoiceFilter(
        choices=Member.BloodType.choices,
        label='فصيلة الدم'
    )
    
    # فلاتر التاريخ
    join_date_from = django_filters.DateFilter(
        field_name='join_date',
        lookup_expr='gte',
        label='من تاريخ الانضمام'
    )
    join_date_to = django_filters.DateFilter(
        field_name='join_date',
        lookup_expr='lte',
        label='إلى تاريخ الانضمام'
    )
    
    # فلاتر العمر
    age_min = django_filters.NumberFilter(
        method='filter_age_min',
        label='الحد الأدنى للعمر'
    )
    age_max = django_filters.NumberFilter(
        method='filter_age_max',
        label='الحد الأقصى للعمر'
    )
    
    # البحث
    search = django_filters.CharFilter(
        method='filter_search',
        label='البحث'
    )
    
    class Meta:
        model = Member
        fields = ['gender', 'is_active', 'blood_type']
    
    def filter_age_min(self, queryset, name, value):
        """فلترة العمر الأدنى"""
        try:
            max_birth_date = date.today().replace(year=date.today().year - int(value))
            return queryset.filter(date_of_birth__lte=max_birth_date)
        except (ValueError, TypeError):
            return queryset
    
    def filter_age_max(self, queryset, name, value):
        """فلترة العمر الأقصى"""
        try:
            min_birth_date = date.today().replace(year=date.today().year - int(value) - 1)
            return queryset.filter(date_of_birth__gte=min_birth_date)
        except (ValueError, TypeError):
            return queryset
    
    def filter_search(self, queryset, name, value):
        """البحث في الاسم والهاتف والبريد"""
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__phone__icontains=value) |
            Q(user__email__icontains=value)
        )
