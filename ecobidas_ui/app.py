import logging
import sys
from pathlib import Path

from flask import Flask, abort, g, render_template, request
from flask_babel import Babel

from ecobidas_ui import auth, db, generate, protocols, public
from ecobidas_ui._version import version
from ecobidas_ui.extensions import bootstrap, csrf_protect

# from ecobidas_ui.extensions import cache, debug_toolbar
from ecobidas_ui.initializers.assets import init_assets


def create_app(config_object="ecobidas_ui.settings"):

    # create and configure the app
    app = Flask(
        __name__, instance_relative_config=True, instance_path=Path(__file__).parent / "instance"
    )

    app.config.from_object(config_object)

    register_extensions(app)
    db.init_app(app)

    init_assets(app)
    register_blueprints(app)
    register_errorhandlers(app)
    configure_logger(app)

    @app.context_processor
    def inject_version():
        return dict(version=version)

    @app.route("/export")
    def export() -> str:
        abort(501)

    babel = Babel()

    def get_locale():
        if not g.get("lang_code", None):
            g.lang_code = request.accept_languages.best_match(app.config["LANGUAGES"])
        return g.lang_code

    babel.init_app(app, locale_selector=get_locale)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bootstrap.init_app(app)
    csrf_protect.init_app(app)
    # cache.init_app(app)
    # debug_toolbar.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(protocols.views.blueprint)
    app.register_blueprint(generate.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 405, 500, 501]:
        app.errorhandler(errcode)(render_error)
    return None


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
