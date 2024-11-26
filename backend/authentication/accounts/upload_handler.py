
from django.conf import settings
from rest_framework import status
from . import serializers










def _handle_username(request, partial_data):
    print("from handle_username")
    user = request.user
    serializer = serializers.UploadSerializer(user, data=partial_data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("username updated")
        return {"success": "Username updated successfully"}
    return {"error": "invalid username"}


def _handle_email(request, partial_data):
    print("from handle_email")
    user = request.user
    serializer = serializers.UploadSerializer(user, data=partial_data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("email updated")
        return {"success": "Email updated successfully"}
    return {"error":  "Invalid email "}


def _handle_password(request, partial_data):
    print("from handle_password")
    user = request.user
    serializer = serializers.UploadSerializer(user, data=partial_data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("password updated")
        return {"success": "Password updated successfully"}
    return {'error': "Password is not strong enough"}


def _handle_first_name(request, partial_data):
    print("from handle_first_name")
    user = request.user
    serializer = serializers.UploadSerializer(user, data=partial_data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return {"success": "First name updated successfully"}
    return {"error": serializer.errors.get('first_name', "Invalid first name")}


def _handle_last_name(request, partial_data):
    print("from handle_last_name")
    user = request.user
    serializer = serializers.UploadSerializer(user, data=partial_data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("last name updated")
        return {"success": "Last name updated successfully"}
    return {"error": serializer.errors.get('last_name', "Invalid last name")}


def _handle_profile_picture(request, partial_data):
    print("from handle_profile_picture")
    user = request.user
    serializer = serializers.UploadSerializer(user, data=partial_data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("profile picture updated")
        return {"success": "Profile picture updated successfully"}
    return {"error": serializer.errors.get('profile_picture', "Invalid profile picture")}


