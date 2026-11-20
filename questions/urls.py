from django.urls import path

from . import api, views


app_name = "questions"
urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("ask/", views.ask, name="ask"),
    path("api/vote/<str:kind>/<int:post_id>/", api.vote, name="vote"),
    path("api/accept/<int:question_id>/", api.accept, name="accept"),
]
