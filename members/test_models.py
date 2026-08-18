"""
members/test_models.py

Tests for the Governorate model's unique constraint (item #10).
"""
from django.db import IntegrityError, transaction
from django.test import TestCase

from members.models import Governorate


class GovernorateUniqueConstraintTests(TestCase):
    def test_duplicate_governorate_name_raises_integrity_error(self):
        Governorate.objects.create(governorate_name="Cairo")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Governorate.objects.create(governorate_name="Cairo")

    def test_get_or_create_does_not_duplicate(self):
        gov1, created1 = Governorate.objects.get_or_create(governorate_name="Giza")
        gov2, created2 = Governorate.objects.get_or_create(governorate_name="Giza")

        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertEqual(gov1.id, gov2.id)
        self.assertEqual(Governorate.objects.filter(governorate_name="Giza").count(), 1)
