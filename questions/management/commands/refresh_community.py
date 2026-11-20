from datetime import timedelta

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from core.models import Profile
from questions.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        week = timezone.now() - timedelta(days=7)
        tags = list(Tag.objects.annotate(total=Count("questions")).order_by("-total", "name")[:20])
        members = list(Profile.objects.filter(
            Q(user__questions__created__gte=week) | Q(user__answers__created__gte=week)
        ).distinct().order_by("-rating", "pk").values_list("nickname", flat=True)[:10])
        cache.set("community", {"popular_tags": tags, "best_members": members}, timeout=3600)
        self.stdout.write("Списки тегов и участников обновлены.")
