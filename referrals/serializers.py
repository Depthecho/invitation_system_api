from rest_framework import serializers
from .models import User

class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite', 'date_joined']