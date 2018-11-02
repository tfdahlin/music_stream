from django.contrib import admin
from django.urls import path, include

from .views import (
    login,
    register,
)

app_name = 'user'

urlpatterns = [
    path(r'', login, name='login'),
    path(r'register', register, name='register'),
]