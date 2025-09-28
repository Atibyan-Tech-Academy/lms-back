import urllib.parse
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser

jwt_auth = JWTAuthentication()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        scope["user"] = AnonymousUser()
        query_string = scope.get("query_string", b"").decode()
        params = urllib.parse.parse_qs(query_string)
        token = None
        if "token" in params and params["token"]:
            token = params["token"][0]
        else:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1].strip()
        if token:
            try:
                validated = UntypedToken(token)
                validated_user = jwt_auth.get_user(validated)
                scope["user"] = validated_user
            except Exception:
                scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return AuthMiddlewareStack(JWTAuthMiddleware(inner))
