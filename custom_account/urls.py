from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordChangeView

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from custom_account.views import login_user, logout_user, register_user

app_name = 'account'
urlpatterns = [
    path('login', login_user, name="login"),
    path('logout', logout_user, name="logout"),
    path('register', register_user, name="register"),

    # Password Reset URLs with Custom Templates
    path('password-reset/', CustomPasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_reset_complete.html'), name='password_change_done'),
]
