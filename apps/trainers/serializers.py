from rest_framework import serializers
from .models import Trainer, TrainerAvailability


class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = [
            'id',
            'user',
            'trainer_id',
            'bio',
            'certifications',
            'years_of_experience',
            'rating',
            'is_active',
        ]


class TrainerAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerAvailability
        fields = [
            'id',
            'trainer',
            'day_of_week',
            'start_time',
            'end_time',
        ]
