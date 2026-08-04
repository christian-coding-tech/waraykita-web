from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Count, Sum
from django.db import connection
from .models import Item, Profile


def get_user_profile(user):
    """Get or create the Profile for a given user."""
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


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
        "profile": get_user_profile(request.user),
        "total_users": total_users,
        "total_items": total_items,
        "activity_rate": activity_rate,
        "reports_count": inactive_items,
        "recent_users": recent_users,
    }
    return render(request, "users/admin_dashboard.html", context)


@login_required(login_url="login")
def reports_view(request):
    """Admin reports page — statistics and breakdowns."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("user_dashboard")

    # --- User statistics ---
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superuser_count = User.objects.filter(is_superuser=True).count()

    # --- Item statistics ---
    total_items = Item.objects.count()
    active_items = Item.objects.filter(is_active=True).count()
    inactive_items = Item.objects.filter(is_active=False).count()
    in_stock_items = Item.objects.filter(stock__gt=0).count()
    out_of_stock_items = Item.objects.filter(stock=0).count()

    # Total inventory value (sum of prices for active items)
    inventory_value = Item.objects.filter(is_active=True).aggregate(
        total=Sum("price")
    )["total"] or 0
    inventory_value = float(inventory_value)

    # --- Breakdowns ---
    # Items grouped by color
    color_breakdown = (
        Item.objects.values("color_variant")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Items grouped by stock status
    stock_breakdown = [
        {"label": "In Stock", "count": in_stock_items},
        {"label": "Out of Stock", "count": out_of_stock_items},
    ]

    # Users grouped by role
    role_breakdown = [
        {"label": "Superuser", "count": superuser_count},
        {"label": "Staff", "count": staff_users},
        {"label": "Regular", "count": max(total_users - staff_users, 0)},
    ]

    # Users grouped by status
    user_status_breakdown = [
        {"label": "Active", "count": active_users},
        {"label": "Inactive", "count": inactive_users},
    ]

    # --- Recent data ---
    recent_users = User.objects.all().order_by("-date_joined")[:5]
    recent_items = Item.objects.all().order_by("-created_at")[:8]

    # Top products by stock level
    top_products = Item.objects.all().order_by("-stock")[:5]

    context = {
        "user": request.user,
        "profile": get_user_profile(request.user),
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "staff_users": staff_users,
        "superuser_count": superuser_count,
        "total_items": total_items,
        "active_items": active_items,
        "inactive_items": inactive_items,
        "in_stock_items": in_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "inventory_value": inventory_value,
        "color_breakdown": color_breakdown,
        "stock_breakdown": stock_breakdown,
        "role_breakdown": role_breakdown,
        "user_status_breakdown": user_status_breakdown,
        "recent_users": recent_users,
        "recent_items": recent_items,
        "top_products": top_products,
    }
    return render(request, "users/reports.html", context)


@login_required(login_url="login")
def user_dashboard_view(request):
    """User dashboard for normal user accounts."""
    if request.user.is_superuser or request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":
        settings_action = request.POST.get("settings_action")

        if settings_action == "profile":
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            email = request.POST.get("email", "").strip()
            avatar = request.FILES.get("avatar")

            if email and email != request.user.email:
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.error(request, "Email is already in use by another account.")
                else:
                    request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()

            if avatar:
                profile = get_user_profile(request.user)
                if profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception:
                        pass
                profile.avatar = avatar
                profile.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("user_dashboard")

        elif settings_action == "password":
            current_password = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password changed successfully. Please log in again.")
                return redirect("login")

    profile = get_user_profile(request.user)
    return render(request, "users/user_dashboard.html", {"user": request.user, "profile": profile})


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
# Roles Management (Admin only)
# ============================================================

@user_passes_test(is_admin, login_url="login")
def manage_roles_view(request):
    """Manage user roles (Superuser / Staff / Regular)."""
    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")

        if action and user_id:
            target_user = get_object_or_404(User, id=user_id)
            username = target_user.username

            if action == "make_staff":
                # Prevent demoting/downgrading the currently logged-in superuser
                if target_user.id == request.user.id and request.user.is_superuser:
                    messages.error(request, "You cannot change your own role.")
                else:
                    target_user.is_staff = True
                    target_user.is_superuser = False
                    target_user.save()
                    messages.success(request, f"'{username}' is now a Staff member.")
            elif action == "make_superuser":
                if target_user.id == request.user.id and request.user.is_superuser:
                    messages.error(request, "You cannot change your own role.")
                else:
                    target_user.is_staff = True
                    target_user.is_superuser = True
                    target_user.save()
                    messages.success(request, f"'{username}' is now a Superuser.")
            elif action == "make_user":
                # Prevent downgrading the currently logged-in superuser
                if target_user.id == request.user.id and request.user.is_superuser:
                    messages.error(request, "You cannot change your own role.")
                else:
                    target_user.is_staff = False
                    target_user.is_superuser = False
                    target_user.save()
                    messages.success(request, f"'{username}' is now a Regular user.")

        return redirect("manage_roles")

    users = User.objects.all().order_by("-is_superuser", "-is_staff", "username")

    superuser_count = User.objects.filter(is_superuser=True).count()
    staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
    regular_count = User.objects.filter(is_staff=False, is_superuser=False).count()

    context = {
        "user": request.user,
        "profile": get_user_profile(request.user),
        "users": users,
        "superuser_count": superuser_count,
        "staff_count": staff_count,
        "regular_count": regular_count,
    }
    return render(request, "users/manage_roles.html", context)


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
# Database Management (Admin only)
# ============================================================

@user_passes_test(is_admin, login_url="login")
def database_view(request):
    """Display database tables, row counts, and database info."""
    tables_info = []
    total_records = 0
    db_name = ""
    db_engine = connection.vendor
    db_path = ""
    db_size = 0

    try:
        db_name = connection.settings_dict.get("NAME", "")
        tables = connection.introspection.table_names()

        with connection.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                    row_count = cursor.fetchone()[0]
                    total_records += row_count
                except Exception:
                    row_count = 0

                try:
                    columns = [c.name for c in connection.introspection.get_table_description(cursor, table)]
                except Exception:
                    columns = []

                tables_info.append({
                    "name": table,
                    "rows": row_count,
                    "columns": columns,
                })

        # Sort: app tables first, then django internal tables
        tables_info.sort(key=lambda t: t["name"])

        # SQLite file size
        if connection.vendor == "sqlite":
            import os
            db_file = str(db_name)
            if os.path.exists(db_file):
                db_path = os.path.abspath(db_file)
                db_size = os.path.getsize(db_file)
    except Exception:
        pass

    def format_size(num_bytes):
        for unit in ["B", "KB", "MB", "GB"]:
            if num_bytes < 1024 or unit == "GB":
                return f"{num_bytes:.2f} {unit}" if unit != "B" else f"{num_bytes} {unit}"
            num_bytes /= 1024

    context = {
        "user": request.user,
        "profile": get_user_profile(request.user),
        "tables_info": tables_info,
        "total_tables": len(tables_info),
        "total_records": total_records,
        "db_engine": db_engine,
        "db_name": db_name,
        "db_path": db_path,
        "db_size_display": format_size(db_size) if db_size else "—",
    }
    return render(request, "users/database.html", context)


# ============================================================
# Settings (Admin & User)
# ============================================================

@login_required(login_url="login")
def admin_settings_view(request):
    """Admin settings page — profile + password change."""
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("user_dashboard")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "profile":
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            email = request.POST.get("email", "").strip()
            avatar = request.FILES.get("avatar")

            if email and email != request.user.email:
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.error(request, "Email is already in use by another account.")
                else:
                    request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()

            # Handle avatar upload
            if avatar:
                profile = get_user_profile(request.user)
                if profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception:
                        pass
                profile.avatar = avatar
                profile.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("admin_settings")

        elif action == "password":
            current_password = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password changed successfully. Please log in again.")
                return redirect("login")

    profile = get_user_profile(request.user)
    return render(request, "users/admin_settings.html", {"user": request.user, "profile": profile})


@login_required(login_url="login")
def user_settings_view(request):
    """User settings page — profile + password change."""
    if request.user.is_superuser or request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "profile":
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            email = request.POST.get("email", "").strip()
            avatar = request.FILES.get("avatar")

            if email and email != request.user.email:
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.error(request, "Email is already in use by another account.")
                else:
                    request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()

            # Handle avatar upload
            if avatar:
                profile = get_user_profile(request.user)
                if profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception:
                        pass
                profile.avatar = avatar
                profile.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("user_settings")

        elif action == "password":
            current_password = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password changed successfully. Please log in again.")
                return redirect("login")

    profile = get_user_profile(request.user)
    return render(request, "users/user_settings.html", {"user": request.user, "profile": profile})


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
