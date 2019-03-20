from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import DeployStackSerializer
from app.models import Stack
from app.tasks import deploy_stack


class DeployStackAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(Stack, name=self.kwargs["name"])

    def post(self, request, name):
        obj = self.get_object()
        serializer = DeployStackSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message, result = deploy_stack(obj)
        return Response(
            {"message": message, "logs": result}, status=200 if message == "" else 500
        )
