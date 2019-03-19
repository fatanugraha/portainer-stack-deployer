from django.db import models


class Stack(models.Model):
    name = models.SlugField(max_length=256)
    environment_variable = models.TextField()
    stack_file = models.TextField()

    @property
    def stack_id(self):
        obj = self.metas.filter(name="stack_id").first()
        if obj:
            return obj.value

    @property
    def resource_control_id(self):
        obj = self.metas.filter(name="resource_control_id").first()
        if obj:
            return obj.value

    def set_meta(self, name, value):
        return self.metas.create(name=name, value=value, environment=self)

    def unset_meta(self, name):
        self.metas.filter(name=name, environment=self).delete()

    def __str__(self):
        return self.name

    def serialize(self):
        env_lines = self.environment_variable.split("\n")
        envs = []

        for line in filter(lambda i: i.strip() != "", env_lines):
            name, value = line.rstrip("\r").split("=")
            envs.append({"name": name, "value": value})

        return {"Name": self.name, "StackFileContent": self.stack_file, "Env": envs}


class Meta(models.Model):
    environment = models.ForeignKey(
        Stack, related_name="metas", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    value = models.TextField()

    def __str__(self):
        return self.name
