import os
import traceback
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models import PendingRegistration


class Command(BaseCommand):
    help = (
        "Delete PendingRegistration records (and their pending photo files) "
        "that are older than 24 hours and were never activated."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=24,
            help='Delete pending registrations older than this many hours (default: 24).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting anything.',
        )

    def handle(self, *args, **options):
        max_age_hours = options['max_age_hours']
        dry_run = options['dry_run']

        cutoff = timezone.now() - timedelta(hours=max_age_hours)
        expired_qs = PendingRegistration.objects.filter(created_at__lt=cutoff)
        count = expired_qs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired pending registrations found.'))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would delete {count} pending registration(s) '
                    f'older than {max_age_hours} hour(s).'
                )
            )
            for pr in expired_qs:
                self.stdout.write(f'  - id={pr.id}  email={pr.email}  created={pr.created_at}')
            return

        # Delete associated files first, then the DB rows.
        deleted_files = 0
        failed_files = 0

        for pr in expired_qs:
            for pp in pr.pending_pictures.all():
                try:
                    if pp.image and os.path.isfile(pp.image.path):
                        os.remove(pp.image.path)
                        deleted_files += 1
                except Exception:
                    failed_files += 1
                    traceback.print_exc()

        expired_qs.delete()

        msg = (
            f'Deleted {count} expired pending registration(s) '
            f'({deleted_files} photo file(s) removed'
        )
        if failed_files:
            msg += f', {failed_files} file(s) could not be removed — check logs'
        msg += ').'

        self.stdout.write(self.style.SUCCESS(msg))

        # TODO: wire this command to a cron job or Celery beat task so it runs
        # automatically (e.g. once per hour).  For now, run manually:
        #   docker compose exec app python manage.py cleanup_pending_registrations
