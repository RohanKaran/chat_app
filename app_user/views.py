from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.shortcuts import redirect, render
from .forms import UserRegistrationForm, LoginForm
from .models import User


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.filter(Q(email=username) | Q(phone=username)).first()
        if user:
            if user.is_active and user.check_password(password):
                login(request, user)
                return redirect("home")
            else:
                form.add_error("username", "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})
