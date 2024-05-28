import pandas as pd
import pytest


@pytest.fixture
def participants_json():
    return {
        "participant_id": {"Annotations": {"IsAbout": {"TermURL": "", "Label": ""}}},
        "age": {
            "Annotations": {
                "IsAbout": {"TermURL": "nb:Age", "Label": ""},
                "Transformation": {"TermURL": "nb:FromInt", "Label": "integer data"},
                "MissingValues": ["", "n/a", " "],
            }
        },
    }


@pytest.fixture
def participants_df():
    return pd.DataFrame(
        {
            "participant_id": [
                "sub-01",
                "sub-02",
                "sub-03",
                "sub-04",
                "sub-05",
                "sub-06",
                "sub-07",
                "sub-08",
                "sub-09",
                "sub-10",
                "sub-11",
                "sub-12",
                "sub-13",
                "sub-14",
                "sub-15",
                "sub-16",
            ],
            "age": [
                26,
                24,
                27,
                20,
                22,
                26,
                24,
                21,
                26,
                21,
                24,
                22,
                21,
                30,
                24,
                19,
            ],
            "sex": [
                "F",
                "M",
                "F",
                "F",
                "M,",
                "F",
                "M",
                "M",
                "M",
                "F",
                "F",
                "F",
                "F",
                "F",
                "F",
                "M",
            ],
        }
    )
