from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user type when already logged in
        if request.user.is_superuser or request.user.is_staff:
            return redirect("admin_dashboard")
        return redirect("user_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user type after successful login
            if user.is_superuser or user.is_staff:
                return redirect("admin_dashboard")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "users/login.html")


def register_view(request):
    """Register a new account. Registered accounts are always normal users."""
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect("admin_dashboard")
        return redirect("user_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Basic validation
        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("login")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("login")

        # Create a normal user (not staff, not superuser)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        messages.success(
            request,
            "Account created successfully! You can now log in.",
        )
        return redirect("login")

    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def admin_dashboard_view(request):
    """Admin dashboard for superuser/staff accounts."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("user_dashboard")

    return render(request, "users/admin_dashboard.html", {"user": request.user})


@login_required(login_url="login")
def user_dashboard_view(request):
    """User dashboard for normal user accounts."""
    if request.user.is_superuser or request.user.is_staff:
        return redirect("admin_dashboard")

    return render(request, "users/user_dashboard.html", {"user": request.user})
