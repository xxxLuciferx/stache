import requests
from .models import CustomUser
from django.contrib.auth import authenticate
from . import serializers, views 
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from .serializers import RegisterSerializer, UploadSerializer
from datetime import datetime, timezone,timedelta
import jwt
from rest_framework.views import APIView
from django.core.files.base import ContentFile
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText
from django.middleware.csrf import get_token
import urllib.parse
from rest_framework.decorators import api_view as api_View


def check_onlineFlag():
    from .models import CustomUser
    print("from check_onlineFlag")
    users = CustomUser.objects.all()
    for user in users:
        now = datetime.now(timezone.utc)
        if now - user.last_request_time > timedelta(minutes=5):
            user.online = False
            user.save()

def get_user_data(user):
    return({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_id": user.id,
            "username":user.username,
            "email": user.email,
            "lastname": user.last_name,
            "status" : user.online,
            "profile_picture": user.profile_picture.url,
            "is2FAEnabled": user.auth_2fa
            })


def login(request, user):
    print("from login")
    print("2fa ",user.auth_2fa)
    print("status ",user.online)
    if user.auth_2fa and not user.online:
        token  = generate_jwt(user=user,tamp=90)
        token_query = urllib.parse.urlencode({'token': token})     
        redirect_url = f'/2fa/?{token_query}'
        return Response({'success': True,'message': '2fa required.', 'redirect': redirect_url}, status=status.HTTP_200_OK)
    response = Response({'success': True,'message': "Logged in succesfully", "user":get_user_data(user)}, status=status.HTTP_200_OK)
    user.online = True
    user.save()
    request.user = user
    response.set_cookie("X-CSRFToken", get_token(request), httponly=False)
    response.set_cookie("JWT_token", generate_jwt(user, tamp=180), httponly=False)
    print("out from login")
    return response


def generateResponse(request, msg, status_code):
    print("Generating response")

    token = None

    if request.user.is_authenticated:
        request.user.online = True
        request.user.save()
        token = generate_jwt(request.user, tamp=180)
    csrf_token = get_token(request)
    response = Response({'message': msg}, status=status_code)
    response.set_cookie("X-CSRFToken", csrf_token)
    response.set_cookie("JWT_token", token)
    return response


JWT_SECRET_KEY="yichiba94@"

def generate_jwt(user,tamp):
    print("from generate_jwt")
    print("user-status",user.online)
    payloads = {
        "sub": user.id,
        "username":user.username,
        "email":user.email,
        "iat":datetime.now().timestamp(),
        "exp":(datetime.now() + timedelta(minutes = tamp)).timestamp()
    }
    token = jwt.encode(payloads, JWT_SECRET_KEY, 'HS256')
    return token

def send_email(user):
    message = MIMEText("")
    message["Subject"] = 'reset password -Trancendence'
    message["From"] = "youssefichiba@gmail.com"
    message["To"] = user.email
    token = generate_jwt(user,5)
    url = "http://127.0.0.1:5500/resetpassword/"+token
    message = MIMEText(url)

    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, user.email, message.as_string())
    except Exception as e:
        print(f"Error: {e}")    

    
def get_profile_pict(img_url):
    response = requests.get(url=img_url)
    if response.status_code == 200:
        return ContentFile(response.content)
    return None
    
def save_profile_picture(user, image_url):
    image_file = get_profile_pict(image_url)
    if image_file:
        file_name = f'{user.username}_profile.jpg'
        user.profile_picture.save(file_name, image_file)
        user.save()



def remote_login( user_data, request):
    print("from remote_login Fun")
    random_pasword = get_random_string(12)

    validated_data = {
        "42_login":True,
        "username": user_data['login'],
        "first_name": user_data['first_name'],
        "last_name": user_data['last_name'],
        "email": user_data['email'],
        "password": random_pasword,
        "password_confirm":random_pasword
    }
    print("validated_data",validated_data)
    try:
        existing_user = CustomUser.objects.get(email=validated_data['email'])
        return existing_user
    except CustomUser.DoesNotExist:
        serializer = RegisterSerializer(data=validated_data)
        if serializer.is_valid():
            new_user = serializer.save()
            save_profile_picture(new_user,user_data['image']['versions']['small'])
            return new_user
    return None

def fetch_user_data(access_token):
    user_url = 'https://api.intra.42.fr/v2/me'
    headers = {'Authorization': f'Bearer {access_token}',}

    response = requests.get(user_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  
    return None  


@api_View(['GET'])
def callback_with_42(request):
    print("from callback_with_42")
    code = request.GET.get('code')
    print("code",code)
    if code:
        token_url = 'https://api.intra.42.fr/v2/oauth/token'
        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.UID,
            'client_secret': settings.SECRET,
            'redirect_uri': settings.REDIRECT_URI,
            'code': code
        }

        response = requests.post(token_url, json=payload)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            user_data = fetch_user_data(access_token)
            user = remote_login(user_data,request)
            print("user",user)
            if user :
                response = login(request, user)
                return response
            return Response({'message': 'Login failed. User not found or invalid.','redirect':'home/'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Failed to obtain access token.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'No authorization code found.'}, status=status.HTTP_400_BAD_REQUEST)
    
