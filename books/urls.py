from django.urls import path
from .views import recommendations_view
from .views import profile_view

urlpatterns = [
    path('recommendations/', recommendations_view, name='recommendations'),
    path("profile/", profile_view, name="profile"),
]
