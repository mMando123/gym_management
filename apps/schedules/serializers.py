from rest_framework import serializers
from .models import ClassSchedule, ClassSession, ClassBooking


class ClassScheduleSerializer(serializers.ModelSerializer):
    """Serializer لجدول الحصص"""
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    trainer_name = serializers.CharField(source='trainer.user.get_full_name', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'sport', 'sport_name', 'trainer', 'trainer_name',
            'name', 'day_of_week', 'day_name', 'start_time', 'end_time',
            'max_participants', 'difficulty_level', 'room', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ClassSessionSerializer(serializers.ModelSerializer):
    """Serializer للحصص الفعلية"""
    schedule_info = ClassScheduleSerializer(source='schedule', read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ClassSession
        fields = [
            'id', 'schedule', 'schedule_info', 'date', 'status',
            'actual_trainer', 'participants_count', 'notes',
            'available_spots', 'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'participants_count']


class ClassBookingSerializer(serializers.ModelSerializer):
    """Serializer لحجوزات الحصص"""
    session_info = ClassSessionSerializer(source='session', read_only=True)
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = ClassBooking
        fields = [
            'id', 'session', 'session_info', 'member', 'member_name',
            'status', 'booked_at', 'cancelled_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['booked_at', 'cancelled_at', 'created_at', 'updated_at']