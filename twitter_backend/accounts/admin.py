from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.UserProfile)
admin.site.register(models.Followers)
admin.site.register(models.Tweet)