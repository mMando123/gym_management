from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.utils import timezone

from .models import SubscriptionPlan, Package, Subscription
from .serializers import (
    SubscriptionPlanSerializer,
    PackageSerializer,
    SubscriptionListSerializer,
    SubscriptionDetailSerializer,
    SubscriptionCreateSerializer,
    SubscriptionFreezeCreateSerializer,
    SubscriptionRenewSerializer,
    CalculatePriceSerializer
)
from .services import SubscriptionService
from apps.members.models import Member
from apps.sports.models import Sport


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """API خطط الاشتراك"""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """عرض جميع خطط الاشتراك النشطة"""
        return super().list(request, *args, **kwargs)


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    """API الباقات"""
    
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """API الاشتراكات"""
    
    queryset = Subscription.objects.select_related(
        'member__user', 'plan', 'package'
    ).prefetch_related('sports', 'freezes').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'member', 'plan']
    
    def get_serializer_class(self):
        """اختيار Serializer حسب الـ Action"""
        if self.action == 'create':
            return SubscriptionCreateSerializer
        elif self.action == 'retrieve':
            return SubscriptionDetailSerializer
        elif self.action == 'renew':
            return SubscriptionRenewSerializer
        elif self.action == 'freeze':
            return SubscriptionFreezeCreateSerializer
        elif self.action == 'calculate_price':
            return CalculatePriceSerializer
        return SubscriptionListSerializer
    
    def get_queryset(self):
        """تصفية حسب دور المستخدم"""
        user = self.request.user
        
        # المدربون يرون اشتراكات أعضائهم فقط
        if hasattr(user, 'trainer_profile'):
            # جميع الاشتراكات (يمكن تحسينها لاحقاً)
            return super().get_queryset()
        
        # الأعضاء يرون اشتراكاتهم فقط
        if hasattr(user, 'member_profile'):
            return super().get_queryset().filter(member__user=user)
        
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        """إنشاء اشتراك جديد"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            member = Member.objects.get(id=data['member_id'])
            plan = SubscriptionPlan.objects.get(id=data['plan_id'])
            sports = list(Sport.objects.filter(id__in=data['sport_ids']))
            package = None
            if data.get('package_id'):
                package = Package.objects.get(id=data['package_id'])
            
            subscription = SubscriptionService.create_subscription(
                member=member,
                plan=plan,
                sports=sports,
                package=package,
                start_date=data.get('start_date'),
                promo_code=data.get('promo_code', ''),
                payment_method=data.get('payment_method', 'cash'),
                notes=data.get('notes', '')
            )
            
            return Response(
                SubscriptionDetailSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def calculate_price(self, request):
        """حساب سعر الاشتراك"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            plan = SubscriptionPlan.objects.get(id=data['plan_id'])
            sports = list(Sport.objects.filter(id__in=data['sport_ids']))
            package = None
            if data.get('package_id'):
                package = Package.objects.get(id=data['package_id'])
            
            pricing = SubscriptionService.calculate_price(
                plan=plan,
                sports=sports,
                package=package,
                promo_code=data.get('promo_code', '')
            )
            
            return Response(pricing)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        """تجميد الاشتراك"""
        subscription = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            freeze = SubscriptionService.freeze_subscription(
                subscription=subscription,
                days=serializer.validated_data['days'],
                reason=serializer.validated_data['reason'],
                notes=serializer.validated_data.get('notes', '')
            )
            
            return Response({
                'message': 'تم تجميد الاشتراك بنجاح',
                'subscription': SubscriptionDetailSerializer(subscription).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def unfreeze(self, request, pk=None):
        """إلغاء تجميد الاشتراك"""
        subscription = self.get_object()
        
        try:
            SubscriptionService.unfreeze_subscription(subscription)
            return Response({
                'message': 'تم إلغاء تجميد الاشتراك',
                'subscription': SubscriptionDetailSerializer(subscription).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """تجديد الاشتراك"""
        subscription = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            new_subscription = SubscriptionService.renew_subscription(
                subscription=subscription,
                payment_method=serializer.validated_data.get('payment_method', 'cash')
            )
            return Response({
                'message': 'تم تجديد الاشتراك بنجاح',
                'subscription': SubscriptionDetailSerializer(new_subscription).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """الاشتراكات التي ستنتهي قريباً (خلال 7 أيام)"""
        today = timezone.now().date()
        end_date = today + timedelta(days=7)
        
        subscriptions = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            end_date__range=[today, end_date]
        ).select_related('member__user', 'plan')
        
        serializer = SubscriptionListSerializer(subscriptions, many=True)
        return Response({
            'count': subscriptions.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """الاشتراكات النشطة"""
        subscriptions = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE
        ).select_related('member__user', 'plan')
        
        serializer = SubscriptionListSerializer(subscriptions, many=True)
        return Response({
            'count': subscriptions.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """الاشتراكات المنتهية"""
        subscriptions = Subscription.objects.filter(
            status=Subscription.Status.EXPIRED
        ).select_related('member__user', 'plan')
        
        serializer = SubscriptionListSerializer(subscriptions, many=True)
        return Response({
            'count': subscriptions.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def frozen(self, request):
        """الاشتراكات المجمدة"""
        subscriptions = Subscription.objects.filter(
            status=Subscription.Status.FROZEN
        ).select_related('member__user', 'plan')
        
        serializer = SubscriptionListSerializer(subscriptions, many=True)
        return Response({
            'count': subscriptions.count(),
            'results': serializer.data
        })
