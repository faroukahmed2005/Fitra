"""
Django management command to grant (or revoke) the Firebase "admin" custom
claim for a user, identified by email.

Usage:
    docker compose exec app python manage.py make_firebase_admin --email admin@example.com
    docker compose exec app python manage.py make_firebase_admin --email admin@example.com --revoke
"""
from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth


class Command(BaseCommand):
    help = "Grant or revoke the Firebase 'admin' custom claim for a user by email."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            required=True,
            help="Email address of the Firebase user to modify.",
        )
        parser.add_argument(
            "--revoke",
            action="store_true",
            help="Remove admin privileges instead of granting them.",
        )

    def handle(self, *args, **options):
        email = options["email"]
        revoke = options["revoke"]

        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            raise CommandError(f"No Firebase user found with email: {email}")
        except Exception as e:
            raise CommandError(f"Failed to look up user: {e}")

        # Preserve any other existing custom claims instead of overwriting them
        existing_claims = user.custom_claims or {}
        existing_claims["admin"] = not revoke

        try:
            auth.set_custom_user_claims(user.uid, existing_claims)
        except Exception as e:
            raise CommandError(f"Failed to set custom claims: {e}")

        if revoke:
            self.stdout.write(self.style.SUCCESS(
                f"Removed admin privileges from {email} (uid: {user.uid})"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Granted admin privileges to {email} (uid: {user.uid})"
            ))

        self.stdout.write(
            "Note: if this user has an active session/token, they must sign in "
            "again (or refresh their ID token) before the new claim takes effect."
        )
