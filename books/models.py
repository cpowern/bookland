from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kaggle_user_id = models.IntegerField()

    def __str__(self):
        return self.user.username
