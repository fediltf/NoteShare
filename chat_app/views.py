from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect('home')
    context = {}
    return render(request, "chat_app/chatPage.html", context)

# def chatPage(request, username=None, *args, **kwargs):
#     if not request.user.is_authenticated:
#         return redirect('home')
#
#     if username:
#         receiver = get_object_or_404(User, username=username)
#     else:
#         # Handle the case where no receiver is specified (optional)
#         return redirect('home')  # Or another fallback
#
#     context = {
#         'receiver': receiver
#     }
#     return render(request, "chat_app/chatPage.html", context)