from django.conf import settings
import requests
import json
import base64


class PortainerAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.request = requests.Session()
        self.request.hooks = {"response": self.log_response}
        self.logs = []

    def log_response(self, r, *args, **kwargs):
        self.logs.append({"url": r.url, "result": r.text})

    def login(self, username, password):
        r = self.request.post(
            self.base_url + "/auth",
            data=json.dumps({"username": username, "password": password}),
        )

        if r.status_code == 200:
            self.jwt = r.json()["jwt"]
            self.user = json.loads(base64.b64decode(self.jwt.split(".")[1] + "=="))
            self.request.headers.update({"Authorization": "Bearer {}".format(self.jwt)})

        return r

    def delete_stack(self, stack_id):
        url = self.base_url + "/stacks/{}?endpointId=1&external=false".format(stack_id)
        return self.request.delete(url)

    def delete_resource_control(self, resource_control_id):
        url = self.base_url + "/resource_controls/{}".format(resource_control_id)
        return self.request.delete(url)

    def pull_image(self, image, tag):
        url = (
            self.base_url
            + "/endpoints/1/docker/images/create?fromImage={}&tag={}".format(image, tag)
        )
        return self.request.post(url, data=json.dumps({"fromImage": image, "tag": tag}))

    def inspect_stack(self, stack_name):
        url = (
            self.base_url
            + '/endpoints/1/docker/containers/json?all=1&filters={{"label":["com.docker.compose.project={}"]}}'.format(
                stack_name
            )
        )
        return self.request.get(url)

    def create_stack(self, name, stack_file_content, env):
        url = self.base_url + "/stacks?endpointId=1&method=string&type=2"
        payload = {"Name": name, "StackFileContent": stack_file_content, "Env": env}
        return self.request.post(url, data=json.dumps(payload))

    def create_private_resource_control(self, resource_id):
        url = self.base_url + "/resource_controls"
        payload = {
            "Type": "stack",
            "Public": False,
            "ResourceID": resource_id,
            "Users": [self.user["id"]],
            "Teams": [],
            "SubResourceIDs": [],
        }
        return self.request.post(url, data=json.dumps(payload))


class StackController:
    def __init__(self, stack, portainer_api_base_url):
        self.api = PortainerAPI(portainer_api_base_url)
        self.stack = stack

    def login(self, username, password, num_retries=10):
        current_retries = 0
        success = False

        while current_retries < num_retries and not success:
            r = self.api.login(username, password)
            success = r.status_code == 200
            current_retries += 1

    def delete_stack(self):
        if self.stack.stack_id is None:
            return

        r = self.api.delete_stack(self.stack.stack_id)
        if r.status_code != 204:
            raise Exception(r.text)

        self.stack.stack_id = None
        self.stack.save()

    def delete_resource_control(self):
        if self.stack.resource_control_id is None:
            return

        r = self.api.delete_resource_control(self.stack.resource_control_id)
        if r.status_code != 204:
            raise Exception(r.text)

        self.stack.resource_control_id = None
        self.stack.save()

    def pull_stack_images(self):
        if self.stack.stack_id is None:
            return

        images = self.api.inspect_stack(self.stack.name).json()

        for image in images:
            image_name = image["Image"]
            if "sha256" in image_name:
                continue

            name, tag = image_name.split(":")
            self.api.pull_image(name, tag)

    def create_stack(self):
        if self.stack.stack_id:
            return

        env_lines = self.stack.environment_variable.split("\n")
        envs = []

        for line in filter(lambda i: i.strip() != "", env_lines):
            name, value = line.rstrip("\r").split("=")
            envs.append({"name": name, "value": value})

        r = self.api.create_stack(self.stack.name, self.stack.stack_file, envs)
        if r.status_code != 200:
            raise Exception(r.text)

        self.stack.stack_id = r.json()["Id"]
        self.stack.save()

    def create_resource_control(self):
        if self.stack.resource_control_id:
            return

        r = self.api.create_private_resource_control(self.stack.name)
        if r.status_code != 200:
            raise Exception(r.text)

        self.stack.resource_control_id = r.json()["Id"]
        self.stack.save()


def deploy_stack(stack):
    controller = StackController(stack, "https://portainer.docker.ppl.cs.ui.ac.id/api")
    try:
        controller.login(settings.PORTAINER_USERNAME, settings.PORTAINER_PASSWORD)
        controller.pull_stack_images()
        controller.delete_stack()
        controller.delete_resource_control()
        controller.create_stack()
        controller.create_resource_control()
    except Exception as e:
        return str(e), controller.api.logs

    return "", controller.api.logs
