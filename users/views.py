from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Item


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
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Basic validation
        if not first_name or not last_name or not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("login")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("login")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("login")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("login")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("login")

        # Create a normal user (not staff, not superuser)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
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

    # Real statistics from the database
    total_users = User.objects.count()
    total_items = Item.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    active_items = Item.objects.filter(is_active=True).count()

    # Activity rate = percentage of active users
    activity_rate = round((active_users / total_users * 100), 1) if total_users > 0 else 0

    # "Reports" placeholder — count of inactive items as a proxy metric
    inactive_items = Item.objects.filter(is_active=False).count()

    # Recent users (latest 5)
    recent_users = User.objects.all().order_by("-date_joined")[:5]

    context = {
        "user": request.user,
        "total_users": total_users,
        "total_items": total_items,
        "activity_rate": activity_rate,
        "reports_count": inactive_items,
        "recent_users": recent_users,
    }
    return render(request, "users/admin_dashboard.html", context)


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


# ============================================================
# Item / Product Management (Admin only)
# ============================================================

@user_passes_test(is_admin, login_url="login")
def manage_items_view(request):
    """List all items/products for admin management."""
    items = Item.objects.all().order_by("-created_at")
    return render(request, "users/manage_items.html", {"items": items})


@user_passes_test(is_admin, login_url="login")
def add_item_view(request):
    """Add a new product from the admin panel."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        price = request.POST.get("price", "0").strip()
        description = request.POST.get("description", "").strip()
        details = request.POST.get("details", "").strip()
        stock = request.POST.get("stock", "0").strip()
        color_variant = request.POST.get("color_variant", "").strip()
        is_active = request.POST.get("is_active") == "on"
        image = request.FILES.get("image")

        if not title:
            messages.error(request, "Product title is required.")
            return redirect("manage_items")

        try:
            price_val = float(price) if price else 0.00
            stock_val = int(stock) if stock else 0
        except ValueError:
            messages.error(request, "Invalid price or stock value.")
            return redirect("manage_items")

        item = Item.objects.create(
            title=title,
            price=price_val,
            description=description,
            details=details,
            stock=stock_val,
            color_variant=color_variant,
            is_active=is_active,
        )
        if image:
            item.image = image
            item.save()

        messages.success(request, f"Product '{title}' created successfully.")
        return redirect("manage_items")

    return redirect("manage_items")


@user_passes_test(is_admin, login_url="login")
def toggle_item_status_view(request, item_id):
    """Toggle a product's active/inactive status."""
    item = get_object_or_404(Item, id=item_id)
    item.is_active = not item.is_active
    item.save()

    status = "activated" if item.is_active else "deactivated"
    messages.success(request, f"Product '{item.title}' {status} successfully.")
    return redirect("manage_items")


@user_passes_test(is_admin, login_url="login")
def delete_item_view(request, item_id):
    """Delete a product."""
    item = get_object_or_404(Item, id=item_id)
    title = item.title
    # Remove image file from disk if present
    if item.image:
        try:
            item.image.delete(save=False)
        except Exception:
            pass
    item.delete()
    messages.success(request, f"Product '{title}' deleted successfully.")
    return redirect("manage_items")


# ============================================================
# Public Product API (for real-time updates on user dashboard)
# ============================================================

@require_GET
def api_active_items_view(request):
    """Return active products as JSON for the user dashboard polling."""
    items = Item.objects.filter(is_active=True).order_by("-created_at")
    data = []
    for it in items:
        data.append({
            "id": it.id,
            "title": it.title,
            "price": str(it.price),
            "description": it.description,
            "details": it.details,
            "stock": it.stock,
            "color_variant": it.color_variant,
            "image": request.build_absolute_uri(it.image.url) if it.image else None,
            "created_at": it.created_at.isoformat(),
        })
    return JsonResponse({"items": data})
