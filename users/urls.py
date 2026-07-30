from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("user-dashboard/", views.user_dashboard_view, name="user_dashboard"),
    path("logout/", views.logout_view, name="logout"),
]
