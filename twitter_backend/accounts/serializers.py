from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tweet,UserProfile, TweetComments

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        # extra_kwargs = {'password': {'write_only': True}}
        # validators = [
        # ]

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class TweetCommentsSerializer(serializers.ModelSerializer):
    class  Meta:
        model = TweetComments
        fields = '__all__'
        
        
class TweetSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user.profile', read_only=True)
    comments = TweetCommentsSerializer(many=True,read_only=True,source="comment")
    class Meta:
        model = Tweet
        fields = ['user','user_profile','uuid', 'content','media','updated_at','likes','comments']
        extra_kwargs = {
            'user_profile' : {'required':False},
            'media': {'required': False},
            'is_video': {'required': False},
            'updated_at ': {'required': False},
            'uuid ': {'required': False},
            'likes': {'required': False},
            'comments':{'requied':False}
        }

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['coverImage', 'profileImage', 'bio', 'display_name', 'website','updated_at']
        
    def update(self, instance, validated_data):
        instance.coverImage = validated_data.get('coverImage', instance.coverImage)
        instance.profileImage = validated_data.get('profileImage', instance.profileImage)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.website = validated_data.get('website', instance.website)
        instance.is_verified = validated_data.get('is_verified', instance.is_verified)
        instance.updated_at = validated_data.get('is_verified', instance.updated_at)
        instance.save()
        return instance
    
class TweetSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['content', 'media']
        extra_kwargs = {
            'media': {'required': False},
        }
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetComments
        fields = ['comment_content', 'media']
    
    def validate(self, data):
        comment_content = data.get('comment_content')
        media = data.get('media')
        if not comment_content and not media:
            raise serializers.ValidationError("Either 'comment_content' or 'media' is required.")

        return data
