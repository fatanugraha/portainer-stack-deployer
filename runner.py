from app.tasks import *

from app.models import Stack

deploy_stack(Stack.objects.first())
delete_stack(Stack.objects.first())
