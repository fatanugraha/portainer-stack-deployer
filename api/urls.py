from django.urls import path, include

from api import views

app_name = "api"

urlpatterns = [
    path("deploy-stack/<str:name>/", views.DeployStackAPIView.as_view(), name="deploy")
]
