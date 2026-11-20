from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import close_old_connections
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.db import connection

from core.forms import SignupForm
from .forms import AnswerForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag
from .services import change_vote


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user("owner", "owner@example.com", "A-test-password-47")
        cls.other = User.objects.create_user("other", "other@example.com", "Another-password-48")
        cls.question = Question.objects.create(author=cls.owner, title="A question", text="Details")
        cls.answer = Answer.objects.create(question=cls.question, author=cls.other, text="An answer")

    def test_empty_pages_and_missing_objects(self):
        Question.objects.all().delete()
        self.assertContains(self.client.get("/"), "Пока нет ни одного вопроса")
        self.assertEqual(self.client.get("/question/999/").status_code, 404)
        self.assertEqual(self.client.get("/tag/missing/").status_code, 404)

    def test_auth_redirect_and_logout(self):
        self.assertEqual(self.client.get("/profile/").status_code, 302)
        self.client.post("/login/?next=https://evil.example", {"username": "owner", "password": "A-test-password-47", "next": "https://evil.example"})
        self.assertEqual(self.client.get("/profile/").status_code, 200)
        response = self.client.post("/logout/", {"next": "/hot/?page=2"})
        self.assertRedirects(response, "/hot/?page=2")
        self.assertNotContains(self.client.get("/"), "settings</a>")

    def test_signup_validation_and_profile(self):
        data = {"username": "new-user", "email": "new@example.com", "first_name": "New", "password1": "Long-sample-password-84", "password2": "Long-sample-password-84"}
        response = self.client.post("/signup/", data)
        self.assertRedirects(response, "/")
        account = User.objects.get(username="new-user")
        self.assertEqual(account.profile.nickname, "New")
        response = self.client.post("/profile/", {"email": "changed@example.com", "nickname": "Changed"})
        self.assertRedirects(response, "/profile/")
        account.refresh_from_db()
        self.assertEqual(account.email, "changed@example.com")
        data.update(username="weak-user", password1="123", password2="123")
        self.assertFalse(SignupForm(data).is_valid())

    def test_question_answer_validation(self):
        self.client.force_login(self.owner)
        invalid = self.client.post("/ask/", {"title": "Title", "text": "Text", "tags": "a,b,c,d"})
        self.assertContains(invalid, "не больше трёх тегов")
        self.assertContains(invalid, 'value="Title"')
        response = self.client.post("/ask/", {"title": "Title", "text": "Text", "tags": "django, python"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.get(title="Title").tags.count(), 2)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.question.get_absolute_url(), {"text": "Fresh answer"})
        answer = Answer.objects.get(text="Fresh answer")
        self.assertEqual(response.url, answer.get_absolute_url())
        self.assertEqual(len(mail.outbox), 1)

    def test_votes_and_acceptance(self):
        self.assertEqual(self.client.post(f"/api/vote/question/{self.question.pk}/", {"value": 1}).status_code, 401)
        self.client.force_login(self.other)
        url = f"/api/vote/question/{self.question.pk}/"
        for value, expected in [(1, 1), (1, 0), (-1, -1), (1, 1)]:
            self.assertEqual(self.client.post(url, {"value": value}).json()["score"], expected)
        self.assertEqual(QuestionLike.objects.count(), 1)
        self.assertEqual(self.client.post(url, {"value": 4}).status_code, 400)
        self.assertEqual(self.client.get(url).status_code, 405)
        accept = f"/api/accept/{self.question.pk}/"
        self.assertEqual(self.client.post(accept, {"answer": self.answer.pk}).status_code, 403)
        self.client.force_login(self.owner)
        self.assertTrue(self.client.post(accept, {"answer": self.answer.pk}).json()["accepted"])
        second = Answer.objects.create(question=self.question, author=self.other, text="Second")
        self.client.post(accept, {"answer": second.pk})
        self.assertEqual(self.question.answers.filter(accepted=True).count(), 1)
        self.assertFalse(self.client.post(accept, {"answer": second.pk}).json()["accepted"])

    def test_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post("/ask/", {"title": "Title", "text": "Body"}).status_code, 403)

    def test_avatar_validation(self):
        data = {"username": "image-user", "email": "image@example.com", "first_name": "Name", "password1": "Long-sample-password-84", "password2": "Long-sample-password-84"}
        invalid = SimpleUploadedFile("photo.jpg", b"fake image", content_type="image/jpeg")
        self.assertFalse(SignupForm(data, {"avatar": invalid}).is_valid())
        image = BytesIO()
        Image.new("RGB", (20, 20)).save(image, "PNG")
        valid = SignupForm(data, {"avatar": SimpleUploadedFile("avatar.png", image.getvalue())})
        self.assertTrue(valid.is_valid(), valid.errors)

    def test_query_count_and_pagination(self):
        Question.objects.bulk_create([Question(author=self.owner, title=f"Question {i}", text="Body") for i in range(45)])
        self.client.force_login(self.owner)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/")
        self.assertLess(len(queries), 12)
        self.assertEqual(len(response.context["page"]), 20)
        self.assertEqual(self.client.get("/?page=oops").context["page"].number, 1)


class ConcurrentVoteTests(TransactionTestCase):
    def test_parallel_votes_keep_score(self):
        users = [User.objects.create_user(f"parallel-{i}") for i in range(4)]
        post = Question.objects.create(author=users[0], title="Concurrent", text="Body")

        def vote(user_id):
            close_old_connections()
            try:
                return change_vote(User.objects.get(pk=user_id), Question.objects.get(pk=post.pk), 1)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(vote, [user.pk for user in users]))
        post.refresh_from_db()
        self.assertEqual(post.score, 4)
        self.assertEqual(post.likes.count(), 4)

