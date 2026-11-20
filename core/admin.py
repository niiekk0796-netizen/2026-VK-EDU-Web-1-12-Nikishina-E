from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0


admin.site.unregister(User)


@admin.register(User)
class AccountAdmin(UserAdmin):
    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "nickname", "rating"]
    search_fields = ["user__username", "nickname"]
    list_filter = ["user__is_active", "user__is_staff"]
    list_select_related = ["user"]
    raw_id_fields = ["user"]
