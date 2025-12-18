from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from .models import SportCategory, Sport, Belt
from .serializers import (
    SportCategoryListSerializer,
    SportCategoryDetailSerializer,
    SportCategoryCreateSerializer,
    SportListSerializer,
    SportDetailSerializer,
    SportCreateSerializer,
    BeltSerializer
)


class SportCategoryViewSet(viewsets.ModelViewSet):
    """API تصنيفات الرياضات - عرض وإدارة التصنيفات"""
    
    queryset = SportCategory.objects.annotate(
        sports_count=Count('sports', filter=Q(sports__is_active=True))
    ).filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        """اختيار الـ Serializer بناءً على الـ Action"""
        if self.action in ['list']:
            return SportCategoryListSerializer
        elif self.action in ['retrieve']:
            return SportCategoryDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SportCategoryCreateSerializer
        return SportCategoryDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """قائمة التصنيفات"""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """تفاصيل التصنيف مع الرياضات"""
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """إنشاء تصنيف جديد"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        category = SportCategory.objects.get(id=serializer.data['id'])
        response_serializer = SportCategoryDetailSerializer(category)
        
        return Response({
            'message': 'تم إنشاء التصنيف بنجاح',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def active_categories(self, request):
        """التصنيفات النشطة فقط"""
        categories = self.queryset.filter(is_active=True)
        serializer = SportCategoryListSerializer(categories, many=True)
        
        return Response({
            'count': len(categories),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def sports(self, request, pk=None):
        """الرياضات في التصنيف
        
        Parameters:
        - is_active (اختياري): تصفية حسب الحالة
        """
        try:
            category = self.get_object()
            sports = category.sports.all()
            
            is_active = request.query_params.get('is_active')
            if is_active is not None:
                is_active = is_active.lower() == 'true'
                sports = sports.filter(is_active=is_active)
            
            serializer = SportListSerializer(sports, many=True)
            return Response({
                'category': category.name,
                'count': len(sports),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except SportCategory.DoesNotExist:
            return Response(
                {'error': 'التصنيف غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )


class SportViewSet(viewsets.ModelViewSet):
    """API الرياضات - عرض وإدارة الرياضات والأحزمة"""
    
    queryset = Sport.objects.select_related('category').prefetch_related(
        'trainers', 'belts'
    ).filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'has_belt_system', 'requires_equipment', 'is_active']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """اختيار الـ Serializer بناءً على الـ Action"""
        if self.action in ['list']:
            return SportListSerializer
        elif self.action in ['retrieve']:
            return SportDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SportCreateSerializer
        return SportDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """قائمة الرياضات"""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """تفاصيل رياضة مع المدربين والأحزمة"""
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """إنشاء رياضة جديدة"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        sport = Sport.objects.get(id=serializer.data['id'])
        response_serializer = SportDetailSerializer(sport)
        
        return Response({
            'message': 'تم إنشاء الرياضة بنجاح',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def with_belts(self, request):
        """الرياضات التي بها نظام أحزمة"""
        sports = self.queryset.filter(has_belt_system=True)
        serializer = SportListSerializer(sports, many=True)
        
        return Response({
            'count': len(sports),
            'message': 'رياضات بنظام الأحزمة',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def requiring_equipment(self, request):
        """الرياضات التي تتطلب معدات"""
        sports = self.queryset.filter(requires_equipment=True)
        serializer = SportListSerializer(sports, many=True)
        
        return Response({
            'count': len(sports),
            'message': 'رياضات تتطلب معدات',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def belts(self, request, slug=None):
        """أحزمة الرياضة
        
        المعاملات:
        - slug: معرّف الرياضة (مثل: karate)
        """
        try:
            sport = self.get_object()
            
            if not sport.has_belt_system:
                return Response(
                    {'error': 'هذه الرياضة لا تحتوي على نظام أحزمة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            belts = sport.belts.all().order_by('order')
            serializer = BeltSerializer(belts, many=True)
            
            return Response({
                'sport': sport.name,
                'count': len(belts),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Sport.DoesNotExist:
            return Response(
                {'error': 'الرياضة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def trainers(self, request, slug=None):
        """مدربو الرياضة
        
        المعاملات:
        - slug: معرّف الرياضة
        """
        try:
            sport = self.get_object()
            trainers = sport.trainers.filter(is_active=True).select_related('user')
            
            trainer_data = [
                {
                    'id': trainer.id,
                    'name': trainer.user.get_full_name(),
                    'phone': trainer.user.phone,
                    'specializations': [
                        s.name for s in trainer.specializations.all()
                    ],
                    'rating': trainer.average_rating,
                    'is_active': trainer.is_active
                }
                for trainer in trainers
            ]
            
            return Response({
                'sport': sport.name,
                'count': len(trainer_data),
                'data': trainer_data
            }, status=status.HTTP_200_OK)
            
        except Sport.DoesNotExist:
            return Response(
                {'error': 'الرياضة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def sessions_info(self, request, slug=None):
        """معلومات جلسات الرياضة
        
        المعاملات:
        - slug: معرّف الرياضة
        """
        try:
            sport = self.get_object()
            
            return Response({
                'sport': sport.name,
                'data': {
                    'session_duration_minutes': sport.session_duration_minutes,
                    'max_members_per_session': sport.max_members_per_session,
                    'description': sport.description,
                    'requires_equipment': sport.requires_equipment,
                    'equipment_details': sport.equipment_details
                }
            }, status=status.HTTP_200_OK)
            
        except Sport.DoesNotExist:
            return Response(
                {'error': 'الرياضة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """الرياضات الشهيرة (الأكثر أعضاء)
        
        المعاملات:
        - limit (اختياري): عدد النتائج (افتراضي: 10)
        """
        try:
            limit = int(request.query_params.get('limit', 10))
            
            # يمكن إضافة logic أكثر تعقيداً هنا
            # مثل: عدد الاشتراكات، عدد الجلسات، إلخ
            sports = self.queryset.annotate(
                sessions_count=Count('classchedule')
            ).order_by('-sessions_count')[:limit]
            
            serializer = SportListSerializer(sports, many=True)
            
            return Response({
                'message': 'الرياضات الشهيرة',
                'count': len(sports),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'القيم المدخلة غير صحيحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """البحث عن رياضات
        
        المعاملات:
        - q: كلمة البحث (اسم أو وصف)
        - category_id (اختياري): تصفية حسب التصنيف
        """
        query = request.query_params.get('q', '').strip()
        category_id = request.query_params.get('category_id')
        
        if not query:
            return Response(
                {'error': 'يجب إدخال كلمة البحث'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sports = self.queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            
            if category_id:
                sports = sports.filter(category_id=category_id)
            
            serializer = SportListSerializer(sports, many=True)
            
            return Response({
                'query': query,
                'count': len(sports),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
