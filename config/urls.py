
<<<<<<< HEAD
from django.urls import include, path, re_path
from config.views import HealthChecker
from user.interface import urls as user_urls
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    re_path(r"^$", view=HealthChecker.as_view(), name="HealthChecker"),
    re_path(r"^", include(user_urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema")
=======
from django.urls import path, re_path
from config.views import HealthChecker

urlpatterns = [
    re_path(r"^$", view=HealthChecker.as_view(), name="HealthChecker"),
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448
]

