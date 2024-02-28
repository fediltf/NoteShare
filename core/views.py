from django.shortcuts import render

def home(request):
    return render(request, "layouts-1.html")