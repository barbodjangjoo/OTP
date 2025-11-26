from rest_framework import serializers
from django.contrib.auth import get_user_model

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)

class UserSerializer(serializers.ModelSerializer):
    model = get_user_model()
    fields = '__all__'