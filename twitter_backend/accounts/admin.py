from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.UserProfile)
admin.site.register(models.Followers)
admin.site.register(models.Tweet)
admin.site.register(models.TweetComments)
admin.site.register(models.TweetRetweet)
admin.site.register(models.Bookmark)