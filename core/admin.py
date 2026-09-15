from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Agreement, Clause, Disposition, Flag, FlagDecision, Provision, User


@admin.register(User)
class CalderUserAdmin(UserAdmin):
    # Show the role in the user list, and let an admin set it on the user's page.
    list_display = ("username", "email", "role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Calder role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Calder role", {"fields": ("role",)}),)


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("vendor", "agreement_type", "business_unit", "status", "submitted_by", "submitted_at")
    list_filter = ("status", "agreement_type")


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ("agreement", "provision", "kind", "severity", "confidence", "status")
    list_filter = ("kind", "severity", "status", "source")


admin.site.register([Provision, Clause, FlagDecision, Disposition])
