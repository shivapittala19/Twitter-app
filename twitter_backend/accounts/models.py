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
    def create_follow(sender,instance,created,**kwargs):
        if created:
            user = Followers(user=instance)
            user.save()
    models.signals.post_save.connect(create_follow,sender=User)


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, max_length=40, unique=True, editable=False)
    content = models.TextField(max_length=240, blank=False, null=False)
    media = models.FileField(upload_to='tweet-media', blank=True, null=True)
    likes = models.ManyToManyField(to=User, blank=True, related_name='tweet_likes')
    is_video = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=True)

class TweetComments(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(to=Tweet, on_delete=models.CASCADE,related_name='comment')
    comment_content = models.TextField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    media = models.ImageField(upload_to='comment-media', blank=True, null=True)
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')


class TweetRetweet(models.Model):
    user =  models.ForeignKey(to=User, on_delete=models.CASCADE)
    retweet = models.ForeignKey(Tweet,on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
