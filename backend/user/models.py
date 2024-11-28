from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import Truncator

from api.constants import MAIL_LENGTH, MAX_ADMIN_NAME_LENGTH, USERNAME_LENGTH


class User(AbstractUser):
    """Кастом модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'пользователь'),
        (ADMIN, 'администратор'),
    )
    username = models.CharField(
        max_length=USERNAME_LENGTH,
        verbose_name='имя пользователя',
        unique=True,
        db_index=True,
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=MAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=USERNAME_LENGTH
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=USERNAME_LENGTH
    )
    avatar = models.ImageField(
        verbose_name='аватар',
        upload_to='avatars/',
        help_text='загрузите аватар',
        blank=True
    )
    role = models.CharField(
        verbose_name='роль',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('id',)

    def __str__(self):
        return Truncator(self.username).chars(MAX_ADMIN_NAME_LENGTH)

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author')

    class Meta:
        ordering = ('author_id',)
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
