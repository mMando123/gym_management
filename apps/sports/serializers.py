from rest_framework import serializers
from .models import SportCategory, Sport, Belt


class BeltSerializer(serializers.ModelSerializer):
    """سيريلايزر الحزام (نطاق كاراتيه)"""
    
    class Meta:
        model = Belt
        fields = ['id', 'name', 'color', 'order', 'requirements']
        read_only_fields = ['id']


class SportListSerializer(serializers.ModelSerializer):
    """سيريلايزر قائمة الرياضات (محسّن)"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    trainers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sport
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 'image',
            'max_members_per_session', 'session_duration_minutes',
            'has_belt_system', 'trainers_count', 'is_active'
        ]
        read_only_fields = ['id', 'slug']
    
    def get_trainers_count(self, obj):
        """عدد المدربين النشطين"""
        return obj.trainers.filter(is_active=True).count()


class SportDetailSerializer(serializers.ModelSerializer):
    """سيريلايزر تفاصيل الرياضة"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    belts = BeltSerializer(many=True, read_only=True)
    trainers_count = serializers.SerializerMethodField()
    trainers_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Sport
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 'description',
            'image', 'max_members_per_session', 'session_duration_minutes',
            'has_belt_system', 'requires_equipment', 'equipment_details',
            'belts', 'trainers_count', 'trainers_list', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_trainers_count(self, obj):
        """عدد المدربين النشطين"""
        return obj.trainers.filter(is_active=True).count()
    
    def get_trainers_list(self, obj):
        """قائمة أسماء المدربين"""
        trainers = obj.trainers.filter(is_active=True).values_list(
            'user__first_name', 'user__last_name'
        )
        return [f"{first} {last}" for first, last in trainers]


class SportCreateSerializer(serializers.ModelSerializer):
    """سيريلايزر إنشاء رياضة"""
    
    class Meta:
        model = Sport
        fields = [
            'name', 'category', 'description', 'image',
            'max_members_per_session', 'session_duration_minutes',
            'has_belt_system', 'requires_equipment', 'equipment_details'
        ]
    
    def validate_max_members_per_session(self, value):
        """التحقق من أن العدد الأقصى > 0"""
        if value and value <= 0:
            raise serializers.ValidationError("العدد الأقصى يجب أن يكون أكبر من صفر")
        return value
    
    def validate_session_duration_minutes(self, value):
        """التحقق من مدة الجلسة"""
        if value and value < 15:
            raise serializers.ValidationError("مدة الجلسة يجب أن تكون على الأقل 15 دقيقة")
        return value


class SportCategoryListSerializer(serializers.ModelSerializer):
    """سيريلايزر قائمة تصنيفات الرياضة (محسّن)"""
    
    sports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SportCategory
        fields = ['id', 'name', 'icon', 'sports_count', 'is_active']
        read_only_fields = ['id']
    
    def get_sports_count(self, obj):
        """عدد الرياضات النشطة في التصنيف"""
        return obj.sports.filter(is_active=True).count()


class SportCategoryDetailSerializer(serializers.ModelSerializer):
    """سيريلايزر تفاصيل تصنيف الرياضة"""
    
    sports = SportListSerializer(many=True, read_only=True)
    sports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SportCategory
        fields = [
            'id', 'name', 'description', 'icon', 'sports', 'sports_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sports_count(self, obj):
        """عدد الرياضات"""
        return obj.sports.filter(is_active=True).count()


class SportCategoryCreateSerializer(serializers.ModelSerializer):
    """سيريلايزر إنشاء تصنيف رياضة"""
    
    class Meta:
        model = SportCategory
        fields = ['name', 'description', 'icon']
    
    def validate_name(self, value):
        """التحقق من أن الاسم فريد"""
        if SportCategory.objects.filter(name=value).exists():
            raise serializers.ValidationError("هذا التصنيف موجود بالفعل")
        return value
