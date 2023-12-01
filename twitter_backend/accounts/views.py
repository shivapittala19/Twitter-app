from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import reverse
from django.http import HttpResponseRedirect

# rest framework
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

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
                return Response({"message": "Successfully logged in"}, template_name='accounts/home.html')
            else:
                return Response({"error": "Invalid credentials"}, template_name='accounts/login.html')

    return Response({"serializer": serializers.LoginSerializer()}, template_name='accounts/login.html')

class HomePageView(APIView):
    
    def get(self, request, format=None):
        queryset = Tweet.objects.all()
        serializer = serializers.TweetSerializer(queryset, many=True)
        return render(
            request, 
            'accounts/home.html',
            {
                'tweets': serializer.data,
            }
        )