from random import choice
from string import ascii_letters, digits

from api.constants import S_LINK_LENGTH
from rest_framework import serializers
from shortlink.models import ShortLink


def random_string(length):
    """Генерация коротких ссылок."""
    pool = ascii_letters + digits  # Набор допустимых символов.
    while True:
        result_link = ''.join(choice(pool) for _ in range(length))
        if not ShortLink.objects.filter(short=result_link).exists():
            break
    return result_link


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериалайзер для коротких ссылок."""

    class Meta:
        model = ShortLink
        fields = ('short', 'full')
        read_only_fields = ('short',)
        extra_kwargs = {'full': {'write_only': True}}

    def create(self, validated_data):
        short_path = random_string(S_LINK_LENGTH)
        pre_url = self.context['request'].scheme + \
            '://' + self.context['request'].META['HTTP_HOST']
        validated_data['short'] = f'{pre_url}/s/{short_path}/'
        return super().create(validated_data)
