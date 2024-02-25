from django.urls import path, include  # include is imported here
from .views import index, home, search_view

urlpatterns = [  
    path('', index, name="index"),
    path('home/', home, name="home"),
    path('search/', search_view, name="search_view"),
]
