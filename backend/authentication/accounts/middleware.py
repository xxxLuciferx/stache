import requests
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
import jwt
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework.renderers import JSONRenderer




JWT_SECRET_KEY = "yichiba94@"

from functools import wraps
from rest_framework.response import Response


def requires_authentication(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if args:
            request = args[0]
        if request.is_authenticated :
            return view_func(request, *args, **kwargs)
        else:
            response = Response({'error': 'Authentication required'}, status=401)
            response.accepted_renderer = JSONRenderer()
            response.renderer_context = {'request': request}
            response.accepted_media_type = 'application/json'
            return response
    return wrapper



def not_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if args:
            request = args[0]
        if request.is_authenticated :
            print("you are already logged in !!!'")
            messages.info(request,'you are already logged in !!!')
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


def JWTCheck(token):
    try:
        print("Checking JWT...")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256']) 
        return payload
    
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None

    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None




class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        from .models import CustomUser
        print("Processing request in middleware...")
        if 'JWT_token' in request.COOKIES:
            print("JWT_token found in request...")
            token = request.COOKIES['JWT_token']
            payload = JWTCheck(token)
            if payload:
                request.user_data = payload
                try:
                    request.user = CustomUser.objects.get(username= payload['username'])
                    request.user.last_request_time = datetime.now()
                    if not request.user.online:
                        request.user.online = True
                    request.user.save()
                    request.is_authenticated = True
                except CustomUser.DoesNotExist:
                    request.user_data = None
                    request.is_authenticated = False
            else:
                request.user_data = None    
                request.is_authenticated = False
        else:
            print("JWT_token not found in request...")
            request.user_data = None
            request.is_authenticated = False
        print("out of middleware...",  request.is_authenticated)
    
    
    
    
class DisableCSRF(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)