import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from djoser.social.views import ProviderAuthView

logger = logging.getLogger(__name__)


#Working one
# class CustomTokenObtainPairView(TokenObtainPairView):

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)

#         if response.status_code == 200:
#             access_token = response.data.get("access")
#             refresh_token = response.data.get("refresh")

#             response.set_cookie(
#                 "access",
#                 access_token,
#                 max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
#                 path=settings.AUTH_COOKIE_PATH,
#                 secure=settings.AUTH_COOKIE_SECURE,
#                 httponly=settings.AUTH_COOKIE_HTTPONLY,
#                 samesite=settings.AUTH_COOKIE_SAMESITE,
#             )

#             response.set_cookie(
#                 "refresh",
#                 refresh_token,
#                 max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
#                 path=settings.AUTH_COOKIE_PATH,
#                 secure=settings.AUTH_COOKIE_SECURE,
#                 httponly=settings.AUTH_COOKIE_HTTPONLY,
#                 samesite=settings.AUTH_COOKIE_SAMESITE,
#             )

#             response.data.pop("refresh", None)

#         return response
    

# # working one
# class CustomTokenRefreshView(TokenRefreshView):

#     def post(self, request, *args, **kwargs):
#         refresh_token = request.COOKIES.get("refresh")

#         if refresh_token:
#             request.data["refresh"] = refresh_token
        
#         response = super().post(request, *args, **kwargs)

#         if response.status_code == 200:
#             access_token = response.data.get("access")
#             response.set_cookie(
#                 "access",
#                 access_token,
#                 max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
#                 path=settings.AUTH_COOKIE_PATH,
#                 secure=settings.AUTH_COOKIE_SECURE,
#                 httponly=settings.AUTH_COOKIE_HTTPONLY,
#                 samesite=settings.AUTH_COOKIE_SAMESITE,
#             )
        
#         return response
    

# class CustomProviderAuthView(ProviderAuthView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)

#         if response.status_code == 201:
#             access_token = response.data.get("access")
#             refresh_token = response.data.get("refresh")

#             response.set_cookie(
#                 "access",
#                 access_token,
#                 max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
#                 path=settings.AUTH_COOKIE_PATH,
#                 secure=settings.AUTH_COOKIE_SECURE,
#                 httponly=settings.AUTH_COOKIE_HTTPONLY,
#                 samesite=settings.AUTH_COOKIE_SAMESITE,
#             )

#             response.set_cookie(
#                 "refresh",
#                 refresh_token,
#                 max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
#                 path=settings.AUTH_COOKIE_PATH,
#                 secure=settings.AUTH_COOKIE_SECURE,
#                 httponly=settings.AUTH_COOKIE_HTTPONLY,
#                 samesite=settings.AUTH_COOKIE_SAMESITE,
#             )

#             response.data.pop("refresh", None)

#         return response


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        response.delete_cookie("logged_in")
        return response

class CustomTokenVerifyView(TokenVerifyView):

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access")

        if access_token:
            request.data["token"] = access_token

        return super().post(request, *args, **kwargs)    

# Other Options

def set_auth_cookies(response:Response, access_token: str, refresh_token) -> None:

    cookie_settings = {
        "max_age":settings.AUTH_COOKIE_ACCESS_MAX_AGE,
        "path":settings.AUTH_COOKIE_PATH,
        "secure":settings.AUTH_COOKIE_SECURE,
        "httponly":settings.AUTH_COOKIE_HTTPONLY,
        "samesite":settings.AUTH_COOKIE_SAMESITE,
    }
    response.set_cookie("access", access_token, **cookie_settings)
    if refresh_token:
        refresh_token_lifetine = settings.AUTH_COOKIE_REFRESH_MAX_AGE
        refresh_cookie_settings = cookie_settings.copy()
        refresh_cookie_settings["max_age"] = refresh_token_lifetine
        response.set_cookie("refresh", refresh_token, **refresh_cookie_settings)
    
    logged_in_cookie_settings = cookie_settings.copy()
    logged_in_cookie_settings["httponly"] = False
    response.set_cookie("logged_in", "true", **logged_in_cookie_settings)




class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            if access_token and refresh_token:
                set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)
                response.data.pop("access",None)
                response.data.pop("refresh",None)
            else:
                response.data["message"] = "Login Failed"
                logger.error("Access or refresh token not found in login response data.")
        return response



class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh")

        if refresh_token:
            request.data["refresh"] = refresh_token
        
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            if access_token and refresh_token:
                set_auth_cookies(
                    response, 
                    access_token=access_token, 
                    refresh_token=refresh_token
                )
                response.data.pop("access", None)
                response.data.pop("refresh", None)
                response.data["message"] = "Access tokens refreshed successfully."
            else:
                response.data["message"] = "Access or refresh tokens not found in refresh response data."
                logger.error(
                    "Access of refresh token not found in resfresh response data.")
        
        return response
    

class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            if access_token and refresh_token:
                set_auth_cookies(
                    response, access_token=access_token, refresh_token=refresh_token)
                response.data.pop("access", None)
                response.data.pop("refresh", None)
                response.data["message"] = "You are logged in Successful."
            else:
                response.data["message"] = "Access or refresh not found in provider response."
                logger.error(
                    "Access or refresh token not found in provider response data.") 
        return response
    