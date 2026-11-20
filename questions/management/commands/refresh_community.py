from datetime import timedelta
from heapq import merge

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from questions.models import Answer, Question, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        week = timezone.now() - timedelta(days=7)
        tags = list(Tag.objects.annotate(total=Count("questions")).order_by("-total", "name")[:20])
        questions = Question.objects.filter(created__gte=week).order_by("-score", "-created").values_list("score", "author__profile__nickname")
        answers = Answer.objects.filter(created__gte=week).order_by("-score", "-created").values_list("score", "author__profile__nickname")
        members = []
        for score, nickname in merge(questions.iterator(chunk_size=2000), answers.iterator(chunk_size=2000), key=lambda row: row[0], reverse=True):
            if nickname not in members:
                members.append(nickname)
            if len(members) == 10:
                break
        cache.set("community", {"popular_tags": tags, "best_members": members}, timeout=3600)
        self.stdout.write("Списки тегов и участников обновлены.")
