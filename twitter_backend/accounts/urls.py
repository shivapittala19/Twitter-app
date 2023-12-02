from django.urls import path

# App imports
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path('register/',views.register_view,name='register'),
    path('home/',views.HomePageView.as_view(),name='home'),
    path('profile/',views.ProfilePageView.as_view(),name='profile'),
]
