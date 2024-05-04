import json
import os
from http import HTTPStatus

import requests
from authlib.integrations.django_oauth2 import ResourceProtector
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from . import validator

load_dotenv()

require_auth = ResourceProtector()
validator = validator.Auth0JWTBearerTokenValidator(
    os.environ['DOMAIN'],
    os.environ['AUDIENCE']
)
require_auth.register_token_validator(validator)


def public(request):
    """No access token required to access this route
    """
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return JsonResponse(dict(message=response))


@require_auth(None)
def private(request):
    """A valid access token is required to access this route
    """
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return JsonResponse(dict(message=response))


def get_auth0_management_api_access_token() -> str | None:
    """Auth0 Management APIのアクセストークンを取得します。

    :return: Auth0 Management APIのアクセストークン
    :rtype: str | None
    """
    domain = os.environ['DOMAIN']

    payload = {
        'grant_type': 'client_credentials',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'audience': f'https://{domain}/api/v2/'
    }

    response = requests.post(f'https://{domain}/oauth/token', data=payload)

    if response.status_code != requests.codes.ok:
        return None

    data = response.json()
    return data['access_token']


@require_auth(None)
def get_user(request: HttpRequest) -> HttpResponse:
    """プロディールを取得します。

    :param request: リクエスト
    :type request: HttpRequest
    :return: 更新内容
    :rtype: HttpResponse
    """
    domain = os.environ['DOMAIN']
    user_id = request.oauth_token.sub
    url = f'https://{domain}/api/v2/users/{user_id}'

    payload = {}

    access_token = get_auth0_management_api_access_token()

    if access_token is None:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, data=payload, headers=headers)

    if response.status_code != requests.codes.ok:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    data = response.json()

    return JsonResponse({
        'name': data['name'],
        'email': data['email']
    })


@require_auth(None)
@csrf_exempt
def update_profile(request: HttpRequest) -> HttpResponse:
    """プロディールを更新します。

    :param request: リクエスト
    :type request: HttpRequest
    :return: 更新内容
    :rtype: HttpResponse
    """
    domain = os.environ['DOMAIN']
    user_id = request.oauth_token.sub
    url = f'https://{domain}/api/v2/users/{user_id}'

    payload = json.dumps({
        'name': request.POST['name'],
        'email': request.POST['email']
    })

    access_token = get_auth0_management_api_access_token()

    if access_token is None:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.patch(url, data=payload, headers=headers)

    if response.status_code != requests.codes.ok:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    data = response.json()

    return JsonResponse({
        'name': data['name'],
        'email': data['email']
    })


@require_auth("read:messages")
def private_scoped(request):
    """A valid access token and an appropriate scope are required to access this route
    """
    response = "Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this."
    return JsonResponse(dict(message=response))
