from rest_framework import viewsets
from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('user').all()
    serializer_class = MemberSerializer
