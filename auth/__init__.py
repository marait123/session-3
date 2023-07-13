from copyreg import constructor
from flask import Flask, request, abort
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os
SECRET_KEY = os.getenv("MY_SECRET")
# AUTH0_DOMAIN = "herfy.us.auth0.com"
# ALGORITHMS = ['RS256']
# API_AUDIENCE = "flask_recap_api"
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
ALGORITHMS = ['RS256']
API_AUDIENCE = os.getenv("API_AUDIENCE")


def test_import():
    print("hello all ")
    print(AUTH0_DOMAIN)
    print(ALGORITHMS)
    print(API_AUDIENCE)


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def check_permissions(permissions, payload):
    if 'permissions' not in payload:
        return False
    for permission in permissions:
        if permission not in payload['permissions']:
            return False
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. check the audience.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permissions):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            try:
                token = get_token_auth_header()
            except AuthError:
                abort(401)
            try:
                print('token ', token)

                payload = verify_decode_jwt(token)
                print('payload ', payload)

                is_authorized = check_permissions(permissions, payload)
                if not is_authorized:
                    print("you're not authorized")
                    raise AuthError("you are n't authorized", 403)
            except AuthError:
                abort(403)
            except:
                abort(401)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
