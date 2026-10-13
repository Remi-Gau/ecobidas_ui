from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile

from ecobidas_ui.protocols.utils import prep_activity_page

BIDS_TEMPLATE = Path(__file__).parents[2] / "inputs" / "bids_template"

MRI_ACQUISITION_URL = "/en/protocol/neurovault/mri_acquisition"
PARTICIPANTS_URL = "/en/protocol/neurovault/participants"


def test_activity_items_are_not_shared_between_requests():
    _, _, items = prep_activity_page("neurovault", "participants")
    for item in items.values():
        item["is_answered"] = True
        item["visibility"] = True

    _, _, new_items = prep_activity_page("neurovault", "participants")

    assert not any(item["is_answered"] for item in new_items.values())
    assert not all(item["visibility"] for item in new_items.values())


def upload_bold_json(client, file):
    return client.post(
        MRI_ACQUISITION_URL,
        {"mri_acquisition-bold_json": file, "submit_bold_json": ""},
        follow=True,
    )


def test_upload_bold_json(client):
    with open(BIDS_TEMPLATE / "task-auditoryLocalizer_bold.json", "rb") as f:
        response = upload_bold_json(client, f)

    assert response.status_code == 200
    content = response.content.decode()
    assert "The following fields were updated" in content
    assert "RepetitionTime" in content
    assert 'value="1.8"' in content


def test_upload_bold_json_without_values(client):
    bold_json = (
        BIDS_TEMPLATE
        / "sub-01"
        / "ses-01"
        / "func"
        / "sub-01_ses-01_task-FullExample_run-01_bold.json"
    )
    with open(bold_json, "rb") as f:
        response = upload_bold_json(client, f)

    content = response.content.decode()
    assert "No field could be updated: the file has no values for" in content
    assert "RepetitionTime" in content


def test_upload_bold_json_without_known_fields(client):
    response = upload_bold_json(client, SimpleUploadedFile("bold.json", b'{"foo": 1}'))

    assert "the file has none of the fields of this page" in response.content.decode()


def test_upload_invalid_bold_json(client):
    response = upload_bold_json(client, SimpleUploadedFile("bold.json", b"not json"))

    assert response.status_code == 200
    assert "The uploaded file could not be read." in response.content.decode()


def upload_participants(client, files):
    return client.post(
        PARTICIPANTS_URL,
        {"upload-participants": files, "submit_upload": ""},
        follow=True,
    )


def test_upload_participants(client):
    with (
        open(BIDS_TEMPLATE / "participants.tsv", "rb") as tsv,
        open(BIDS_TEMPLATE / "participants.json", "rb") as json_file,
    ):
        response = upload_participants(client, [tsv, json_file])

    content = response.content.decode()
    assert "The following fields were updated" in content
    assert "number_of_subjects" in content


def test_upload_invalid_participants(client):
    with open(BIDS_TEMPLATE / "participants.tsv", "rb") as tsv:
        response = upload_participants(
            client,
            [tsv, SimpleUploadedFile("participants.json", b"not json")],
        )

    assert response.status_code == 200
    assert "The uploaded files could not be read." in response.content.decode()
