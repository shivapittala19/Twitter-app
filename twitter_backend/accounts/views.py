from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect,JsonResponse

# rest framework
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
# App imports
from  . import serializers, models
from .models import Tweet, UserProfile, Followers

@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:home'))

    if request.method == 'POST':
        serializer = serializers.RegistrationSerializer(data=request.data)  
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            email = serializer.validated_data['email']
 
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            return Response({"message": "Successfully registered"},template_name='accounts/login.html')
        else:
            return Response({"error": "username is already taken"}, template_name='accounts/register.html')
            
    return Response({"serializer": serializers.RegistrationSerializer()}, template_name='accounts/register.html')


@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])    
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:home'))

    if request.method == 'POST':
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('accounts:home'))
            else:
                return Response({"error": "Invalid credentials"}, template_name='accounts/login.html')

    return Response({"serializer": serializers.LoginSerializer()}, template_name='accounts/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))

class HomePageView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request, format=None):
        if request.user.is_anonymous:
            return HttpResponseRedirect(reverse('accounts:login')) 
        queryset = Tweet.objects.all().order_by('-updated_at')
        serializer = serializers.TweetSerializer(queryset, many=True)
        current_user = UserProfile.objects.get(user = request.user)
        user_serializer = serializers.UserProfileSerializer(current_user)
        return render(
            request, 
            'accounts/home.html',
            { 
                'logged_user' : user_serializer.data,
                'tweets': serializer.data,
            }
        )

class ProfilePageView(APIView):
    def get(self,request,format = None):
        queryset = Tweet.objects.filter(user = request.user).order_by('-updated_at')
        serializer = serializers.TweetSerializer(queryset, many=True)
        current_user = UserProfile.objects.get(user = request.user)
        user_serializer = serializers.UserProfileSerializer(current_user)
        return render(
            request, 
            'accounts/profile.html',
            {   'logged_user' : user_serializer.data,
                'tweets': serializer.data,
            }
        )

class EditProfileView(APIView):
    def post(self, request, format = None):
        user_profile = request.user.profile  
        serializer = serializers.UserProfileSerializer(user_profile, data=request.data )
        if serializer.is_valid():
            serializer.save()
        return HttpResponseRedirect(reverse('accounts:profile'))

class CreateTweetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.TweetSaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
        return HttpResponseRedirect(reverse('accounts:profile')) 


from django.shortcuts import get_object_or_404
class IncrementLikeView(APIView):
    def post(self, request, tweet_uuid, *args, **kwargs):
        tweet = get_object_or_404(Tweet, uuid=tweet_uuid)
        if request.user not in tweet.likes.all():
            tweet.likes.add(request.user)
        else:
            tweet.likes.remove(request.user)
        likes_count = tweet.likes.count()
        return JsonResponse({'likes_count': likes_count})


class ProfileDetailView(APIView):
    template_name = 'accounts/profile.html'

    def get(self, request, profile_id):
        user_profile = UserProfile.objects.get(id=profile_id)    
        queryset = Tweet.objects.filter(user = user_profile.user).order_by('-updated_at')
        serializer = serializers.TweetSerializer(queryset, many=True)
        user_serializer = serializers.UserProfileSerializer(user_profile)
        
        current_user = UserProfile.objects.get(user = request.user)
        curent_user_serializer = serializers.UserProfileSerializer(current_user)
        
        profile_user_follow = Followers.objects.get(user = request.user )
        current_user_follow = Followers.objects.get(user = user_profile.user)
        if request.user in current_user_follow.following.all():
            is_followed = False
        else:
            is_followed = True
        return render(
            request, 
            'accounts/others-profile.html',
            {   
                'is_followed':is_followed,
                'profile_id':profile_id,
                'logged_user' : curent_user_serializer.data ,
                'specific' : user_serializer.data,
                'tweets': serializer.data,
            }
        )

class FollowUser(APIView):
    def post(self, request,pk):
        current_user = request.user
        profile_user = UserProfile.objects.get(id=pk).user
        
        profile_user_follow = Followers.objects.get(user = current_user )
        current_user_follow = Followers.objects.get(user = profile_user)
        is_followed = False
        if profile_user not in current_user_follow.following.all():
            current_user_follow.following.add(profile_user)
            profile_user_follow.followers.add(current_user)
            is_followed = True
        else:
            current_user_follow.following.remove(profile_user)
            profile_user_follow.followers.remove(current_user)
            is_followed = False

        return JsonResponse(
            {
                'following':current_user_follow.following.count(),
                'followers':current_user_follow.followers.count(),
                'is_followed': is_followed
            }
        )



class AddCommentAPIView(APIView):
    def post(self, request ,*args, **kwargs):
        tweet_uuid = request.data['tweet_uuid']
        tweet = get_object_or_404(Tweet, uuid=tweet_uuid)
        serializer = serializers.CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, tweet=tweet)
            # return Response({'success': True}, status=status.HTTP_201_CREATED)
            return JsonResponse({'success': True})
        else:
            # return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse({'success': False})