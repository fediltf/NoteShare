from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView, \
    PasswordChangeDoneView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.urls import reverse_lazy

from dashboard.models import School, Topic, Student
from .forms import SignUpForm, CustomPasswordResetForm, CustomSetPasswordForm


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'You have been successfully logged in as {username} ..')
            return redirect('dashboard:index')
        else:
            messages.success(request, 'Error! Try Again..')
            return redirect('account:login')
    else:
        return render(request, 'registration/auth-login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out..')
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('account:complete-profile')
        else:
            messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
            return redirect('register')
    else:
        return render(request, 'registration/auth-register.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    form_class = CustomSetPasswordForm


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_change_done')
    form_class = CustomSetPasswordForm


@login_required
def complete_profile(request):
    schools = School.objects.all().order_by('name')
    topics = Topic.objects.all().order_by('name')
    context = {'schools': schools, 'topics': topics}
    if request.method == 'POST':
        selected_school_id = request.POST.get('uni')
        selected_interests = request.POST.getlist('interests')
        student= Student.objects.get(user=request.user)
        student.school_id = selected_school_id
        student.interests.clear()
        for interest_id in selected_interests:
            student.interests.add(interest_id)
        student.save()
        return redirect('dashboard:index')
    return render(request, 'registration/complete_profile.html', context)
