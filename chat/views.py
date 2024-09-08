from django.shortcuts import render, redirect

def chatPage(request, id):
    if not request.user.is_authenticated:
        return redirect("home")
    context = {
        'user_id': id,  # Pass the user ID to the context
    }
    return render(request, "chat_app/chatPage.html", context)