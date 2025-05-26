from django.contrib import admin
from .models import UserProfile
from .models import Book, Rating

admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(Rating)
