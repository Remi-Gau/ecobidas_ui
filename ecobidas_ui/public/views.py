"""Public section, including homepage and signup."""

import json

from flask import Blueprint, abort, current_app, g, redirect, render_template, request, url_for
from flask_babel import _

from ecobidas_ui.settings import STATIC_FOLDER

blueprint = Blueprint(
    "public",
    __name__,
    static_folder="../static",
    template_folder="templates",
    url_prefix="/<lang_code>",
)


@blueprint.url_defaults
def add_language_code(endpoint, values):
    values.setdefault("lang_code", g.lang_code)


@blueprint.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop("lang_code")


@blueprint.before_request
def before_request():
    print(request.full_path)
    if g.lang_code not in current_app.config["LANGUAGES"]:
        adapter = current_app.url_map.bind("")
        try:
            endpoint, args = adapter.match("/en" + request.full_path.rstrip("/ ?"))
            return redirect(url_for(endpoint, **args), 301)
        except:  # noqa
            abort(404)

    dfl = request.url_rule.defaults
    if "lang_code" in dfl:
        if dfl["lang_code"] != request.full_path.split("/")[1]:
            abort(404)


@blueprint.route("/index", methods=["GET", "POST"])
def index():
    """Home page."""
    return render_template("public/index.html", message=_("testing"))


@blueprint.route("/faq/")
def faq():
    data = json.load(open(STATIC_FOLDER / "json" / "faq.json"))
    return render_template("public/faq.html", data=data)


@blueprint.route("/about/")
def about():
    """About page."""
    return render_template("public/about.html")
