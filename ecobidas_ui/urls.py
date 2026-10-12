from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

from ecobidas_ui import views

urlpatterns = [
    path("", views.home, name="home"),
    path("export", views.export, name="export"),
]

urlpatterns += i18n_patterns(
    path("", include("ecobidas_ui.public.urls")),
    path("auth/", include("ecobidas_ui.auth.urls")),
    path("", include("ecobidas_ui.protocols.urls")),
    path("generate/", include("ecobidas_ui.generate.urls")),
)

handler404 = "ecobidas_ui.views.page_not_found"
handler500 = "ecobidas_ui.views.server_error"
