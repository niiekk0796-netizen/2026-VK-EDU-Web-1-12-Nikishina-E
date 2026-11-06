from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from .data import QUESTIONS, answers_for
from .pagination import paginate


def question_feed(request, template, *, tag=None, by_rating=False):
    query = request.GET.get("q", "").strip()[:100]
    search = query.casefold()
    results = [
        question
        for question in QUESTIONS.values()
        if (tag is None or tag in question["tags"])
        and (not search or search in question["title"].casefold() or search in question["text"].casefold())
    ]
    if by_rating:
        results.sort(key=lambda question: (question["score"], question["created"]), reverse=True)
    else:
        results.sort(key=lambda question: question["created"], reverse=True)

    return render(
        request,
        template,
        {"page": paginate(results, request, per_page=20), "tag": tag, "search_query": query},
    )


@require_safe
def index(request):
    return question_feed(request, "questions/index.html")


@require_safe
def hot(request):
    return question_feed(request, "questions/hot.html", by_rating=True)


@require_safe
def tag(request, tag):
    return question_feed(request, "questions/tag.html", tag=tag, by_rating=True)


@require_safe
def question(request, question_id):
    post = QUESTIONS.get(question_id)
    if post is None:
        raise Http404("Question not found.")

    return render(
        request,
        "questions/question.html",
        {"question": post, "page": paginate(answers_for(post), request, per_page=30)},
    )


@require_safe
def ask(request):
    return render(request, "questions/ask.html")
