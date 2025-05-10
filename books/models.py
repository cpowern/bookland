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
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user.username} → {self.book.title} : {self.stars}"
