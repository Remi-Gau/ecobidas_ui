import json
import logging
from typing import Any

import pandas as pd
from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from ecobidas_ui.protocols.expressions import is_true, to_value
from ecobidas_ui.protocols.forms import (
    UploadBoldJsonForm,
    UploadParticipantsForm,
    generate_form,
    validate_participants_json,
    validate_participants_tsv,
)
from ecobidas_ui.protocols.utils import (
    activity_in_protocol,
    allowed_file,
    extract_values_participants,
    get_landing_page,
    get_nav_bar_content,
    get_preamble,
    get_prefLabel,
    get_protocol,
    prep_activity_page,
    protocol_url,
    update_format,
)
from ecobidas_ui.views import render_error, require_methods

KNWON_PROTOCOLS = ["neurovault", "eyetracking", "pet", "cobidas", "reexecution"]

logger = logging.getLogger(__name__)


@require_methods("GET", "POST")
def protocol(request, protocol_name: str):

    if protocol_name not in KNWON_PROTOCOLS:
        messages.warning(request, _("unknown protocol_name"))
        return render_error(request, 404)

    protocol_content = get_protocol(protocol_name)

    landing_page_url = protocol_url(protocol_name).parent / protocol_content["landingPage"]["@id"]
    landing_page = get_landing_page(landing_page_url)

    activities = get_nav_bar_content(protocol_name)

    return render(
        request,
        "protocols/protocol.html",
        {
            "protocol_pref_label": protocol_name,
            "protocol_preamble": get_preamble(protocol_content),
            "activities": activities,
            "landing_page": landing_page,
            "show_export_button": show_export_button(protocol_name),
        },
    )


def show_export_button(protocol_name):
    return protocol_name in ["neurovault", "cobidas"]


@require_methods("GET", "POST")
def activity(request, protocol_name: str, activity_name: str):

    if protocol_name not in KNWON_PROTOCOLS or not activity_in_protocol(
        protocol_name, activity_name
    ):
        return render_error(request, 404)

    if request.method == "POST":
        return activity_post(request, protocol_name, activity_name)

    activities, activity, items = prep_activity_page(protocol_name, activity_name)

    upload_participants_form, extra_form = generate_extra_forms(
        request, protocol_name, activity_name
    )

    form = generate_form(items=items, prefix=activity_name)

    return render_activity(
        request,
        protocol_name,
        activity,
        activities,
        items,
        form,
        upload_participants_form,
        extra_form,
    )


def activity_post(request, protocol_name: str, activity_name: str):

    logger.info(f"{protocol_name}-{activity_name}")

    activities, activity, items = prep_activity_page(protocol_name, activity_name)

    base_nb_items = sum(bool(i["visibility"]) for i in items.values())

    upload_participants_form, extra_form = generate_extra_forms(
        request, protocol_name, activity_name
    )

    form = generate_form(items=items, prefix=activity_name, data=request.POST)
    form_data = get_form_data(form)
    # keep the submitted values without displaying validation errors
    form = generate_form(items=items, prefix=activity_name, initial=form_data)

    upload_submitted = False
    found = None
    if (
        upload_participants_form is not None
        and "submit_upload" in request.POST
        and upload_participants_form.is_valid()
    ):
        upload_submitted = True
        found = read_participants_upload(request, upload_participants_form)
    elif extra_form is not None and "submit_bold_json" in request.POST and extra_form.is_valid():
        upload_submitted = True
        found = read_bold_json_upload(request, extra_form)

    if upload_submitted:
        if found is None:
            return redirect(request.get_full_path())

        form, items, fields = process_upload_form(form_data, activity_name, items, found)

        if not fields:
            messages.warning(request, no_field_updated_message(found, form))
            return redirect(request.get_full_path())

        messages.success(request, f"{_('The following fields were updated:')} {fields}")

    elif "submit" in request.POST:
        if "messages" in activity:
            for message in validate_activity(activity["messages"], items, form_data):
                messages.error(request, message)

        form, items = update_items_and_forms(form_data, items, activity_name)

    nb_items = sum(bool(i["visibility"]) for i in items.values())

    messages.success(request, _("Your data was saved."))

    if nb_items > base_nb_items:
        # update so it gets the right number and the names of items added
        messages.success(request, f"{nb_items - base_nb_items}  {_('items were added.')}")

    return render_activity(
        request,
        protocol_name,
        activity,
        activities,
        items,
        form,
        upload_participants_form,
        extra_form,
    )


def render_activity(
    request,
    protocol_name,
    activity,
    activities,
    items,
    form,
    upload_participants_form,
    extra_form,
):
    completed_items = sum(bool(i["is_answered"]) for i in items.values())
    nb_items = sum(bool(i["visibility"]) for i in items.values())

    return render(
        request,
        "protocols/protocol.html",
        {
            "protocol_pref_label": protocol_name,
            "activity_pref_label": get_prefLabel(activity),
            "activity_preamble": get_preamble(activity),
            "activities": activities,
            "form": form,
            "progress": progress_bar(completed_items, nb_items),
            "upload_participants_form": upload_participants_form,
            "upload_acquisition_form": extra_form,
            "show_export_button": show_export_button(protocol_name),
        },
    )


def progress_bar(completed_items: int, nb_items: int) -> dict[str, Any]:
    percent_completed = round(completed_items / nb_items * 100) if nb_items else 0

    color = "danger"
    if percent_completed > 80:
        color = "success"
    elif percent_completed > 60:
        color = "info"
    elif percent_completed > 40:
        color = "secondary"
    elif percent_completed > 20:
        color = "warning"

    return {
        "completed_items": completed_items,
        "nb_items": nb_items,
        "percent_completed": percent_completed,
        "color": color,
        "emoji": mark_safe("&#127881;") if completed_items == nb_items else "",
    }


def get_form_data(form: forms.Form) -> dict[str, Any]:
    """Return the submitted values of the form, cleaned whenever they are valid."""
    form.is_valid()
    cleaned_data = getattr(form, "cleaned_data", {})
    return {
        name: cleaned_data[name] if name in cleaned_data else form[name].value()
        for name in form.fields
    }


def generate_extra_forms(
    request, protocol_name, activity_name
) -> tuple[forms.Form | None, forms.Form | None]:

    upload_participants_form = None
    upload_acquisition_form = None

    if protocol_name not in ["neurovault", "cobidas"]:
        return upload_participants_form, upload_acquisition_form

    if (protocol_name == "neurovault" and activity_name == "participants") or (
        protocol_name == "cobidas" and activity_name == "sample"
    ):
        upload_participants_form = UploadParticipantsForm(
            *bound_form_args(request, "submit_upload"), prefix="upload"
        )

    if (protocol_name == "neurovault" and activity_name == "mri_acquisition") or (
        protocol_name == "cobidas" and activity_name == "common_parameters"
    ):
        upload_acquisition_form = UploadBoldJsonForm(
            *bound_form_args(request, "submit_bold_json"), prefix="mri_acquisition"
        )

    return upload_participants_form, upload_acquisition_form


def bound_form_args(request, submit_name: str) -> tuple:
    """Only bind an upload form to the request data if that form was submitted."""
    if request.method == "POST" and submit_name in request.POST:
        return request.POST, request.FILES
    return ()


def validate_participants_form(data):
    nb_files_uploaded = len(data)
    if nb_files_uploaded != 2:
        message = f"2 files must be uploaded. Received: {nb_files_uploaded}"
        return message

    participants_json_uploaded = any(file.name == "participants.json" for file in data)
    if not participants_json_uploaded:
        message = "No 'participants.json' was uploaded."
        return message

    participants_tsv_uploaded = any(file.name == "participants.tsv" for file in data)
    if not participants_tsv_uploaded:
        message = "No 'participants.tsv' was uploaded."
        return message

    else:
        return ""


class JsonMeta:
    def __init__(self, json_content: dict[str, Any]) -> None:
        for key in json_content:
            self.__setattr__(key, json_content[key])


def process_upload_form(form_data, activity_name, items, found):
    form, items = update_items_and_forms(form_data, items, activity_name, obj=found)
    fields = [key for key in found.__dir__() if getattr(found, key) and key in form.fields]
    return form, items, fields


def read_participants_upload(request, upload_form: forms.Form):
    """Extract values from the uploaded participants.tsv and participants.json.

    Return None and add a warning message if the files are not valid.
    """
    data = upload_form.cleaned_data["participants"]

    if message := validate_participants_form(data):
        messages.warning(request, message)
        return None

    files = {file.name: file for file in data}
    try:
        participants_tsv = pd.read_csv(files["participants.tsv"], sep="\t")
        participants_json = json.load(files["participants.json"])
    except ValueError:
        messages.warning(request, _("The uploaded files could not be read."))
        return None

    if not validate_participants_tsv(participants_tsv):
        message = _(
            "The 'participants.tsv' does not seem to be valid: 'participant_id' column is missing."
        )
        messages.warning(request, mark_safe(f"<p>{message}</p>"))
        return None

    if not validate_participants_json(participants_json):
        messages.warning(
            request,
            mark_safe(
                "<p>"
                f"{_('The `participants.json` was not annotated. ')}"
                f"{_('Annotate your data with the ')}"
                "<a href='https://annotate.neurobagel.org/' target='_blank'"
                "class='alert-link'>"
                f"{_('neurobagel online annotation tool')}"
                "</a></p>"
            ),
        )
        return None

    return extract_values_participants(participants_tsv, json_content=participants_json)


def read_bold_json_upload(request, upload_form: forms.Form):
    """Extract values from the uploaded bold.json.

    Return None and add a warning message if the file is not valid.
    """
    file = upload_form.cleaned_data["bold_json"]
    if not allowed_file(file.name):
        messages.warning(request, _("No '_bold.json' was uploaded."))
        return None

    try:
        return JsonMeta(json.load(file))
    except ValueError:
        messages.warning(request, _("The uploaded file could not be read."))
        return None


def no_field_updated_message(found, form: forms.Form) -> str:
    """Explain why no field could be updated from an uploaded file."""
    known_fields = [key for key in vars(found) if key in form.fields]
    if known_fields:
        return _("No field could be updated: the file has no values for %(fields)s.") % {
            "fields": ", ".join(known_fields)
        }
    return _("No field could be updated: the file has none of the fields of this page.")


def update_items_and_forms(form_data: dict, items, activity_name: str, obj=None):
    if obj is not None:
        for key in obj.__dir__():
            if key in form_data:
                form_data[key] = getattr(obj, key)

    items = update_visibility(items, form_data)
    items = update_format(items, form_data)
    form = generate_form(items, prefix=activity_name, obj=obj, initial=form_data)
    return form, items


def answers_to_values(items: dict[str, Any], form_data) -> dict[str, Any]:
    """Return the answers to the items as values usable in the schema expressions."""
    return {key: to_value(value) for key, value in form_data.items() if key in items}


def update_visibility(items: dict[str, Any], form_data):
    """Evaluate visibility condition of each item and make item visible if necessary."""
    values = answers_to_values(items, form_data)
    for item in items.values():
        if isinstance(item["isVis"], str):
            item["visibility"] = is_true(item["isVis"], values)
    return items


def validate_activity(
    activity_messages: list[dict[str, str]], items: dict[str, Any], form_data
) -> list[str]:
    """Return the validation messages of the activity whose condition is true."""
    values = answers_to_values(items, form_data)
    return [
        message["message"]
        for message in activity_messages or []
        if is_true(message["jsExpression"], values)
    ]
