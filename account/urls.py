from django.contrib import admin
from django.urls import path

from account.views import login_user, logout_user, register_user

app_name = 'account'
urlpatterns = [
    path('login', login_user, name="login"),
    path('logout', logout_user, name="logout"),
    path('register', register_user, name="register"),
]
