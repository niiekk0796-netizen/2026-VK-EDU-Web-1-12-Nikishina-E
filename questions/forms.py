from django import forms
from django.db import transaction
from django.utils.text import slugify

from core.forms import StyledForm
from .models import Answer, Question, Tag
from .services import change_vote, choose_answer, notify_author


class QuestionForm(StyledForm, forms.ModelForm):
    tags = forms.CharField(label="Tags", required=False, max_length=122, help_text="До трёх тегов через запятую, каждый до 40 символов.")

    class Meta:
        model = Question
        fields = ["title", "text", "tags"]
        labels = {"title": "Title", "text": "Text"}
        help_texts = {"title": "До 120 символов.", "text": "До 5000 символов."}
        widgets = {"text": forms.Textarea(attrs={"rows": 7})}

    def __init__(self, *args, author, **kwargs):
        self.author = author
        super().__init__(*args, **kwargs)

    def clean_tags(self):
        tags = []
        for value in self.cleaned_data["tags"].split(","):
            value = value.strip()
            if not value:
                continue
            tag = slugify(value, allow_unicode=True)
            if not tag or len(tag) > 40:
                raise forms.ValidationError("Тег должен содержать от 1 до 40 букв, цифр или дефисов.")
            if tag not in tags:
                tags.append(tag)
        if len(tags) > 3:
            raise forms.ValidationError("Можно указать не больше трёх тегов.")
        return tags

    @transaction.atomic
    def save(self, commit=True):
        post = super().save(commit=False)
        post.author = self.author
        if commit:
            post.save()
            tags = [Tag.objects.get_or_create(name=name)[0] for name in self.cleaned_data["tags"]]
            post.tags.set(tags)
        return post


class AnswerForm(StyledForm, forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        labels = {"text": "Your answer"}
        help_texts = {"text": "До 5000 символов."}
        widgets = {"text": forms.Textarea(attrs={"rows": 3, "placeholder": "Enter your answer here.."})}

    def __init__(self, *args, author, question, **kwargs):
        self.author = author
        self.question = question
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = self.question
        if commit:
            answer.save()
            transaction.on_commit(lambda: notify_author(answer))
        return answer


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(choices=[(-1, "Down"), (1, "Up")], coerce=int)

    def save(self, user, post):
        return change_vote(user, post, self.cleaned_data["value"])


class AcceptedAnswerForm(forms.Form):
    answer = forms.ModelChoiceField(queryset=Answer.objects.none())

    def __init__(self, *args, question, **kwargs):
        self.question = question
        super().__init__(*args, **kwargs)
        self.fields["answer"].queryset = question.answers.all()

    def save(self, user):
        return choose_answer(user, self.question, self.cleaned_data["answer"])
