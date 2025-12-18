from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer
)
from .models import OTP

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """عرض تسجيل الدخول المخصص"""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """عرض تسجيل مستخدم جديد"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'تم التسجيل بنجاح',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """عرض وتعديل الملف الشخصي"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """عرض تغيير كلمة المرور"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return Response({'message': 'تم تغيير كلمة المرور بنجاح'})


class OTPRequestView(APIView):
    """طلب كود التحقق عبر SMS"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone']
        
        # التحقق من وجود المستخدم
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({
                'error': 'رقم الهاتف غير مسجل'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # إنشاء كود التحقق
        otp = OTP.create_otp(user)
        
        # هنا يتم إرسال الكود عبر SMS (مثلاً Twilio)
        # send_sms(phone, f"كود التحقق: {otp.code}")
        
        return Response({
            'message': 'تم إرسال كود التحقق إلى رقم الهاتف',
            'phone': phone
        })


class OTPVerifyView(APIView):
    """التحقق من كود OTP"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        
        # البحث عن المستخدم
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({
                'error': 'رقم الهاتف غير مسجل'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # البحث عن الكود
        try:
            otp = OTP.objects.get(user=user, code=code)
        except OTP.DoesNotExist:
            return Response({
                'error': 'كود التحقق غير صحيح'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من صحة الكود
        if not otp.is_valid():
            return Response({
                'error': 'انتهت صلاحية الكود'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # تعليم الكود كمستخدم
        otp.is_used = True
        otp.save()
        
        # تعليم المستخدم كمتحقق
        user.is_verified = True
        user.save()
        
        return Response({
            'message': 'تم التحقق بنجاح',
            'user': UserProfileSerializer(user).data
        })


class LogoutView(APIView):
    """تسجيل الخروج"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        return Response({
            'message': 'تم تسجيل الخروج بنجاح'
        })
