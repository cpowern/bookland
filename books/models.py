from django.contrib.auth.models import User
from django.db import models

class Book(models.Model):
    isbn = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=20, default='dummy')
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3)

    class Meta:
        unique_together = ('user', 'isbn')  # ein Rating pro User+ISBN

    def __str__(self):
        return f"{self.user.username} → {self.isbn}: {self.score}"
from django.contrib.auth.models import User
from django.db import models

class Book(models.Model):
    isbn = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=20, default='dummy')
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3)

    class Meta:
        unique_together = ('user', 'isbn')  # ein Rating pro User+ISBN

    def __str__(self):
        return f"{self.user.username} → {self.isbn}: {self.score}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kaggle_user_id = models.IntegerField()

    def __str__(self):
        return self.user.username
