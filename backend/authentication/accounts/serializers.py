from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser
from . import views
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

class RegisterSerializer(serializers.ModelSerializer):
    
    profile_picture = serializers.ImageField(default='default.jpg')
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def validate(self, data):
        # if not data.get('42_login'):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user =CustomUser(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            profile_picture= validated_data['profile_picture']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    def get(self, id):
        user = CustomUser.objects.get(id=id)
        return user
 
 
 
 
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'username', 'email', 'password','first_name', 'last_name']
        
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'profile_picture': {'required': False},
            'password': {'write_only': True, 'required': False},
        }

    def validate(self, data):
        print('from validate function')
        user = self.context['request'].user
        
        if data.get('username'):
            username = data.get('username')
            if CustomUser.objects.exclude(id=user.id).filter(username=username).exists():
                raise serializers.ValidationError("This username is already taken.")
        
        if data.get('email'):
            email = data.get('email')
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError("This email is invalid.")
        
        if data.get('profile_picture'):
            print ("progile picture = ",data.get('profile_picture'))
            if data.get('profile_picture').content_type  not in ['image/jpeg', 'image/png','image/jpg']:
                raise serializers.ValidationError("photo type not suported ")
        if data.get('first_name'):
            if len(data.get('first_name')) < 2:
                raise serializers.ValidationError("First name is too short.")
        if data.get('last_name'):
            if len(data.get('last_name')) < 2:
                raise serializers.ValidationError("Last name is too short.")
            
        if data.get('password'):
            try:
                validate_password(data.get('password'))
            except ValidationError as e:
                raise serializers.ValidationError({"password": list(e.messages)})
        return data
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance