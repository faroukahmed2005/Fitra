"""
settings/test_models.py

Tests for PackadgeFeature (unique_together, ordering) and the homepage
view's prefetch_related usage (item #8).

NOTE ON APP LOCATION: place this file in whichever app actually contains
Packadges/Feature/PackadgeFeature/home() -- based on the models.py and
views.py you shared, that's the app registered as 'settings' in
INSTALLED_APPS. If your homepage URL isn't simply '/', update
HOMEPAGE_URL below to match your project's urls.py.
"""
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection

from .models import Packadges, Feature, PackadgeFeature, Info, Brief, AboutUs, Footer

HOMEPAGE_URL = "/"


def make_test_image(name="img.jpg"):
    return SimpleUploadedFile(name, b"\xff\xd8\xff" + b"0" * 50, content_type="image/jpeg")


def seed_required_singletons():
    """
    The homepage template calls .url directly on several singleton
    ImageFields (info.logo, brief.brief_image, about_us.about_us_image)
    with no {% if %} guard. If these are empty -- e.g. a fresh database,
    or an admin accidentally clearing the field -- Django raises a hard
    ValueError and the homepage 500s. That's a real, separate issue
    (worth adding {% if %} guards in settings/home.html), not something
    these tests are meant to cover. We seed real files here purely so
    these tests can reach the part of the page we're actually testing.
    """
    info = Info.get_solo()
    info.logo = make_test_image("logo.jpg")
    info.slogan = "Test slogan"
    info.save()

    brief = Brief.get_solo()
    brief.brief_title = "Test brief"
    brief.brief_content = "content"
    brief.brief_image = make_test_image("brief.jpg")
    brief.save()

    about_us = AboutUs.get_solo()
    about_us.about_us_content = "about"
    about_us.about_us_image = make_test_image("about.jpg")
    about_us.save()

    footer = Footer.get_solo()
    footer.footer_slogan = "one two three four five six seven eight nine ten"
    footer.save()


def make_package(name="Basic Plan", n_features=3):
    package = Packadges.objects.create(
        name=name,
        before_price=Decimal("500.00"),
        after_price=Decimal("400.00"),
        time="1 Month",
        image="settings/placeholder.jpg",
    )
    for i in range(n_features):
        feature = Feature.objects.create(text=f"Feature {i}")
        PackadgeFeature.objects.create(
            package=package, feature=feature, is_included=True, order=i
        )
    return package


class PackadgeFeatureConstraintTests(TestCase):
    def test_same_feature_cannot_be_attached_twice_to_same_package(self):
        package = Packadges.objects.create(
            name="Test Pack", before_price=Decimal("100"), after_price=Decimal("80"),
            time="1 Month", image="settings/placeholder.jpg",
        )
        feature = Feature.objects.create(text="Excel sheet")
        PackadgeFeature.objects.create(package=package, feature=feature, order=0)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PackadgeFeature.objects.create(package=package, feature=feature, order=1)

    def test_features_are_returned_in_order(self):
        package = Packadges.objects.create(
            name="Ordered Pack", before_price=Decimal("100"), after_price=Decimal("80"),
            time="1 Month", image="settings/placeholder.jpg",
        )
        f1 = Feature.objects.create(text="Third")
        f2 = Feature.objects.create(text="First")
        f3 = Feature.objects.create(text="Second")
        PackadgeFeature.objects.create(package=package, feature=f1, order=2)
        PackadgeFeature.objects.create(package=package, feature=f2, order=0)
        PackadgeFeature.objects.create(package=package, feature=f3, order=1)

        ordered_texts = [pf.feature.text for pf in package.packadgefeature_set.all()]
        self.assertEqual(ordered_texts, ["First", "Second", "Third"])


class HomepageNPlusOneTests(TestCase):
    """
    Confirms prefetch_related('packadgefeature_set__feature') keeps the
    query count flat regardless of how many packages/features exist --
    the actual regression test for item #8.
    """

    def test_query_count_does_not_scale_with_package_count(self):
        seed_required_singletons()
        make_package("Pack A", n_features=3)

        # Warm django-solo's cache for Info/Brief/AboutUs/Footer BEFORE either
        # measurement. get_solo() caches its result after first lookup, so
        # without this warm-up, whichever request happens first pays extra
        # "cold cache" queries that have nothing to do with packages/features
        # -- that mismatch previously made the comparison meaningless.
        self.client.get(HOMEPAGE_URL)

        with CaptureQueriesContext(connection) as queries_one_pack:
            response = self.client.get(HOMEPAGE_URL)
            self.assertEqual(response.status_code, 200)
            _ = response.content
        count_with_one_pack = len(queries_one_pack.captured_queries)

        make_package("Pack B", n_features=3)
        make_package("Pack C", n_features=3)

        with CaptureQueriesContext(connection) as queries_three_packs:
            response = self.client.get(HOMEPAGE_URL)
            self.assertEqual(response.status_code, 200)
            _ = response.content
        count_with_three_packs = len(queries_three_packs.captured_queries)

        self.assertEqual(
            count_with_one_pack,
            count_with_three_packs,
            "Query count grew as packages were added -- prefetch_related "
            "may not be covering the features relation correctly (N+1 regression)."
        )
