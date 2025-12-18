from rest_framework import viewsets
from .models import ClassSchedule, ClassSession, ClassBooking
from .serializers import (
    ClassScheduleSerializer,
    ClassSessionSerializer,
    ClassBookingSerializer,
)


class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.select_related('class_type', 'trainer', 'room').all()
    serializer_class = ClassScheduleSerializer


class ClassSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassSession.objects.select_related('schedule').all()
    serializer_class = ClassSessionSerializer


class ClassBookingViewSet(viewsets.ModelViewSet):
    queryset = ClassBooking.objects.select_related('session', 'member').all()
    serializer_class = ClassBookingSerializer