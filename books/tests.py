from django.test import TestCase
from django.contrib.auth.models import User
from .models import Book, Rating

class BookTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.book = Book.objects.create(isbn="123", title="Testbuch", author="Autor")

    def test_user_can_rate_book(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.post(f"/rate/{self.book.isbn}/", {"score": 4})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rating.objects.count(), 1)


    def test_main_page_loads(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get("/main/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bücher durchsuchen")


    def test_recommendations_requires_login(self):
        response = self.client.get("/recommendations/")
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/accounts/login/", response.url)
    