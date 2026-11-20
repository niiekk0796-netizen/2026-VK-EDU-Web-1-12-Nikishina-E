from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ["author"]
    fields = ["author", "text", "score", "accepted"]
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created", "score"]
    search_fields = ["title", "author__username"]
    list_filter = ["created"]
    list_select_related = ["author"]
    raw_id_fields = ["author", "tags"]
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "author", "score", "accepted"]
    search_fields = ["text", "author__username"]
    list_filter = ["accepted", "created"]
    list_select_related = ["question", "author"]
    raw_id_fields = ["question", "author"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]
    list_filter = ["name"]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "question", "value"]
    search_fields = ["user__username", "question__title"]
    list_filter = ["value"]
    list_select_related = ["user", "question"]
    raw_id_fields = ["user", "question"]


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "answer", "value"]
    search_fields = ["user__username", "answer__text"]
    list_filter = ["value"]
    list_select_related = ["user", "answer"]
    raw_id_fields = ["user", "answer"]
