from django.conf import settings
from django.db import models
from django.db.models import Count, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.urls import reverse


class QuestionQuerySet(models.QuerySet):
    def display(self, user=None):
        counts = Answer.objects.filter(question_id=OuterRef("pk")).values("question_id").annotate(total=Count("pk")).values("total")
        result = self.select_related("author__profile").prefetch_related("tags").annotate(answer_count=Coalesce(Subquery(counts), 0))
        if user and user.is_authenticated:
            votes = QuestionLike.objects.filter(question_id=OuterRef("pk"), user=user).values("value")
            return result.annotate(vote=Coalesce(Subquery(votes), 0))
        return result.annotate(vote=Value(0))

    def newest(self):
        return self.order_by("-created", "-pk")

    def best(self):
        return self.order_by("-score", "-created", "-pk")

    def search(self, query):
        return self.filter(Q(title__icontains=query) | Q(text__icontains=query)) if query else self

    def tagged(self, name):
        return self.filter(tags__name=name).best()


class Tag(models.Model):
    name = models.SlugField("Тег", max_length=40, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Question(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions", verbose_name="Автор")
    title = models.CharField("Заголовок", max_length=120)
    text = models.TextField("Текст", max_length=5000)
    tags = models.ManyToManyField(Tag, related_name="questions", verbose_name="Теги", blank=True)
    created = models.DateTimeField("Создан", auto_now_add=True)
    score = models.IntegerField("Рейтинг", default=0)
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        indexes = [models.Index(fields=["-created", "-id"]), models.Index(fields=["-score", "-created", "-id"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("questions:question", args=[self.pk])


class AnswerQuerySet(models.QuerySet):
    def ranked(self):
        return self.order_by("-score", "-created", "-pk")

    def display(self, user=None):
        result = self.select_related("author__profile")
        if user and user.is_authenticated:
            votes = AnswerLike.objects.filter(answer_id=OuterRef("pk"), user=user).values("value")
            return result.annotate(vote=Coalesce(Subquery(votes), 0))
        return result.annotate(vote=Value(0))


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers", verbose_name="Вопрос")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="answers", verbose_name="Автор")
    text = models.TextField("Текст", max_length=5000)
    created = models.DateTimeField("Создан", auto_now_add=True)
    score = models.IntegerField("Рейтинг", default=0)
    accepted = models.BooleanField("Правильный ответ", default=False)
    objects = AnswerQuerySet.as_manager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        indexes = [models.Index(fields=["question", "-score", "-created", "-id"])]
        constraints = [models.UniqueConstraint(fields=["question"], condition=Q(accepted=True), name="one_accepted_answer")]

    def __str__(self):
        return self.text[:80]

    def get_absolute_url(self):
        preceding = self.question.answers.filter(
            Q(score__gt=self.score)
            | Q(score=self.score, created__gt=self.created)
            | Q(score=self.score, created=self.created, pk__gt=self.pk)
        ).count()
        return f"{self.question.get_absolute_url()}?page={preceding // 30 + 1}#answer-{self.pk}"


class QuestionLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="likes", verbose_name="Вопрос")
    value = models.SmallIntegerField("Оценка", choices=[(1, "Лайк"), (-1, "Дизлайк")])

    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        constraints = [
            models.UniqueConstraint(fields=["user", "question"], name="unique_question_vote"),
            models.CheckConstraint(condition=Q(value__in=[-1, 1]), name="question_vote_value"),
        ]


class AnswerLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="likes", verbose_name="Ответ")
    value = models.SmallIntegerField("Оценка", choices=[(1, "Лайк"), (-1, "Дизлайк")])

    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        constraints = [
            models.UniqueConstraint(fields=["user", "answer"], name="unique_answer_vote"),
            models.CheckConstraint(condition=Q(value__in=[-1, 1]), name="answer_vote_value"),
        ]
