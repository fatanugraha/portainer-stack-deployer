from django.db import models


class Stack(models.Model):
    name = models.SlugField(max_length=256)
    environment_variable = models.TextField()
    stack_file = models.TextField()
    stack_id = models.IntegerField(null=True, blank=True)
    resource_control_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
