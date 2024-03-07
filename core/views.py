from django.shortcuts import render, redirect


def home(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    else:
        return render(request, "landing/layouts-1.html")