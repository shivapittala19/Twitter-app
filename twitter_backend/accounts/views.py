from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect,JsonResponse

# rest framework
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated     

# App imports
from  . import serializers
from .models import Tweet, UserProfile, TweetRetweet, Bookmark

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
        queryset = Tweet.objects.exclude(user=request.user).order_by('-updated_at')
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
    authentication_classes = [SessionAuthentication]
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
                'posts': queryset,
                'following':request.user.followers.following.all(),
                'followers':request.user.followers.followers.all(),
            }
        )

class EditProfileView(APIView):
    authentication_classes = [SessionAuthentication]
    def post(self, request, format = None):
        user_profile = request.user.profile  
        serializer = serializers.UserProfileSerializer(user_profile, data=request.data )
        if serializer.is_valid():
            serializer.save()
        return HttpResponseRedirect(reverse('accounts:profile'))

class CreateTweetView(APIView):
    authentication_classes = [SessionAuthentication]
    def post(self, request, *args, **kwargs):
        serializer = serializers.TweetSaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
        return HttpResponseRedirect(reverse('accounts:profile')) 


class IncrementLikeView(APIView):
    authentication_classes = [SessionAuthentication]
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
    authentication_classes = [SessionAuthentication]
    def get(self, request, profile_id):
        user_profile = UserProfile.objects.get(id=profile_id)    
        queryset = Tweet.objects.filter(user = user_profile.user).order_by('-updated_at')
        serializer = serializers.TweetSerializer(queryset, many=True)
        user_serializer = serializers.UserProfileSerializer(user_profile)
        
        current_user = UserProfile.objects.get(user = request.user)
        curent_user_serializer = serializers.UserProfileSerializer(current_user)
        
        profile_user_follow = request.user.followers
        current_user_follow = user_profile.user.followers

        is_following = user_profile.user in  request.user.followers.following.all()
    
        return render(
            request,
            'accounts/others-profile.html',
            {   
                'posts' : queryset,
                'following':current_user_follow.following.all(),
                'followers':current_user_follow.followers.all(),
                'is_following':is_following,
                'profile_id':profile_id,
                'logged_user' : curent_user_serializer.data ,
                'specific' : user_serializer.data,
                'tweets': serializer.data,
            }
        )

class FollowUser(APIView):
    authentication_classes = [SessionAuthentication]
    
    def post(self, request,pk):
        user_to_toggle = User.objects.get(id=pk)
        current_user = request.user
        current_user_profile = request.user.followers
        user_to_toggle_profile = user_to_toggle.followers
        
        is_following = current_user_profile.following.filter(username = user_to_toggle.username).exists()

        if is_following:
            current_user_profile.following.remove(user_to_toggle)
            user_to_toggle_profile.followers.remove(current_user)
            
        else:
            current_user_profile.following.add(user_to_toggle)
            user_to_toggle_profile.followers.add(current_user)

        return JsonResponse(
            {
                'is_following': not is_following,
                'following':user_to_toggle_profile.following.count(),
                'followers':user_to_toggle_profile.followers.count(),
            })

class AddCommentAPIView(APIView):
    def post(self, request, tweet_uuid, *args, **kwargs):
        tweet = get_object_or_404(Tweet, uuid=tweet_uuid)
        serializer = serializers.CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, tweet=tweet)
        return HttpResponseRedirect(reverse('accounts:home'))

class RetweetAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.RetweetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tweet_uuid = serializer.validated_data['tweet_uuid']

        tweet = get_object_or_404(Tweet, uuid=tweet_uuid)

        if TweetRetweet.objects.filter(user=request.user, retweet=tweet).exists():
            TweetRetweet.objects.filter(user=request.user, retweet=tweet).delete()
            retweet_status = False
        else:
            TweetRetweet.objects.create(user=request.user, retweet=tweet)
            retweet_status = True
        return Response(
            {
                'retweet_status': retweet_status,
            }, status=status.HTTP_200_OK)


class BookmarkAPIView(APIView):
    def post(self, request,tweet_uuid, *args, **kwargs):
        user = request.user  
        tweet = get_object_or_404(Tweet, uuid=tweet_uuid)
        
        if Bookmark.objects.filter(user=user, tweet=tweet).exists():
            existing_bookmark = Bookmark.objects.get(user=user, tweet=tweet)
            existing_bookmark.delete()
            return JsonResponse({'success': False, 'message': 'Bookmark deleted'})

        # Create the bookmark
        bookmark = Bookmark(user=user, tweet=tweet)
        bookmark.save()

        return JsonResponse({'success': True})

class BookmarkDetailView(APIView):
    def get(self, request):
        queryset = Tweet.objects.filter(bookmark__user=request.user)
        serializer = serializers.TweetSerializer(queryset, many=True)
        return render(
            request, 
            'accounts/bookmark.html',
            { 
                'tweets': serializer.data,
            }
        )
   
class DeletePostAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, tweet_uuid):
        tweet = get_object_or_404(Tweet, uuid = tweet_uuid)
        self.check_object_permissions(request, tweet)
        tweet.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
    
def get_tweet(request, tweet_uuid):
    tweet = get_object_or_404(Tweet, uuid=tweet_uuid)
    # You can customize the data you want to include in the response
    data = {
        'success': True,
        'tweet': {
            'id': tweet.id,
            'content': tweet.content,
            'media': tweet.media.url if tweet.media else None,
            # Add other fields as needed
        }
    }
    return JsonResponse(data)

class UpdateTweetView(APIView):
    def post(self, request, tweet_uuid, *args, **kwargs):
        tweet = get_object_or_404(Tweet, uuid=tweet_uuid)
        content = request.POST.get('content', tweet.content)
        media = request.FILES.get('media', tweet.media)

        # Update the tweet object with the new values
        tweet.content = content
        tweet.media = media
        tweet.save()

        # Return the updated tweet data in the response
        data = {
            'success': True,
            'tweet': {
                'id': tweet.id,
                'content': tweet.content,
                'media': tweet.media.url if tweet.media else None,
            }
        }
        return HttpResponseRedirect(reverse('accounts:profile'))