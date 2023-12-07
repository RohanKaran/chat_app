from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def chat_view(request):
    return render(request, "chat.html")
