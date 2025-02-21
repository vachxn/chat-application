from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chat.views import signup_view, login_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("chat.urls")),  # Include all chat app URLs
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
