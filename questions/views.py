from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from .data import QUESTIONS, answers_for
from .pagination import paginate


def page_context(objects, request, per_page):
    page = paginate(objects, request, per_page)
    return {
        "page": page,
        "page_numbers": page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1),
    }


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

    context = page_context(results, request, per_page=20)
    context.update(tag=tag, search_query=query, demo_member="Dr. Pepper")
    return render(request, template, context)


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

    context = page_context(answers_for(post), request, per_page=2)
    return render(request, "questions/question.html", {"question": post, **context})


@require_safe
def ask(request):
    return render(request, "questions/ask.html")
