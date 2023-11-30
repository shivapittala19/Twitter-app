from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    coverImage = models.ImageField(null=True, blank=True)
    profileImage = models.ImageField(null=True,blank=True)
    bio = models.TextField(max_length=160, blank=True, null=True)
    display_name = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"username": self.user.username})
    
    def create_profile(sender,instance,created,**kwargs):
        if created:
            user = UserProfile(user=instance)
            user.save()
    models.signals.post_save.connect(create_profile,sender=User)

class Followers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(to=User, related_name="following", blank=True)
    followers = models.ManyToManyField(to=User, related_name="followed_user", blank=True)


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, max_length=40, unique=True, editable=False)
    content = models.TextField(max_length=240, blank=False, null=False)
    media = models.FileField(upload_to='tweet-media', blank=True, null=True)
    likes = models.ManyToManyField(to=User, blank=True, related_name='tweet_likes')
    is_video = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=True)
    
# class TweetComments(models.Model):
#     # fields
#     # user, tweet, comment, date, media, likes(User)
#     pass
    
# class TweetLike(models.Model):
#     # fields
#     # user, tweet, created_at
#     pass

# class TweetRetweet(models.Model):
#     # fields
#     # user, tweet, created_at
#     pass

# class Media(models.Model):
#     # fields
#     # user, image/video, type, description, url, created_at
#     pass

