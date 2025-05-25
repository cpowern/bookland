from django.urls import path
from .views import (
    recommendations_view, profile_view, rate_book_view,
    home_view, main_view, search_books_view,
    add_book_view, edit_book_view, delete_book_view  # 👈 hinzufügen
)

urlpatterns = [
    path("", home_view, name="home"),
    path("main/", main_view, name="main"),
    path("profile/", profile_view, name="profile"),
    path("recommendations/", recommendations_view, name="recommendations"),
    path("rate/<str:isbn>/", rate_book_view, name="rate_book"),
    path("search-books/", search_books_view, name="search_books"),

    # ✨ CRUD für Bücher:
    path("book/add/", add_book_view, name="add_book"),
    path("book/<str:isbn>/edit/", edit_book_view, name="edit_book"),
    path("book/<str:isbn>/delete/", delete_book_view, name="delete_book"),
]
