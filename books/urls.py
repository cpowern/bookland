from django.urls import path
from .views import recommendations_view
from .views import profile_view
from .views import rate_book_view
from .views import main_view
from .views import main_view, search_books_view

urlpatterns = [
    path('recommendations/', recommendations_view, name='recommendations'),
    path("profile/", profile_view, name="profile"),
    path("rate/<str:isbn>/", rate_book_view, name="rate_book"),
    path("", main_view, name="main"),
    path("search-books/", search_books_view, name="search_books"),
]
