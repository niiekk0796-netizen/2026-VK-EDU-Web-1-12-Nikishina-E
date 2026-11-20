from urllib.parse import quote
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_safe, require_http_methods

from .forms import AnswerForm, QuestionForm
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


@require_http_methods(["GET", "POST"])
def question(request, question_id):
    post = get_object_or_404(Question.objects.display(request.user), pk=question_id)
    if request.method == "POST" and not request.user.is_authenticated:
        return redirect(f"{reverse('core:login')}?next={quote(request.path)}")
    form = AnswerForm(request.POST if request.method == "POST" else None, author=request.user, question=post)
    if request.method == "POST" and form.is_valid():
        return redirect(form.save().get_absolute_url())
    return render(request, "questions/question.html", {"question": post, "form": form, **page_context(post.answers.display(request.user).ranked(), request, 30)})


@login_required
@require_http_methods(["GET", "POST"])
def ask(request):
    form = QuestionForm(request.POST if request.method == "POST" else None, author=request.user)
    if request.method == "POST" and form.is_valid():
        post = form.save()
        messages.success(request, "Вопрос добавлен.")
        return redirect(post)
    return render(request, "questions/ask.html", {"form": form})