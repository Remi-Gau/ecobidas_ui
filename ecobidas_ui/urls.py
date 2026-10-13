from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from ecobidas_ui import views
from ecobidas_ui.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("export", views.export, name="export"),
    # not translated: this exact URL must be registered on ORCID
    path("auth/orcid/callback", auth_views.orcid_callback, name="orcid_callback"),
    # the admin site has no passwords either: log in with ORCID
    path("admin/login/", auth_views.admin_login, name="admin_login"),
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("", include("ecobidas_ui.public.urls")),
    path("auth/", include("ecobidas_ui.auth.urls")),
    path("", include("ecobidas_ui.protocols.urls")),
    path("generate/", include("ecobidas_ui.generate.urls")),
)

handler404 = "ecobidas_ui.views.page_not_found"
handler500 = "ecobidas_ui.views.server_error"
