from pathlib import Path

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Profile


class StyledForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class AvatarForm(StyledForm):
    avatar = forms.ImageField(label="Upload avatar", required=False, help_text="PNG, JPEG или WebP, до 2 МБ.")

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Размер изображения должен быть не больше 2 МБ.")
            if Path(avatar.name).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"} or avatar.image.format not in {"PNG", "JPEG", "WEBP"}:
                raise forms.ValidationError("Выберите изображение PNG, JPEG или WebP.")
        return avatar


class LoginForm(StyledForm, AuthenticationForm):
    username = forms.CharField(label="Login", max_length=150, help_text="Логин, указанный при регистрации.")
    password = forms.CharField(label="Password", widget=forms.PasswordInput, help_text="Введите пароль.")


class SignupForm(AvatarForm, UserCreationForm):
    email = forms.EmailField(label="Email", help_text="Укажите действующий адрес почты.")
    first_name = forms.CharField(label="NickName", max_length=40, help_text="Имя, которое увидят другие пользователи.")
    avatar = AvatarForm.avatar

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password1", "password2", "avatar"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
            profile = user.profile
            profile.nickname = user.first_name
            profile.avatar = self.cleaned_data.get("avatar") or ""
            profile.save()
        return user


class ProfileForm(AvatarForm, forms.ModelForm):
    email = forms.EmailField(label="Email", help_text="Адрес для уведомлений об ответах.")
    avatar = AvatarForm.avatar

    class Meta:
        model = Profile
        fields = ["email", "nickname", "avatar"]
        labels = {"nickname": "NickName"}
        help_texts = {"nickname": "До 40 символов."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.user_id).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.email = self.cleaned_data["email"]
            profile.user.first_name = profile.nickname
            profile.user.save(update_fields=["email", "first_name"])
            profile.save()
        return profile
