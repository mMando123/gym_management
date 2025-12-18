from rest_framework import serializers
from .models import Attendance, GuestVisit


class AttendanceListSerializer(serializers.ModelSerializer):
    """سيريلايزر قائمة الحضور (محسّن)"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_checked_out = serializers.ReadOnlyField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'member_name', 'sport_name', 'check_in',
            'check_out', 'duration_minutes', 'is_checked_out'
        ]


class AttendanceDetailSerializer(serializers.ModelSerializer):
    """سيريلايزر تفاصيل الحضور"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    trainer_name = serializers.SerializerMethodField()
    duration_minutes = serializers.ReadOnlyField()
    is_checked_out = serializers.ReadOnlyField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'member', 'member_name', 'member_id', 'subscription',
            'sport', 'sport_name', 'trainer', 'trainer_name',
            'check_in', 'check_out', 'duration_minutes',
            'is_manual_entry', 'notes', 'is_checked_out', 'created_at'
        ]
        read_only_fields = [
            'subscription', 'check_in', 'check_out',
            'created_at', 'is_manual_entry'
        ]
    
    def get_trainer_name(self, obj):
        """الحصول على اسم المدرب"""
        if obj.trainer:
            return obj.trainer.user.get_full_name()
        return None


class CheckInSerializer(serializers.Serializer):
    """سيريلايزر تسجيل الدخول"""
    
    member_id = serializers.IntegerField()
    sport_id = serializers.IntegerField()
    trainer_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_member_id(self, value):
        """التحقق من وجود العضو"""
        from apps.members.models import Member
        try:
            Member.objects.get(id=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("العضو غير موجود")
        return value
    
    def validate_sport_id(self, value):
        """التحقق من وجود الرياضة"""
        from apps.sports.models import Sport
        try:
            Sport.objects.get(id=value, is_active=True)
        except Sport.DoesNotExist:
            raise serializers.ValidationError("الرياضة غير موجودة")
        return value
    
    def validate_trainer_id(self, value):
        """التحقق من وجود المدرب"""
        if value:
            from apps.trainers.models import Trainer
            try:
                Trainer.objects.get(id=value, is_active=True)
            except Trainer.DoesNotExist:
                raise serializers.ValidationError("المدرب غير موجود")
        return value


class CheckOutSerializer(serializers.Serializer):
    """سيريلايزر تسجيل الخروج"""
    
    attendance_id = serializers.IntegerField(required=False, allow_null=True)
    member_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """التحقق من توفر معرف الحضور أو العضو"""
        if not data.get('attendance_id') and not data.get('member_id'):
            raise serializers.ValidationError(
                "يجب توفير إما attendance_id أو member_id"
            )
        return data


class GuestVisitListSerializer(serializers.ModelSerializer):
    """سيريلايزر قائمة زيارات الضيوف"""
    
    host_member_name = serializers.CharField(
        source='host_member.user.get_full_name',
        read_only=True
    )
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = GuestVisit
        fields = [
            'id', 'host_member_name', 'guest_name',
            'visit_date', 'check_in', 'check_out', 'duration_minutes'
        ]


class GuestVisitDetailSerializer(serializers.ModelSerializer):
    """سيريلايزر تفاصيل زيارة الضيف"""
    
    host_member_name = serializers.CharField(
        source='host_member.user.get_full_name',
        read_only=True
    )
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = GuestVisit
        fields = [
            'id', 'host_member', 'host_member_name', 'guest_name',
            'guest_phone', 'visit_date', 'check_in', 'check_out',
            'duration_minutes', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['visit_date', 'check_in', 'check_out', 'created_at', 'updated_at']


class GuestCheckInSerializer(serializers.Serializer):
    """سيريلايزر تسجيل دخول الضيف"""
    
    host_member_id = serializers.IntegerField()
    guest_name = serializers.CharField(max_length=100)
    guest_phone = serializers.CharField(max_length=15)
    
    def validate_host_member_id(self, value):
        """التحقق من وجود العضو المضيف"""
        from apps.members.models import Member
        try:
            Member.objects.get(id=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("العضو المضيف غير موجود")
        return value
    
    def validate_guest_phone(self, value):
        """التحقق من صيغة الهاتف"""
        if not value or len(value) < 7:
            raise serializers.ValidationError("رقم الهاتف غير صحيح")
        return value


class GuestCheckOutSerializer(serializers.Serializer):
    """سيريلايزر تسجيل خروج الضيف"""
    
    visit_id = serializers.IntegerField()


class AttendanceStatisticsSerializer(serializers.Serializer):
    """سيريلايزر إحصائيات الحضور"""
    
    total_attendance = serializers.IntegerField()
    daily_attendance = serializers.ListField()
    hourly_distribution = serializers.ListField()
    by_sport = serializers.ListField()
    average_duration_minutes = serializers.FloatField(allow_null=True)


class AttendanceRateSerializer(serializers.Serializer):
    """سيريلايزر معدل الحضور"""
    
    total_attendance = serializers.IntegerField()
    days_period = serializers.IntegerField()
    attendance_rate_percentage = serializers.FloatField()
    average_per_week = serializers.FloatField()
