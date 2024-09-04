from django.shortcuts import render, redirect

def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("home")
    context = {}
    return render(request, "chat_app/chatPage.html", context)