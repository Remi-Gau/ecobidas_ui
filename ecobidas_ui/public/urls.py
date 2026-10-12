from django.urls import path

from ecobidas_ui.public import views

app_name = "public"

urlpatterns = [
    path("index", views.index, name="index"),
    path("faq/", views.faq, name="faq"),
    path("about/", views.about, name="about"),
]
