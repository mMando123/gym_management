from rest_framework import serializers
from .models import Notification, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'title_template',
            'body_template', 'send_push', 'send_sms', 'send_email',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'template', 'template_name', 'title', 'body',
            'is_read', 'read_at', 'push_sent', 'sms_sent', 'email_sent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'read_at', 'push_sent', 'sms_sent', 'email_sent', 'created_at', 'updated_at']