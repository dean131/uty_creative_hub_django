from django.contrib import admin

from . import models


class UserModelAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "is_active", "verification_status",  "is_admin"]
    list_filter = ["is_admin", "is_active"]
    search_fields = ["email", "full_name"]

    class Meta:
        model = models.User


admin.site.register(models.User, UserModelAdmin)
admin.site.register(models.UserProfile)
