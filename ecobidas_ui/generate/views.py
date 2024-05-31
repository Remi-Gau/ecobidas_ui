"""Public section, including homepage and signup."""

import json
from pathlib import Path

from flask import Blueprint, current_app, render_template, send_from_directory
from markdownify import markdownify as md

from ecobidas_ui.protocols.utils import local_cobidas_schema

blueprint = Blueprint("generate", __name__, url_prefix="/generate")


def dummmy_data():
    with open(
        current_app.config["ROOT_DIR"] / ".." / "inputs" / "bids_template" / "task-auditoryLocalizer_bold.json"
    ) as f:
        data = json.load(f)
    return data


@blueprint.route("/", methods=["GET", "POST"])
def generate():
    return render_template("generate/index.html", **dummmy_data())


@blueprint.route("/download", methods=["GET"])
def download():
    tmp = md(render_template("generate/report.html"), heading_style="ATX")
    with open(Path(current_app.config["UPLOAD_FOLDER"]) / "report.md", "w") as f:
        f.write(tmp)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], "report.md")
