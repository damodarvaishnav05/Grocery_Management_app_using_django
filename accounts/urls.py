from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("google/login/", views.google_login_dispatch, name="google_login_dispatch"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("refer/", views.refer_and_earn_view, name="refer"),
]