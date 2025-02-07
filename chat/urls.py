from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from chat.views import signup_view

urlpatterns = [
    path("", views.messages_page, name="home"),
    path("signup/", signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("messages/", views.messages_page, name="messages"),
]
