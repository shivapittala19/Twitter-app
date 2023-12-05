# from django import forms 
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User


# class LoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)   

# class SignUpForm(UserCreationForm):
    
#     email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1']
from django import forms
from .models import UserProfile, Tweet

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'display_name', 'profileImage']

