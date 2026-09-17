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


@admin.register(Provision)
class ProvisionAdmin(admin.ModelAdmin):
    """The playbook. Severity, method and keywords are the settings an administrator changes."""

    list_display = ("name", "cuad_category", "default_severity", "method", "keyword_count")
    list_filter = ("default_severity", "method")
    fields = ("name", "cuad_category", "default_severity", "method", "keywords", "definition",
              "standard_position", "required")

    @admin.display(description="Keywords")
    def keyword_count(self, provision):
        return len([line for line in provision.keywords.splitlines() if line.strip()])


admin.site.register([Clause, FlagDecision, Disposition])
