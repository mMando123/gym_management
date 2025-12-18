from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Attendance, GuestVisit
from .serializers import (
    AttendanceListSerializer,
    AttendanceDetailSerializer,
    CheckInSerializer,
    CheckOutSerializer,
    GuestVisitListSerializer,
    GuestVisitDetailSerializer,
    GuestCheckInSerializer,
    GuestCheckOutSerializer,
    AttendanceStatisticsSerializer,
    AttendanceRateSerializer
)
from .services import AttendanceService
from apps.members.models import Member
from apps.sports.models import Sport
from apps.trainers.models import Trainer


class AttendanceViewSet(viewsets.ModelViewSet):
    """API الحضور - تسجيل الدخول والخروج والإحصائيات"""
    
    queryset = Attendance.objects.select_related(
        'member__user', 'sport', 'trainer__user', 'subscription'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['member', 'sport', 'trainer']
    
    def get_serializer_class(self):
        """اختيار الـ Serializer بناءً على الـ Action"""
        if self.action in ['list', 'current', 'member_attendance']:
            return AttendanceListSerializer
        elif self.action in ['retrieve']:
            return AttendanceDetailSerializer
        elif self.action in ['check_in']:
            return CheckInSerializer
        elif self.action in ['check_out']:
            return CheckOutSerializer
        return AttendanceDetailSerializer
    
    def get_queryset(self):
        """تصفية حسب دور المستخدم"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # الأعضاء يرون حضورهم فقط
        if hasattr(user, 'member_profile'):
            queryset = queryset.filter(member__user=user)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """قائمة الحضور"""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """تفاصيل حضور محدد"""
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """تسجيل دخول العضو
        
        Parameters:
        - member_id: معرف العضو
        - sport_id: معرف الرياضة
        - trainer_id (اختياري): معرف المدرب
        - notes (اختياري): ملاحظات
        """
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            member = Member.objects.get(id=serializer.validated_data['member_id'])
            sport = Sport.objects.get(id=serializer.validated_data['sport_id'])
            trainer = None
            notes = serializer.validated_data.get('notes', '')
            
            if serializer.validated_data.get('trainer_id'):
                trainer = Trainer.objects.get(
                    id=serializer.validated_data['trainer_id']
                )
            
            # تسجيل الدخول عبر الخدمة
            attendance = AttendanceService.check_in(
                member=member,
                sport=sport,
                trainer=trainer,
                notes=notes
            )
            
            response_serializer = AttendanceDetailSerializer(attendance)
            return Response({
                'message': 'تم تسجيل الدخول بنجاح',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Member.DoesNotExist:
            return Response(
                {'error': 'العضو غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Sport.DoesNotExist:
            return Response(
                {'error': 'الرياضة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Trainer.DoesNotExist:
            return Response(
                {'error': 'المدرب غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """تسجيل خروج العضو
        
        Parameters:
        - attendance_id أو member_id: معرف الحضور أو العضو
        - notes (اختياري): ملاحظات
        """
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            attendance = None
            
            # محاولة الحصول على سجل الحضور
            if serializer.validated_data.get('attendance_id'):
                attendance = Attendance.objects.get(
                    id=serializer.validated_data['attendance_id']
                )
            elif serializer.validated_data.get('member_id'):
                member = Member.objects.get(
                    id=serializer.validated_data['member_id']
                )
                attendance = AttendanceService.check_out(member=member)
            
            if not attendance:
                return Response(
                    {'error': 'لم يتم العثور على سجل حضور نشط'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response_serializer = AttendanceDetailSerializer(attendance)
            return Response({
                'message': 'تم تسجيل الخروج بنجاح',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Member.DoesNotExist:
            return Response(
                {'error': 'العضو غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'سجل الحضور غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """الأعضاء الموجودون حالياً في الجيم"""
        sport_id = request.query_params.get('sport_id')
        sport = None
        
        try:
            if sport_id:
                sport = Sport.objects.get(id=sport_id)
            
            attendees = AttendanceService.get_current_attendees(sport)
            serializer = AttendanceListSerializer(attendees, many=True)
            
            return Response({
                'count': len(attendees),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Sport.DoesNotExist:
            return Response(
                {'error': 'الرياضة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات الحضور
        
        Parameters:
        - start_date (اختياري): تاريخ البداية
        - end_date (اختياري): تاريخ النهاية
        - sport_id (اختياري): معرف الرياضة
        """
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            sport_id = request.query_params.get('sport_id')
            
            sport = None
            if sport_id:
                sport = Sport.objects.get(id=sport_id)
            
            stats = AttendanceService.get_attendance_statistics(
                start_date=start_date,
                end_date=end_date,
                sport=sport
            )
            
            serializer = AttendanceStatisticsSerializer(stats)
            return Response({
                'message': 'إحصائيات الحضور',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Sport.DoesNotExist:
            return Response(
                {'error': 'الرياضة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def peak_hours(self, request):
        """ساعات الذروة في الجيم
        
        Parameters:
        - days (اختياري): عدد الأيام (افتراضي: 30)
        """
        try:
            days = int(request.query_params.get('days', 30))
            peak_hours = AttendanceService.get_peak_hours(days)
            
            return Response({
                'message': 'ساعات الذروة',
                'data': peak_hours
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'عدد الأيام يجب أن يكون رقماً'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def member_attendance(self, request):
        """سجل حضور العضو
        
        Parameters:
        - member_id (اختياري): معرف العضو (افتراضي: العضو الحالي)
        - limit (اختياري): عدد السجلات (افتراضي: 50)
        """
        try:
            member_id = request.query_params.get('member_id')
            limit = int(request.query_params.get('limit', 50))
            
            if not member_id:
                # إذا كان العضو الحالي
                if hasattr(request.user, 'member_profile'):
                    member = request.user.member_profile
                else:
                    return Response(
                        {'error': 'أنت لست عضواً في الجيم'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                member = Member.objects.get(id=member_id)
            
            history = AttendanceService.get_member_attendance_history(
                member=member,
                limit=limit
            )
            
            serializer = AttendanceListSerializer(history, many=True)
            return Response({
                'count': len(history),
                'member_id': member.id,
                'member_name': member.user.get_full_name(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Member.DoesNotExist:
            return Response(
                {'error': 'العضو غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'القيم المدخلة غير صحيحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def attendance_rate(self, request):
        """معدل حضور العضو
        
        Parameters:
        - member_id (اختياري): معرف العضو
        - days (اختياري): عدد الأيام (افتراضي: 30)
        """
        try:
            member_id = request.query_params.get('member_id')
            days = int(request.query_params.get('days', 30))
            
            if not member_id:
                if hasattr(request.user, 'member_profile'):
                    member = request.user.member_profile
                else:
                    return Response(
                        {'error': 'أنت لست عضواً في الجيم'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                member = Member.objects.get(id=member_id)
            
            rate = AttendanceService.get_attendance_rate(member=member, days=days)
            serializer = AttendanceRateSerializer(rate)
            
            return Response({
                'message': 'معدل الحضور',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Member.DoesNotExist:
            return Response(
                {'error': 'العضو غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'القيم المدخلة غير صحيحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GuestVisitViewSet(viewsets.ModelViewSet):
    """API زيارات الضيوف - تسجيل الدخول والخروج"""
    
    queryset = GuestVisit.objects.select_related('host_member__user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['host_member', 'visit_date']
    
    def get_serializer_class(self):
        """اختيار الـ Serializer بناءً على الـ Action"""
        if self.action in ['list']:
            return GuestVisitListSerializer
        elif self.action in ['retrieve']:
            return GuestVisitDetailSerializer
        elif self.action in ['check_in']:
            return GuestCheckInSerializer
        elif self.action in ['check_out']:
            return GuestCheckOutSerializer
        return GuestVisitDetailSerializer
    
    def get_queryset(self):
        """تصفية حسب دور المستخدم"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # الأعضاء يرون ضيوفهم فقط
        if hasattr(user, 'member_profile'):
            queryset = queryset.filter(host_member__user=user)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """قائمة زيارات الضيوف"""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """تفاصيل زيارة ضيف"""
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """تسجيل دخول ضيف
        
        Parameters:
        - host_member_id: معرف العضو المضيف
        - guest_name: اسم الضيف
        - guest_phone: هاتف الضيف
        """
        serializer = GuestCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            member = Member.objects.get(
                id=serializer.validated_data['host_member_id']
            )
            
            # التحقق من وجود باقة ضيوف
            visit = AttendanceService.record_guest_visit(
                host_member=member,
                guest_name=serializer.validated_data['guest_name'],
                guest_phone=serializer.validated_data['guest_phone']
            )
            
            response_serializer = GuestVisitDetailSerializer(visit)
            return Response({
                'message': 'تم تسجيل دخول الضيف بنجاح',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Member.DoesNotExist:
            return Response(
                {'error': 'العضو المضيف غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """تسجيل خروج ضيف
        
        Parameters:
        - visit_id: معرف سجل الزيارة
        """
        serializer = GuestCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            visit = GuestVisit.objects.get(
                id=serializer.validated_data['visit_id']
            )
            
            # تسجيل الخروج
            visit = AttendanceService.checkout_guest(visit=visit)
            
            response_serializer = GuestVisitDetailSerializer(visit)
            return Response({
                'message': 'تم تسجيل خروج الضيف بنجاح',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except GuestVisit.DoesNotExist:
            return Response(
                {'error': 'سجل الزيارة غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def member_guests(self, request):
        """زيارات ضيوف العضو
        
        Parameters:
        - member_id (اختياري): معرف العضو
        - limit (اختياري): عدد السجلات (افتراضي: 50)
        """
        try:
            member_id = request.query_params.get('member_id')
            limit = int(request.query_params.get('limit', 50))
            
            if not member_id:
                if hasattr(request.user, 'member_profile'):
                    member = request.user.member_profile
                else:
                    return Response(
                        {'error': 'أنت لست عضواً في الجيم'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                member = Member.objects.get(id=member_id)
            
            visits = GuestVisit.objects.filter(
                host_member=member
            ).select_related('host_member__user').order_by('-visit_date')[:limit]
            
            serializer = GuestVisitListSerializer(visits, many=True)
            return Response({
                'count': len(visits),
                'member_id': member.id,
                'member_name': member.user.get_full_name(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Member.DoesNotExist:
            return Response(
                {'error': 'العضو غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'القيم المدخلة غير صحيحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
