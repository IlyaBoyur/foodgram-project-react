from rest_framework import serializers


class UniqueManyFieldsValidator:
    """Check all values are unique between each other in a list field."""
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


class MinValueForFieldValidator:
    """
    Check value_field is greater than min_value,
    construct thorough message on validation error
    """
    message = 'Minimum for {name} is {value}.'

    def __init__(self, min_value, value_field, name_field, message=None):
        self.field = value_field
        self.name_field = name_field
        self.min_value = min_value
        self.message = message or self.message

    def __call__(self, attrs):
        if attrs[self.field] < self.min_value:
            raise serializers.ValidationError(
                {
                    self.field: self.message.format(
                        name=str(attrs[self.name_field]),
                        value=self.min_value)
                }
            )
