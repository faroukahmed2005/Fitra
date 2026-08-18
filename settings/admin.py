from django import forms
from django_summernote.admin import SummernoteModelAdmin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from . import models
from solo.admin import SingletonModelAdmin
from adminsortable2.admin import SortableTabularInline, SortableAdminBase


class SingletonSummernoteAdmin(SummernoteModelAdmin, TranslationAdmin, SingletonModelAdmin):
    summernote_fields = '__all__'

class PackageFeatureInline(SortableTabularInline):
    model = models.PackageFeature
    extra = 1

class PackagesAdmin(SortableAdminBase, SummernoteModelAdmin, TranslationAdmin):
    summernote_fields = '__all__'
    list_display = ['name']
    inlines = [PackageFeatureInline]

admin.site.register(models.Info, SingletonSummernoteAdmin)
admin.site.register(models.Brief, SingletonSummernoteAdmin)
admin.site.register(models.AboutUs, SingletonSummernoteAdmin)
admin.site.register(models.SocialLinks, SingletonModelAdmin)

admin.site.register(models.SuccessfullStories)
admin.site.register(models.Packages, PackagesAdmin)
admin.site.register(models.Feature, TranslationAdmin)