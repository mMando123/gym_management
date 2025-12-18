from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            'id',
            'member_id',
            'user',
            'gender',
            'date_of_birth',
            'national_id',
            'address',
        ]
