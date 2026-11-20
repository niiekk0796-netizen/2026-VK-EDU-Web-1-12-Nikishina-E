from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from .models import Question, Tag
from .pagination import paginate


def page_context(objects, request, per_page):
    page = paginate(objects, request, per_page)
    return {"page": page, "page_numbers": page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)}


def question_feed(request, template, tag=None, by_rating=False):
    query = request.GET.get("q", "").strip()[:100]
    posts = Question.objects.display(request.user).search(query)
    posts = posts.tagged(tag) if tag else posts.best() if by_rating else posts.newest()
    return render(request, template, {**page_context(posts, request, 20), "tag": tag, "search_query": query})


@require_safe
def index(request):
    return question_feed(request, "questions/index.html")


@require_safe
def hot(request):
    return question_feed(request, "questions/hot.html", by_rating=True)


@require_safe
def tag(request, tag):
    topic = get_object_or_404(Tag, name=tag)
    return question_feed(request, "questions/tag.html", tag=topic.name)


@require_safe
def question(request, question_id):
    post = get_object_or_404(Question.objects.display(request.user), pk=question_id)
    answers = post.answers.display(request.user).ranked()
    return render(request, "questions/question.html", {"question": post, **page_context(answers, request, 30)})


@require_safe
def ask(request):
    return render(request, "questions/ask.html")
