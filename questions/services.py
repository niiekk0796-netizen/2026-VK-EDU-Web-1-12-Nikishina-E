import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F

from .models import AnswerLike, Question, QuestionLike


logger = logging.getLogger(__name__)


@transaction.atomic
def change_vote(user, post, value):
    post = type(post).objects.select_for_update().get(pk=post.pk)
    model, field = (QuestionLike, "question") if isinstance(post, Question) else (AnswerLike, "answer")
    lookup = {"user": user, field: post}
    previous = model.objects.filter(**lookup).first()
    old = previous.value if previous else 0
    current = 0 if old == value else value
    if current == 0:
        previous.delete()
    else:
        model.objects.update_or_create(**lookup, defaults={"value": current})
    type(post).objects.filter(pk=post.pk).update(score=F("score") + current - old)
    return {"score": post.score + current - old, "vote": current}


@transaction.atomic
def choose_answer(user, question, answer):
    question = Question.objects.select_for_update().get(pk=question.pk)
    if question.author_id != user.pk:
        raise PermissionError("Выбрать правильный ответ может только автор вопроса.")
    answer.refresh_from_db(fields=["accepted"])
    accepted = not answer.accepted
    question.answers.filter(accepted=True).update(accepted=False)
    if accepted:
        question.answers.filter(pk=answer.pk).update(accepted=True)
    return {"answer": answer.pk, "accepted": accepted}


def notify_author(answer):
    if not answer.question.author.email:
        return
    link = settings.SITE_URL.rstrip("/") + answer.get_absolute_url()
    try:
        send_mail(
            f"Новый ответ: {answer.question.title}",
            f"На ваш вопрос ответили.\n{link}",
            settings.DEFAULT_FROM_EMAIL,
            [answer.question.author.email],
        )
    except Exception:
        logger.exception("Не удалось отправить уведомление об ответе")
