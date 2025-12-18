import os
import django
from django.conf import settings
import pytest
from django.test.utils import get_unique_databases_and_mirrors
from django.db import connections

# تهيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from django.contrib.auth import get_user_model
from apps.members.models import Member, MemberBodyMetrics
from apps.sports.models import SportCategory, Sport
from apps.subscriptions.models import SubscriptionPlan, Package
from apps.trainers.models import Trainer
from apps.attendance.models import Attendance

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup():
    """إعداد قاعدة بيانات الاختبار"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def user_factory():
    """مصنع لإنشاء مستخدمين"""
    def _create_user(**kwargs):
        defaults = {
            'phone': '+966501234567',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        
        phone = defaults.pop('phone')
        password = defaults.pop('password')
        
        user = User.objects.create_user(phone=phone, **defaults)
        user.set_password(password)
        user.save()
        return user
    
    return _create_user


@pytest.fixture
def admin_user(user_factory):
    """إنشاء مستخدم إداري"""
    return user_factory(
        phone='+966501234568',
        is_staff=True,
        is_superuser=True,
        role='ADMIN'
    )


@pytest.fixture
def trainer_user(user_factory):
    """إنشاء مستخدم مدرب"""
    user = user_factory(
        phone='+966501234569',
        role='TRAINER'
    )
    Trainer.objects.create(user=user, experience_years=5)
    return user


@pytest.fixture
def member_user(user_factory):
    """إنشاء مستخدم عضو"""
    user = user_factory(
        phone='+966501234570',
        role='MEMBER'
    )
    member = Member.objects.create(
        user=user,
        date_of_birth='1990-01-01',
        gender='M',
        address='123 Main St'
    )
    return user


@pytest.fixture
def member(member_user):
    """الحصول على كائن العضو"""
    return member_user.member


@pytest.fixture
def sport_category():
    """إنشاء فئة رياضة"""
    return SportCategory.objects.create(
        name='تمارين اللياقة البدنية',
        name_ar='تمارين اللياقة البدنية',
        description='تمارين عامة للياقة البدنية'
    )


@pytest.fixture
def sport(sport_category):
    """إنشاء رياضة"""
    return Sport.objects.create(
        category=sport_category,
        name='الجري',
        name_ar='الجري',
        description='تمارين الجري',
        slug='running'
    )


@pytest.fixture
def subscription_plan():
    """إنشاء خطة اشتراك"""
    return SubscriptionPlan.objects.create(
        name='الخطة الذهبية',
        name_ar='الخطة الذهبية',
        price=200.0,
        duration_days=30,
        description='خطة شاملة مع جميع المميزات',
        is_active=True
    )


@pytest.fixture
def package(sport):
    """إنشاء حزمة رياضية"""
    package = Package.objects.create(
        name='حزمة الجري الأسبوعية',
        name_ar='حزمة الجري الأسبوعية',
        description='حزمة شاملة لتمارين الجري',
        price=50.0,
        sessions_per_week=3
    )
    package.sports.add(sport)
    return package


@pytest.mark.django_db
class TestBase:
    """فئة أساسية للاختبارات"""
    
    @staticmethod
    def create_test_user(phone='+966501234567', **kwargs):
        """إنشاء مستخدم اختبار"""
        defaults = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
        }
        defaults.update(kwargs)
        user = User.objects.create_user(phone=phone, **defaults)
        return user
    
    @staticmethod
    def create_test_member(user=None, **kwargs):
        """إنشاء عضو اختبار"""
        if not user:
            user = User.objects.create_user(phone='+966501234567')
        
        defaults = {
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'address': '123 Main St'
        }
        defaults.update(kwargs)
        
        return Member.objects.create(user=user, **defaults)


# تكوينات pytest
def pytest_configure(config):
    """تكوين pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')


@pytest.fixture
def api_client():
    """عميل REST API"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user_factory):
    """عميل API مصرح به"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    user = user_factory()
    refresh = RefreshToken.for_user(user)
    
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    
    return api_client, user
