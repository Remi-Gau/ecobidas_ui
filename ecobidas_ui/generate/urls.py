from django.urls import path

from ecobidas_ui.generate import views

app_name = "generate"

urlpatterns = [
    path("", views.generate, name="generate"),
    path("download", views.download, name="download"),
]
