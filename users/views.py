import json
import os
from http import HTTPStatus

import requests
from authlib.integrations.django_oauth2 import ResourceProtector
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from users import validator
from users.models import User

load_dotenv()

require_auth = ResourceProtector()

validator = validator.Auth0JWTBearerTokenValidator(
    os.environ['DOMAIN'],
    os.environ['AUDIENCE']
)

require_auth.register_token_validator(validator)


def get_auth0_management_api_access_token() -> str | None:
    """Auth0 Management APIのアクセストークンを取得します。

    :return: Auth0 Management APIのアクセストークン
    :rtype: str | None
    """
    payload = {
        'grant_type': 'client_credentials',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'audience': f'https://{os.environ['DOMAIN']}/api/v2/'
    }

    response = requests.post(f'https://{os.environ['DOMAIN']}/oauth/token', data=payload)

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
    access_token = get_auth0_management_api_access_token()

    if access_token is None:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    user_id = request.oauth_token.sub
    user = get_object_or_404(User, auth0_user_id=user_id)

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(f'https://{os.environ['DOMAIN']}/api/v2/users/{user_id}', data={}, headers=headers)

    if response.status_code != requests.codes.ok:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    data = response.json()

    return JsonResponse({
        'first_name': user.first_name,
        'last_name': user.last_name,
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
    user_id = request.oauth_token.sub

    user = get_object_or_404(User, auth0_user_id=user_id)
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.save()

    access_token = get_auth0_management_api_access_token()

    if access_token is None:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    payload = json.dumps({
        'name': f'{request.POST['last_name']} {request.POST['first_name']}',
        'email': request.POST['email']
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.patch(f'https://{os.environ['DOMAIN']}/api/v2/users/{user_id}', data=payload, headers=headers)

    if response.status_code != requests.codes.ok:
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    data = response.json()

    return JsonResponse({
        'name': data['name'],
        'email': data['email']
    })
