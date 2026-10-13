from django.contrib.auth import views as auth_views
from django.urls import path

from ecobidas_ui.auth import views

app_name = "auth"

urlpatterns = [
    path("login", views.login_page, name="login"),
    path("orcid", views.orcid_login, name="orcid"),
    # logging out must be done with a POST request
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
]
