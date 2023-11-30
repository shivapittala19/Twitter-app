from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.models import User

# App imports
# from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return render(request,'accounts/home.html',{})
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user:
            if user.is_active:
                login(request,user)
                return render(request,'accounts/home.html',{})
            else:   
                return HttpResponse("Account Not Active")
        else:
            return render(request, "accounts/login.html", {
                "error": "Invalid username or password"
            })
    else:
        return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return HttpResponse("Already logged")
    
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST.get('password')
    
        # create a user.
        try:
            user = User.objects.create(username = username, email=email, password = password)
            # user = authenticate(request, username=username, password=password)
            user.save()
        except IntegrityError:
            return render(request, "accounts/register.html", {
                "error": "Username already taken"
            })

        return render(request, "accounts/login.html",{"message":"Sucessfully registered"})
    else:
        return render(request, "accounts/register.html")
