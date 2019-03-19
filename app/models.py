from django.db import models


class Stack(models.Model):
    name = models.SlugField(max_length=256)
    environment_variable = models.TextField()
    stack_file = models.TextField()

    @property
    def stack_id(self):
        return self.metas.filter("portainer_stack_id").first()

    def __str__(self):
        return self.name

class Meta(models.Model):
    environment = models.ForeignKey(
        Stack, related_name="metas", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    value = models.TextField()

    def __str__(self):
        return self.name
