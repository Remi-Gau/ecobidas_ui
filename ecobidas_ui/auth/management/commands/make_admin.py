from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Give access to the admin site to a user, identified by their ORCID iD."

    def add_arguments(self, parser):
        parser.add_argument("orcid_id", help="for example: 0000-0002-1825-0097")
        parser.add_argument(
            "--remove", action="store_true", help="remove the access to the admin site instead"
        )

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options["orcid_id"])
        except User.DoesNotExist as exc:
            raise CommandError(
                f"No user with the ORCID iD {options['orcid_id']}: they must log in once first."
            ) from exc

        user.is_staff = user.is_superuser = not options["remove"]
        user.save()
        action = "removed from" if options["remove"] else "given access to"
        self.stdout.write(self.style.SUCCESS(f"{user.username} was {action} the admin site."))
