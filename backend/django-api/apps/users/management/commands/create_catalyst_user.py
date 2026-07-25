"""
Django management command: create_catalyst_user
================================================
Creates a test user in the Zoho Catalyst User Management cloud
using the zcatalyst-sdk's built-in authentication service.

Usage:
    python manage.py create_catalyst_user --email test@example.com --first-name John --last-name Doe

Note:
    This command works when run INSIDE the AppSail container (where Catalyst
    env vars are injected automatically). For local testing, add the Catalyst
    OAuth token to .env.
"""
import os
import json
from django.core.management.base import BaseCommand, CommandError
from apps.users.models import User


class Command(BaseCommand):
    help = "Create a user in Zoho Catalyst User Management and sync to local DB"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="", help="User email address")
        parser.add_argument("--first-name", default="Test", help="First name")
        parser.add_argument("--last-name", default="User", help="Last name")
        parser.add_argument("--role", default="Investigator", help="Catalyst role name")
        parser.add_argument(
            "--local-only",
            action="store_true",
            help="Skip Catalyst API call, only create in local Django DB (for testing)",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all users currently in the local Django DB",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self._list_local_users()
            return

        email = options["email"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        if options["local_only"]:
            self._create_local_only(email, first_name, last_name, options["role"])
        else:
            self._create_via_catalyst(email, first_name, last_name)

    def _list_local_users(self):
        """List all users in the local Django DB."""
        self.stdout.write(self.style.SUCCESS("\n-- Local Django DB Users ----------------------------------"))
        users = User.objects.all().order_by("-date_joined")
        if not users.exists():
            self.stdout.write("  No users found.")
            return

        for u in users:
            self.stdout.write(
                f"  {u.email or u.username:<35} "
                f"role={u.role:<15} "
                f"provider={u.auth_provider:<10} "
                f"catalyst_uid={u.catalyst_user_id or 'N/A'}"
            )
        self.stdout.write(f"\n  Total: {users.count()} user(s)")

    def _create_local_only(self, email, first_name, last_name, role_name):
        """Create a user only in the local Django DB (for dev/testing)."""
        from apps.users.repository import UserRepository

        fake_catalyst_user = {
            "user_id": f"local-test-{email}",
            "email_id": email,
            "first_name": first_name,
            "last_name": last_name,
            "platform": "email",
            "role_details": {"role_name": role_name},
        }

        try:
            user, created = UserRepository.get_or_create_from_catalyst(fake_catalyst_user)
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"[CREATED] New user synced to local DB:\n"
                    f"   Email:    {user.email}\n"
                    f"   Role:     {user.role}\n"
                    f"   ID:       {user.id}\n"
                    f"   Username: {user.username}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"[EXISTS] User already exists in local DB:\n"
                    f"   Email:    {user.email}\n"
                    f"   Role:     {user.role}\n"
                    f"   ID:       {user.id}"
                ))
        except Exception as e:
            raise CommandError(f"Failed to create local user: {e}")

    def _create_via_catalyst(self, email, first_name, last_name):
        """Create a user in the Catalyst cloud via the zcatalyst-sdk."""
        try:
            import zcatalyst_sdk
            self.stdout.write("Initializing Catalyst SDK...")

            # In AppSail, the SDK auto-reads credentials from the environment
            app = zcatalyst_sdk.initialize()
            auth = app.authentication()

            signup_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email_id": email,
                "platform_type": "web",
                "redirect_url": os.getenv("FRONTEND_URL", "https://vigilx.onslate.in"),
            }

            self.stdout.write(f"Creating user in Catalyst: {email}")
            result = auth.sign_up(signup_data)

            self.stdout.write(self.style.SUCCESS(
                f"✅ User created in Catalyst!\n"
                f"   Catalyst Response: {json.dumps(result, indent=4, default=str)}\n\n"
                f"ℹ️  An invitation email has been sent to: {email}\n"
                f"   The user must accept the invite to complete registration.\n"
                f"   Once they log in at https://vigilx.onslate.in,\n"
                f"   the backend will automatically sync them to the local DB."
            ))

        except ImportError:
            raise CommandError("zcatalyst-sdk not installed. Run: pip install zcatalyst-sdk")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Catalyst SDK error: {e}"))
            self.stdout.write(self.style.WARNING(
                "\nTip: This command works best when run inside the AppSail container.\n"
                "For local testing, use --local-only flag instead:\n"
                f"  python manage.py create_catalyst_user --email {email} --first-name {first_name} --last-name {last_name} --local-only"
            ))
