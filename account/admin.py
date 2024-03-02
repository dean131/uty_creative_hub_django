from django.contrib import admin

from . import models


class UserModelAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "is_active", "verification_status",  "is_admin"]
    list_filter = ["is_admin", "is_active"]
    search_fields = ["email", "full_name"]

    class Meta:
        model = models.User


class OTPCodeModelAdmin(admin.ModelAdmin):
    list_display = ["user", "code"]
    list_filter = ["user"]
    search_fields = ["user", "code"]

    class Meta:
        model = models.OTPCode


admin.site.register(models.OTPCode, OTPCodeModelAdmin)
admin.site.register(models.User, UserModelAdmin)
admin.site.register(models.UserProfile)
