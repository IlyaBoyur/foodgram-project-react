from rest_framework import serializers


class UniqueManyFieldsValidator:
    message = 'Many field fields shall all be unique.'

    def __init__(self, many_field, unique_subfield=None, message=None):
        self.many_field = many_field
        self.unique_subfield = unique_subfield
        self.message = message or self.message

    def __call__(self, attrs):
        unique_in_many_field = set(
            attr[self.unique_subfield] for attr in attrs[self.many_field]
        ) if self.unique_subfield else set(attrs[self.many_field])
        if len(attrs[self.many_field]) != len(unique_in_many_field):
            raise serializers.ValidationError({self.many_field: self.message})
