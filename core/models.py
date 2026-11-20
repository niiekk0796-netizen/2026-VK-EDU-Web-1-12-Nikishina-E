from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.templatetags.static import static


def avatar_path(instance, filename):
    return f"avatars/{uuid4().hex}{Path(filename).suffix.lower()}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователь")
    nickname = models.CharField("Никнейм", max_length=40)
    avatar = models.ImageField("Аватар", upload_to=avatar_path, blank=True)
    rating = models.IntegerField("Рейтинг", default=0)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.nickname or self.user.username

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else static("core/img/profile.svg")
