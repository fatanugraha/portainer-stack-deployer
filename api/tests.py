from django.test import TestCase
from rest_framework.test import APITestCase

from app.factories import StackFactory
from api.serializers import DeployStackSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestDeploySerializer(APITestCase):
    def setUp(self):
        self.stack = StackFactory()

    def test_serialzier_doesnt_require_stackfile(self):
        prev_stack_file = self.stack.stack_file

        serializer = DeployStackSerializer(self.stack, data={})
        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertEqual(obj.stack_file, prev_stack_file)

    def test_serializer_updates_stackfile_if_given(self):
        prev_stack_file = self.stack.stack_file

        serializer = DeployStackSerializer(self.stack, data={"stack_file": "yo man"})
        self.assertTrue(serializer.is_valid())
        obj = serializer.save()

        self.assertEqual(obj.stack_file, "yo man")


class TestDeployView(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        user = UserModel.objects.create(
            first_name="fata",
            last_name="nugraha",
            email="fata@localhost",
            username="fata",
        )
        self.client.force_authenticate(user=user)
        self.stack = StackFactory()

    def test_requires_authentication(self):
        self.client.logout()
        r = self.client.post(reverse("api:deploy", kwargs={"name": self.stack.name}))
        self.assertEqual(r.status_code, 403)

    def test_returns_404_on_non_existent_stack_name(self):
        r = self.client.post(reverse("api:deploy", kwargs={"name": "hohoho"}))
        self.assertEqual(r.status_code, 404)
