from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')), 
    path('users/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
