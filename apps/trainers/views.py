from rest_framework import viewsets
from .models import Trainer, TrainerAvailability
from .serializers import TrainerSerializer, TrainerAvailabilitySerializer


class TrainerViewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.select_related('user').all()
    serializer_class = TrainerSerializer


class TrainerAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = TrainerAvailability.objects.select_related('trainer').all()
    serializer_class = TrainerAvailabilitySerializer
