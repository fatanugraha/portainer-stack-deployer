import factory


class StackFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("first_name")
    environment_variable = "key=value"
    stack_file = 'version: "2"\n\nservices:\npostgres:\nimage: postgres:latest\n'

    class Meta:
        model = "app.Stack"
