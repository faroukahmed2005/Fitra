from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import (Governorate,Member,PendingMember,Goals,Picture,HearAboutUs,)
# -----------------------
# Inline لعرض الأهداف
# -----------------------
class GoalsInline(admin.TabularInline):
    model = Goals
    extra = 0
    readonly_fields = ('goal',)
    can_delete = True

# -----------------------
# Inline لعرض الصور
# -----------------------
class PictureInline(admin.TabularInline):
    model = Picture
    extra = 0
    readonly_fields = ('image_tag',)
    can_delete = True

    def image_tag(self, obj):
        if obj.images:
            return mark_safe(f'<img src="{obj.images.url}" width="100" style="border-radius:8px;"/>')
        return "-"
    image_tag.short_description = 'Image'


class HearAboutUsInline(admin.TabularInline):
    model = HearAboutUs
    extra = 0
    readonly_fields = ("source",)
    can_delete = True

# -----------------------
# Member Admin
# -----------------------
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'place', 'plan', 'join_date', 'training_type')
    list_filter = ('gender', 'plan', 'training_type', 'place')
    search_fields = ('name', 'whatsapp_number', 'email', 'telegram_username')
    ordering = ('-join_date',)
    readonly_fields = ('join_date', 'weight_measure_date')
    inlines = [GoalsInline, HearAboutUsInline, PictureInline]   
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'age', 'gender', 'education', 'place', 'whatsapp_number', 'email', 'telegram_username')
        }),
        ('Body Info', {
            'fields': ('height', 'weight', 'weight_measure_date', 'sizes', 'measure_scale')
        }),
        ('Fitness Plan', {
            'fields': ('plan', 'meals_num', 'training_type', 'workout_days', 'daily_spend')
        }),
        ('History & Habits', {
            'fields': ('before_nutrition', 'injuries', 'previous_gym', 'another_sports', 'habits')
        }),
        ('Motivation & Feedback', {
            'fields': ('confidence', 'comeback', 'recommend_us')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_activated=True)

# -----------------------
# Pending Member Admin
# -----------------------
@admin.register(PendingMember)
class PendingMemberAdmin(MemberAdmin):

    def get_queryset(self, request):
        return Member.objects.filter(is_activated=False)

# -----------------------
# Governorate Admin
# -----------------------
@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ('governorate_name',)
    search_fields = ('governorate_name',)

    def has_module_permission(self, request):
        return False 

# -----------------------
# Goals Admin
# -----------------------
@admin.register(Goals)
class GoalsAdmin(admin.ModelAdmin):
    list_display = ('member', 'goal')
    list_filter = ('goal',)
    search_fields = ('member__name',)

    def has_module_permission(self, request):
        return False 

# -----------------------
# Picture Admin
# -----------------------
@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('member', 'image_tag')
    readonly_fields = ('image_tag',)

    def has_module_permission(self, request):
        return False 

    def image_tag(self, obj):
        if obj.images:
            return mark_safe(f'<img src="{obj.images.url}" width="100" style="border-radius:8px;"/>')
        return "-"
    image_tag.short_description = 'Image'


@admin.register(HearAboutUs)
class HearAboutUsAdmin(admin.ModelAdmin):
    list_display = ('member', 'source')
    list_filter = ('source',)
    search_fields = ('member__name',)

    def has_module_permission(self, request):
        return False