from django.db import models
from django.utils.text import Truncator

from api.constants import MAX_ADMIN_NAME_LENGTH, USERNAME_LENGTH


class ShortLink(models.Model):
    """Модель коротких ссылок."""

    full = models.CharField(verbose_name='Полная ссылка',
                            unique=True,
                            max_length=USERNAME_LENGTH,
                            help_text='Полная ссылка')
    short = models.CharField(verbose_name='Короткая ссылка',
                             unique=True,
                             max_length=USERNAME_LENGTH,
                             help_text='Короткая ссылка')

    class Meta:
        ordering = ('id',)
        default_related_name = 'link'
        verbose_name = 'ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return Truncator(self.full).chars(MAX_ADMIN_NAME_LENGTH)
