from django.urls import path
from .views import health, calculate, history

urlpatterns = [
    path('health/', health, name='Health'),
    path('calculate/', calculate, name='Calculate'),
    path('history/', history, name='History'),
]
