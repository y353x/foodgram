from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import Truncator

from api.constants import (MAIL_LENGTH, MAX_ADMIN_NAME_LENGTH,
                           USERNAME_LENGTH)
from api.validators import validate_username


class User(AbstractUser):

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLE_CHOICES = (
        (USER, "пользователь"),
        (MODERATOR, "модератор"),
        (ADMIN, "администратор"),
    )
    username = models.CharField(
        max_length=USERNAME_LENGTH,
        verbose_name="Имя пользователя",
        unique=True,
        db_index=True,
        validators=(validate_username,),
    )
    email = models.EmailField(
        verbose_name="email", max_length=MAIL_LENGTH, unique=True
    )
    role = models.CharField(
        verbose_name="роль",
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )
    first_name = models.CharField(
        verbose_name="имя", max_length=USERNAME_LENGTH, blank=True
    )
    last_name = models.CharField(
        verbose_name="фамилия", max_length=USERNAME_LENGTH, blank=True
    )
    bio = models.TextField(verbose_name="биография", blank=True)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ("id",)

    def __str__(self):
        return Truncator(self.username).chars(MAX_ADMIN_NAME_LENGTH)

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
