from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """مدير المستخدمين المخصص"""
    
    def create_user(self, phone, password=None, **extra_fields):
        """إنشاء مستخدم عادي"""
        if not phone:
            raise ValueError('يجب تقديم رقم هاتف')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """إنشاء مستخدم إداري"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_verified', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('المستخدم الإداري يجب أن يكون is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('المستخدم الإداري يجب أن يكون is_superuser=True')
        
        return self.create_user(phone, password, **extra_fields)
