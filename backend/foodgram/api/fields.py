import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers

IMAGE_FILE_NAME = '{user}_recipe_{unique_end}.{extention}'
VALIDATION_ERROR_BASE64 = 'Неверный формат изображения.'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        """Parse input string, decode, save image."""
        try:
            format, image_string = data.split(';base64,')
            data = ContentFile(
                base64.b64decode(image_string),
                name=IMAGE_FILE_NAME.format(
                    user=self.context['request'].user.username,
                    unique_end=uuid.uuid4().hex[:12],
                    extention=format.split('/')[-1]
                )
            )
        except ValueError:
            raise serializers.ValidationError(VALIDATION_ERROR_BASE64)
        return super().to_internal_value(data)
