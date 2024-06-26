from flask_assets import Bundle, Environment

from ecobidas_ui import settings

# consolidated css bundle
css_bundle = Bundle("css/main.css")


def init_assets(app):
    app.config["ASSETS_DEBUG"] = settings.DEBUG
    webassets = Environment(app)
    webassets.register("css", css_bundle)
