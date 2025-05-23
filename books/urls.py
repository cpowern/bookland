from django.urls import path
from .views import recommendations_view
from .views import profile_view
from .views import rate_book_view
from .views import home_view
from .views import main_view, search_books_view

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("rate/<str:isbn>/", rate_book_view, name="rate_book"),
    path("", home_view, name="home"),
    path('main/', main_view, name='main'),   # Nach Login
    path('recommendations/', recommendations_view, name='recommendations'),
    path("search-books/", search_books_view, name="search_books"),
]
