from django.urls import path

from ecobidas_ui.auth import views

app_name = "auth"

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
]
