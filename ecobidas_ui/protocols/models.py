from typing import Any

import numpy as np
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class AnswersEncoder(DjangoJSONEncoder):
    """Also encode the numpy numbers extracted from uploaded files."""

    def default(self, o: Any) -> Any:
        if isinstance(o, np.generic):
            return o.item()
        return super().default(o)


class SavedAnswers(models.Model):
    """Answers of a user to the items of an activity."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_answers"
    )
    protocol = models.CharField(max_length=100)
    activity = models.CharField(max_length=100)
    answers = models.JSONField(default=dict, encoder=AnswersEncoder)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "saved answers"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "protocol", "activity"], name="unique_answers_per_activity"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.protocol} - {self.activity}"


def load_answers(user, protocol: str, activity: str) -> dict[str, Any]:
    if not user.is_authenticated:
        return {}
    saved = SavedAnswers.objects.filter(user=user, protocol=protocol, activity=activity).first()
    return saved.answers if saved else {}


def save_answers(user, protocol: str, activity: str, answers: dict[str, Any]) -> None:
    SavedAnswers.objects.update_or_create(
        user=user, protocol=protocol, activity=activity, defaults={"answers": answers}
    )
