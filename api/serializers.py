from rest_framework import serializers

from app.models import Stack


class DeployStackSerializer(serializers.ModelSerializer):
    stack_file = serializers.CharField(
        allow_blank=True, required=False, trim_whitespace=True
    )

    def update(self, obj, validated_data):
        obj.stack_file = validated_data.get("stack_file", obj.stack_file)
        obj.save()
        return obj

    class Meta:
        model = Stack
        fields = ("stack_file",)
