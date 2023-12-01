from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tweet,UserProfile

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        # extra_kwargs = {'password': {'write_only': True}}

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        
class TweetSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user.profile', read_only=True)
    class Meta:
        model = Tweet
        fields = ['user','user_profile', 'content','media']
        extra_kwargs = {
            'media': {'required': False},
            'is_video': {'required': False},
        }
