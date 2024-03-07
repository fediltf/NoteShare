from django.shortcuts import render

def home(request):
    return render(request, "landing/layouts-1.html")