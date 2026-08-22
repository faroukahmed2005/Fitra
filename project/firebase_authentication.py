from functools import wraps

from firebase_admin import auth
from rest_framework.response import Response
from rest_framework import status


def firebase_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response(
                {"message": "Authorization header missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not auth_header.startswith("Bearer "):
            return Response(
                {"message": "Invalid authorization header."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header.split(" ")[1]

        try:
            decoded_token = auth.verify_id_token(
                token,
                clock_skew_seconds=60,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {
                    "message": "Invalid Firebase Token.",
                    "error": str(e),
                    "type": str(type(e)),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not decoded_token.get("admin", False):
            return Response(
                {"message": "Admin privileges required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        request.firebase_user = decoded_token
        return view_func(request, *args, **kwargs)

    return wrapper