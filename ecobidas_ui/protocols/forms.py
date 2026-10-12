import json
from pathlib import Path

import pandas as pd
from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]


class UploadParticipantsForm(forms.Form):
    participants = MultipleFileField(
        label=_("Upload participants.tsv and participants.json"),
        validators=[
            FileExtensionValidator(
                ["tsv", "json"], message=_("File must be '.tsv' and '.json' files.")
            )
        ],
    )


def validate_participants_json(participants_json: Path | str | dict):
    if not isinstance(participants_json, dict):
        with open(Path(participants_json)) as f:
            participants_json = json.load(f)
    return bool(
        participants_json.get("participant_id")
        and participants_json["participant_id"].get("Annotations")
    )


def validate_participants_tsv(participants_tsv: Path | pd.DataFrame):
    if not isinstance(participants_tsv, pd.DataFrame):
        participants_tsv = pd.read_csv(participants_tsv, sep="\t")
    return "participant_id" in participants_tsv.columns


class UploadBoldJsonForm(forms.Form):
    bold_json = forms.FileField(
        label=_("Upload bold.json"),
        validators=[
            FileExtensionValidator(["json"], message=_("The file must be a '.json' file."))
        ],
    )


def generate_form(items=None, prefix=None, obj=None, data=None, initial=None) -> forms.Form:
    """Generate a form for the items of an activity.

    Values are taken from ``data`` (submitted values),
    then ``initial``, then the attributes of ``obj``.
    """
    fields = {}

    for item_name, item in items.items():

        attrs = (
            {"style": "border-color: green; border-width: 2px;"}
            if item["is_answered"]
            else {"style": "border-color: red; border-width: 2px;"}
        )

        kwargs = {
            "required": bool(item["required"]),
            "help_text": mark_safe(item["description"]),
        }

        question = f"{item['question']} {item['unit']}"

        if not item["visibility"]:
            fields[item_name] = forms.CharField(
                label=mark_safe(question), widget=forms.HiddenInput, **kwargs
            )
            continue

        input_type = item["input_type"]

        if input_type == "date":
            fields[item_name] = forms.DateField(
                label=mark_safe(question),
                input_formats=["%Y-%m-%d"],
                widget=forms.DateInput(attrs={**attrs, "type": "date"}, format="%Y-%m-%d"),
                **kwargs,
            )

        elif input_type not in ["select", "radio", "slider"]:

            field_kwargs = {}
            FieldType = forms.CharField
            widget = forms.TextInput
            if input_type == "number":
                FieldType = forms.IntegerField
                widget = forms.NumberInput
            elif input_type == "float":
                FieldType = forms.DecimalField
                widget = forms.NumberInput
            elif input_type == "textarea":
                widget = forms.Textarea

            if input_type in ["number", "float"]:
                minimum = item["min"]
                maximum = item["max"]
                field_kwargs = {"min_value": minimum, "max_value": maximum}
                if minimum is not None and maximum is not None:
                    question += f" ({minimum=}, {maximum=})"
                elif minimum is not None:
                    question += f" ({minimum=})"

            fields[item_name] = FieldType(
                label=mark_safe(question), widget=widget(attrs=attrs), **field_kwargs, **kwargs
            )

        elif input_type == "slider":

            min_label = float(item["choices"][0][1])
            max_label = float(item["choices"][-1][1])

            question += f" (min={min_label}, max={max_label})"

            fields[item_name] = forms.DecimalField(
                label=mark_safe(question),
                min_value=min_label,
                max_value=max_label,
                widget=forms.NumberInput(attrs=attrs),
                **kwargs,
            )

        else:

            fields[item_name] = choice_based_field(item, attrs, kwargs)

    DynamicForm = type("DynamicForm", (forms.Form,), fields)

    initial = dict(initial or {})
    if obj is not None:
        for key in fields:
            if getattr(obj, key, None) is not None:
                initial[key] = getattr(obj, key)

    return DynamicForm(data=data, prefix=prefix, initial=initial)


def choice_based_field(item: dict, attrs: dict, kwargs: dict) -> forms.Field:

    question = f"{item['question']} {item['unit']}"

    input_type = item["input_type"]

    if item["is_multiple"]:
        FieldType, widget = forms.MultipleChoiceField, forms.SelectMultiple
    elif input_type == "select":
        FieldType, widget = forms.ChoiceField, forms.Select
    elif input_type == "radio":
        FieldType, widget = forms.ChoiceField, forms.RadioSelect

    return FieldType(
        label=mark_safe(question),
        choices=item["choices"],
        widget=widget(attrs=attrs),
        **kwargs,
    )
