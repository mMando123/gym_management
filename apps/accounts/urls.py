from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('otp/request/', views.OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', views.OTPVerifyView.as_view(), name='otp-verify'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
