from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView

from config.views import HealthChecker
from user.interface import urls as user_urls

urlpatterns = [
    re_path(r"^$", view=HealthChecker.as_view(), name="HealthChecker"),
    re_path(r"^", include(user_urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]
