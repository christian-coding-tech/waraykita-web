from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages


def is_admin(user):
    """Check if the user is an admin (staff or superuser)."""
    return user.is_authenticated and (user.is_superuser or user.is_staff)

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


# ============================================================
# User Management (Admin only)
# ============================================================

@user_passes_test(is_admin, login_url="login")
def manage_users_view(request):
    """List all users for admin management."""
    users = User.objects.all().order_by("-date_joined")
    return render(request, "users/manage_users.html", {"users": users})


@user_passes_test(is_admin, login_url="login")
def add_user_view(request):
    """Add a new user from the admin panel."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        is_staff = request.POST.get("is_staff") == "on"

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("manage_users")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("manage_users")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
        )
        messages.success(request, f"User '{username}' created successfully.")
        return redirect("manage_users")

    return redirect("manage_users")


@user_passes_test(is_admin, login_url="login")
def edit_user_view(request, user_id):
    """Edit an existing user."""
    target_user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        is_staff = request.POST.get("is_staff") == "on"
        is_active = request.POST.get("is_active") == "on"
        new_password = request.POST.get("password", "").strip()

        if email:
            target_user.email = email

        # Prevent a superuser from removing their own staff/superuser status
        if target_user.id == request.user.id and request.user.is_superuser:
            target_user.is_staff = True
            target_user.is_superuser = True
        else:
            target_user.is_staff = is_staff

        target_user.is_active = is_active

        if new_password:
            target_user.set_password(new_password)

        target_user.save()
        messages.success(request, f"User '{target_user.username}' updated successfully.")
        return redirect("manage_users")

    return render(request, "users/edit_user.html", {"target_user": target_user})


@user_passes_test(is_admin, login_url="login")
def delete_user_view(request, user_id):
    """Delete a user."""
    target_user = get_object_or_404(User, id=user_id)

    # Prevent admins from deleting themselves
    if target_user.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect("manage_users")

    username = target_user.username
    target_user.delete()
    messages.success(request, f"User '{username}' deleted successfully.")
    return redirect("manage_users")


@user_passes_test(is_admin, login_url="login")
def toggle_user_status_view(request, user_id):
    """Toggle a user's active/inactive status."""
    target_user = get_object_or_404(User, id=user_id)

    if target_user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("manage_users")

    target_user.is_active = not target_user.is_active
    target_user.save()

    status = "activated" if target_user.is_active else "deactivated"
    messages.success(request, f"User '{target_user.username}' {status} successfully.")
    return redirect("manage_users")