from itertools import islice
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


def insert_batches(model, rows, batch_size=2000):
    iterator = iter(rows)
    while batch := list(islice(iterator, batch_size)):
        model.objects.bulk_create(batch, batch_size=batch_size)
        yield from batch


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options["ratio"]
        if ratio < 2:
            raise CommandError("ratio должен быть не меньше 2: для одного пользователя недостаточно уникальных пар для 200 оценок.")
        fake = Faker("en_US")
        prefix = uuid4().hex[:12]
        users = list(insert_batches(User, (
            User(username=f"{prefix}_{i}", email=f"{prefix}_{i}@example.com", first_name=fake.first_name(), password="!")
            for i in range(ratio)
        )))
        list(insert_batches(Profile, (Profile(user=user, nickname=fake.name()[:40]) for user in users)))
        tags = list(insert_batches(Tag, (Tag(name=f"{fake.word()}-{prefix}-{i}") for i in range(ratio))))
        titles = [fake.sentence(nb_words=8)[:120] for _ in range(1000)]
        texts = [fake.paragraph(nb_sentences=4) for _ in range(1000)]
        question_votes = min(ratio * 100, ratio * ratio * 10)
        answer_votes = ratio * 200 - question_votes
        questions = list(insert_batches(Question, (
            Question(author=users[i % ratio], title=titles[i % 1000], text=texts[i % 1000], score=question_votes // (ratio * 10) + (i < question_votes % (ratio * 10)))
            for i in range(ratio * 10)
        )))
        list(insert_batches(Question.tags.through, (
            Question.tags.through(question_id=question.pk, tag_id=tags[i % ratio].pk)
            for i, question in enumerate(questions)
        )))
        answer_ids = []
        for answer in insert_batches(Answer, (
            Answer(author=users[(i + 1) % ratio], question=questions[i % len(questions)], text=texts[i % 1000], score=answer_votes // (ratio * 100) + (i < answer_votes % (ratio * 100)))
            for i in range(ratio * 100)
        )):
            answer_ids.append(answer.pk)
        for _ in insert_batches(QuestionLike, (
            QuestionLike(user_id=users[i // len(questions)].pk, question_id=questions[i % len(questions)].pk, value=1)
            for i in range(question_votes)
        )):
            pass
        for _ in insert_batches(AnswerLike, (
            AnswerLike(user_id=users[i // len(answer_ids)].pk, answer_id=answer_ids[i % len(answer_ids)], value=1)
            for i in range(ratio * 200 - question_votes)
        )):
            pass
        self.stdout.write(self.style.SUCCESS(
            f"Добавлено: {ratio} пользователей, {ratio * 10} вопросов, {ratio * 100} ответов, {ratio} тегов, {ratio * 200} оценок."
        ))
