from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("user-dashboard/", views.user_dashboard_view, name="user_dashboard"),
    path("logout/", views.logout_view, name="logout"),
    # User management (admin only)
    path("manage-users/", views.manage_users_view, name="manage_users"),
    path("add-user/", views.add_user_view, name="add_user"),
    path("edit-user/<int:user_id>/", views.edit_user_view, name="edit_user"),
    path("delete-user/<int:user_id>/", views.delete_user_view, name="delete_user"),
    path("toggle-user/<int:user_id>/", views.toggle_user_status_view, name="toggle_user"),
]
