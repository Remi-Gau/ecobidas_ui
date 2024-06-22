"""Public section, including homepage and signup."""

import json
from pathlib import Path

from flask import Blueprint, current_app, flash, g, render_template, send_from_directory
from flask_babel import _
from markdownify import markdownify as md

blueprint = Blueprint(
    "generate", __name__, url_prefix="/<lang_code>/generate", template_folder="templates"
)


def dummmy_data():
    with open(
        current_app.config["ROOT_DIR"]
        / ".."
        / "inputs"
        / "bids_template"
        / "task-auditoryLocalizer_bold.json"
    ) as f:
        data = json.load(f)
    return data


@blueprint.url_defaults
def add_language_code(endpoint, values):
    values.setdefault("lang_code", g.lang_code)


@blueprint.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop("lang_code")


@blueprint.route("/", methods=["GET", "POST"])
def generate():
    flash(
        _(
            """This page was generated using dummy data.
        In the final version the content of this page should adapt to the values you inputted in the checklist."""
        ),
        category="warning",
    )
    return render_template("generate/index.html", **dummmy_data())


@blueprint.route("/download", methods=["GET"])
def download():
    tmp = md(render_template("generate/report.html"), heading_style="ATX")
    with open(Path(current_app.config["UPLOAD_FOLDER"]) / "report.md", "w") as f:
        f.write(tmp)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], "report.md")
