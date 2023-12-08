from django.urls import path

# App imports
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path('logout',views.logout_view,name='logout'), 
    path('register/',views.register_view,name='register'),
    path('home/',views.HomePageView.as_view(),name='home'),
    path('profile/',views.ProfilePageView.as_view(),name='profile'),
    path('profile/<int:profile_id>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit-profile'),
    path('follow/<int:pk>/',views.FollowUser.as_view(),name="follow"),
    path('create-tweet/',views.CreateTweetView.as_view(),name="create-tweet"),
    path('increment-like/<uuid:tweet_uuid>/', views.IncrementLikeView.as_view(), name='increment_like'),
    path('add-comment/<uuid:tweet_uuid>/', views.AddCommentAPIView.as_view(), name='add-comment'),
    path('retweet/<uuid:tweet_uuid>/', views.RetweetAPIView.as_view(), name='retweet'),
    path('bookmark/<uuid:tweet_uuid>/', views.BookmarkAPIView.as_view(), name='bookmark-detail'),
    path('bookmark',views.BookmarkDetailView.as_view(),name='bookmark'),
    path('profile/api/delete-post/<uuid:tweet_uuid>/', views.DeletePostAPIView.as_view(), name='delete-post'),
    path('profile/api/get-tweet/<uuid:tweet_uuid>/', views.get_tweet, name='get-tweet'),
    path('update-tweet/<uuid:tweet_uuid>/',views.UpdateTweetView.as_view(),name='update-tweet'),
    path('home/single-tweet/<uuid:tweet_uuid>/', views.TweetDetailView.as_view(), name='single_tweet'),

]   
