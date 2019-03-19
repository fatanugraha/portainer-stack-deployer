from django.conf import settings
import requests
import json
import base64


def login():
    username = settings.PORTAINER_USERNAME
    password = settings.PORTAINER_PASSWORD

    r = requests.post(
        settings.PORTAINER_URL + "/auth",
        data=json.dumps({"username": username, "password": password}),
    )

    if r.status_code == 200:
        jwt = r.json()["jwt"]
        user = jwt.split(".")[1] + "===="  # add base64 padding
        return jwt, json.loads(base64.b64decode(user))

    raise Exception(r.text)


auth_token, user = login()


def delete_stack(stack):

    if stack.stack_id:
        r = requests.delete(
            settings.PORTAINER_URL
            + "/stacks/{}?endpointId=1&external=false".format(stack.stack_id),
            headers={"Authorization": "Bearer %s" % auth_token},
        )

        if r.status_code != 204:
            raise Exception(r.text)
        print(r.text)

        stack.unset_meta("stack_id")

    if stack.resource_control_id:
        r = requests.delete(
            settings.PORTAINER_URL
            + "/resource_controls/{}".format(stack.resource_control_id),
            headers={"Authorization": "Bearer %s" % auth_token},
        )

        if r.status_code != 204:
            raise Exception(r.text)

        stack.unset_meta("resource_control_id")


def pull_image(image):
    name, tag = image.split(":")

    r = requests.post(
        settings.PORTAINER_URL
        + ("/endpoints/1/docker/images/create?fromImage=%s&tag=%s" % (name, tag)),
        headers={"Authorization": "Bearer %s" % auth_token},
        data=json.dumps({"fromImage": name, "tag": tag}),
    )

    if r.status_code != 200:
        raise Exception(r.text)

    print(r.text)


def renew_stack(stack):
    r = requests.get(
        settings.PORTAINER_URL
        + '/endpoints/1/docker/containers/json?all=1&filters={"label":["com.docker.compose.project=%s"]}'
        % stack.name,
        headers={"Authorization": "Bearer %s" % auth_token},
    )

    if r.status_code != 200:
        raise Exception(r.text)

    images = [container["Image"] for container in r.json()]
    print(images)
    for image in images:
        if "sha256" in image:  # already pulled
            continue
        pull_image(image)

    delete_stack(stack)
    deploy_stack(stack)


def deploy_stack(stack):
    # create stack
    if stack.stack_id is None:
        r = requests.post(
            settings.PORTAINER_URL + "/stacks?endpointId=1&method=string&type=2",
            headers={"Authorization": "Bearer %s" % auth_token},
            data=json.dumps(stack.serialize()),
        )

        if r.status_code != 200:
            raise Exception(r.text)

        stack.set_meta("stack_id", r.json()["Id"])

    # set stack permission to private
    if stack.resource_control_id is None:
        r = requests.post(
            settings.PORTAINER_URL + "/resource_controls",
            headers={"Authorization": "Bearer %s" % auth_token},
            data=json.dumps(
                {
                    "Type": "stack",
                    "Public": False,
                    "ResourceID": stack.name,
                    "Users": [user["id"]],
                    "Teams": [],
                    "SubResourceIDs": [],
                }
            ),
        )

        if r.status_code != 200:
            raise Exception(r.text)

        stack.set_meta("resource_control_id", r.json()["Id"])
