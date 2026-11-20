from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .forms import AcceptedAnswerForm, VoteForm
from .models import Answer, Question


def api_access(request):
    if request.method != "POST":
        return JsonResponse({"error": "Используйте POST."}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Войдите, чтобы продолжить."}, status=401)


def vote(request, kind, post_id):
    error = api_access(request)
    if error is not None:
        return error
    model = {"question": Question, "answer": Answer}.get(kind)
    if model is None:
        return JsonResponse({"error": "Неизвестный тип записи."}, status=404)
    post = get_object_or_404(model, pk=post_id)
    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors.get_json_data()}, status=400)
    return JsonResponse(form.save(request.user, post))


def accept(request, question_id):
    error = api_access(request)
    if error is not None:
        return error
    post = get_object_or_404(Question, pk=question_id)
    form = AcceptedAnswerForm(request.POST, question=post)
    if not form.is_valid():
        return JsonResponse({"error": form.errors.get_json_data()}, status=400)
    try:
        return JsonResponse(form.save(request.user))
    except PermissionError as error:
        return JsonResponse({"error": str(error)}, status=403)
