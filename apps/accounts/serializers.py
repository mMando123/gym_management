from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """سيريلايزر تسجيل الدخول المخصص"""
    
    username_field = 'phone'
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # إضافة بيانات مخصصة للتوكن
        token['phone'] = user.phone
        token['user_type'] = user.user_type
        token['full_name'] = user.get_full_name()
        
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """سيريلايزر تسجيل مستخدم جديد"""
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'phone', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'كلمتا المرور غير متطابقتين'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """سيريلايزر الملف الشخصي"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'is_verified', 'created_at'
        ]
        read_only_fields = ['phone', 'user_type', 'is_verified', 'created_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class ChangePasswordSerializer(serializers.Serializer):
    """سيريلايزر تغيير كلمة المرور"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'كلمتا المرور غير متطابقتين'
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('كلمة المرور الحالية غير صحيحة')
        return value


class PhoneVerificationSerializer(serializers.Serializer):
    """سيريلايزر التحقق من الهاتف"""
    
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)


class OTPRequestSerializer(serializers.Serializer):
    """سيريلايزر طلب كود التحقق"""
    
    phone = serializers.CharField(max_length=15)


class OTPVerifySerializer(serializers.Serializer):
    """سيريلايزر التحقق من الكود"""
    
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
