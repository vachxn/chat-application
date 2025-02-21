from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.messages_page, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("messages/", views.messages_page, name="messages"),
    path("chat/<int:user_id>/", views.chat, name="chat"),
    path("chat/", views.chat, name="chat_default"),
    path("send_message/", views.send_message, name="send_message"),
]
