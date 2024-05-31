"""Public section, including homepage and signup."""

import json

from flask import Blueprint, render_template

from ecobidas_ui.settings import STATIC_FOLDER

blueprint = Blueprint("public", __name__, static_folder="../static", template_folder="templates")


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    return render_template("public/index.html")


@blueprint.route("/faq/")
def faq():
    data = json.load(open(STATIC_FOLDER / "json" / "faq.json"))
    return render_template("public/faq.html", data=data)


@blueprint.route("/about/")
def about():
    """About page."""
    return render_template("public/about.html")
