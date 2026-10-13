from django.contrib import admin

from ecobidas_ui.protocols.models import SavedAnswers


@admin.register(SavedAnswers)
class SavedAnswersAdmin(admin.ModelAdmin):
    list_display = ["user", "protocol", "activity", "updated"]
    list_filter = ["protocol"]
    search_fields = ["user__username", "user__first_name"]
