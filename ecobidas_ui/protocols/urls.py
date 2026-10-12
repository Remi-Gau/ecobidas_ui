from django.urls import path

from ecobidas_ui.protocols import views

app_name = "protocols"

urlpatterns = [
    path("protocol/<str:protocol_name>", views.protocol, name="protocol"),
    path("protocol/<str:protocol_name>/<str:activity_name>", views.activity, name="activity"),
]
