from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("user-dashboard/", views.user_dashboard_view, name="user_dashboard"),
    path("reports/", views.reports_view, name="reports"),
    path("logout/", views.logout_view, name="logout"),
    # User management (admin only)
    path("manage-users/", views.manage_users_view, name="manage_users"),
    path("add-user/", views.add_user_view, name="add_user"),
    path("edit-user/<int:user_id>/", views.edit_user_view, name="edit_user"),
    path("delete-user/<int:user_id>/", views.delete_user_view, name="delete_user"),
path("toggle-user/<int:user_id>/", views.toggle_user_status_view, name="toggle_user"),
    path("manage-roles/", views.manage_roles_view, name="manage_roles"),
    path("database/", views.database_view, name="database"),
    # Item / Product management (admin only)
    path("manage-items/", views.manage_items_view, name="manage_items"),
    path("add-item/", views.add_item_view, name="add_item"),
    path("toggle-item/<int:item_id>/", views.toggle_item_status_view, name="toggle_item"),
    path("delete-item/<int:item_id>/", views.delete_item_view, name="delete_item"),
    # Settings (Admin & User)
    path("admin-settings/", views.admin_settings_view, name="admin_settings"),
    path("user-settings/", views.user_settings_view, name="user_settings"),
    # Public product API (for real-time updates)
    path("api/active-items/", views.api_active_items_view, name="api_active_items"),
]
