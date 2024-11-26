from . import serializers, remote_login, models, middleware, upload_handler
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, logout
from django.conf import settings
from django.shortcuts import redirect, render
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
import pyotp
import qrcode
import base64
from io import BytesIO
from django.urls import reverse
from rest_framework.exceptions import ValidationError
import requests


@middleware.requires_authentication
@api_view(["GET"])
def get_online_friends(request):
    print("from get_online_friends")
    online = []
    try:
        remote_login.check_onlineFlag()
        friends = models.FriendShip.get_friends(request.user)
        for friend in friends:
            if friend.online:
                online.insert(0,friend.username)
        return Response({f" online friend :{online}"}, status=200)
    except:
        return Response({" error : you have no friends online at the moment . "}, status=404)


@api_view(['POST',"GET"])
def change_passwrd(request,username):
    if request.method == 'GET':
        active_users = []
        users = models.CustomUser.objects.all()
        for user in users:
            active_users.insert(0,user.username)
        return Response({f"users = {active_users}"},status=200)
    if request.method == 'POST':
        new_password = request.data.get('password')
        if new_password:
            user = models.CustomUser.objects.get(username=username)
            serializer = serializers.UploadSerializer(user,data=request.data,context={'request': request}, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response({"password changed successfully"},status=200)
            else:
                return Response({"Error : password is EMPTY or NOT VALID !!!"},status=404)
        return Response({"Error : password is EMPTY or NOT VALID !!!"},status=404)
def get_json_data(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_picture": user.profile_picture.url,
        "status": user.online
    }

@middleware.requires_authentication
@api_view(["GET"])
def get_friends(request):
    print("from get_friends")
    active_friends = []
    friend_requests = []
    # active_friends = models.FriendShip.get_friends(request.user)
    # friend_requests = models.FriendShip.get_friend_requests(request.user)
    # return Response(f"friends:{active_friends} ..."f"     friends_request:{friend_requests}",status=200)
    user = request.user
    try:
        print("from frie friendd dosnot exist ")
        friends = models.FriendShip.objects.filter(user1=user) | models.FriendShip.objects.filter(user2=user)
        if friends.exists():
            for friend in friends:
                if friend.status == True:
                    if friend.user1 == user:
                        active_friends.insert(0,get_json_data(friend.user2))
                    else:
                        active_friends.insert(0,get_json_data(friend.user1))
                else:
                    if friend.user2 == user:
                        friend_requests.insert(0,get_json_data(friend.user1))
            return Response({ 'success' : True,'data' : { 'success' : True, 'friends' : active_friends, 'requests':friend_requests}} ,status=200)
        return Response({ 'success' : True,'data' : { 'success' : True, 'friends' : active_friends, 'requests':friend_requests}} ,status=200)
    except models.FriendShip.DoesNotExist:
            return Response({ 'success' : False, 'data' : { 'success' : False }} ,status=200)    
    
@api_view(["POST"])
@middleware.requires_authentication
def send_friend_request(request, username):
    user1 = request.user
    try: 
        user2 = models.CustomUser.objects.get(username=username)
        
        if user1 != user2:
            try:
                existing_friendship = models.FriendShip.objects.get(user1=user1,user2=user2)
                return Response({'success': False, "msg": "Friend request already sent"}, status=200)
            except models.FriendShip.DoesNotExist:
                try:
                    existing_friendship = models.FriendShip.objects.get(user1=user2,user2=user1)
                    return Response({'success': False, "msg": "Friend request already sent"}, status=200)
                except models.FriendShip.DoesNotExist:
                    models.FriendShip.objects.create(user1=user1, user2=user2)
                    return Response({'success':True,"msg": "Friend request sent successfully"}, status=200)
        else:
            return Response({'success': False, "msg": "You can't send a friend request to yourself"}, status=200)
    except models.CustomUser.DoesNotExist:
        return Response({'success': False, "msg": "User not found"}, status=404)
    

    
    
@api_view(["POST"])
@middleware.requires_authentication
def accept_friend_request(request, username):
    user1 = request.user
    try:
        user2 = models.CustomUser.objects.get(username=username)
        try:
            friendship = models.FriendShip.objects.get(user1=user2, user2=user1)
            if friendship.status == False:
                friendship.status = True
                friendship.save()
                return Response({'success': True ,"message": f"{user2.username} is now your friend"}, status=200)
            else:
                return Response({'success': True, "message": f"{user2.username} is already in your friend list"}, status=200)
        except models.FriendShip.DoesNotExist:
            return Response({'success': False ,"message": "No friendship  found"}, status=404)
    except models.CustomUser.DoesNotExist:
        return Response({'success': False ,"message": "User not found"}, status=404)


@api_view(["GET"])
def get_all_users(request):
    # Get all users, excluding the 'photo' field
    users = models.CustomUser.objects.values(
        'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active'
    )
    friendship= models.FriendShip.objects.values('id', 'user1','user2','status')
    
    return Response({'users':users,'friendships':friendship}, status=200)  

def is_friend(request, username):
    user1 = request.user
    try:
        user2 = models.CustomUser.objects.get(username=username)
        try:
            friendship = models.FriendShip.objects.get(user1=user2, user2=user1)
            return (
                    {
                        "friend":  friendship.status,
                        "recived" : True,
                        "sent" : False
                    })
        except models.FriendShip.DoesNotExist:
            try:
                friendship = models.FriendShip.objects.get(user1=user1, user2=user2)
                return (
                    {
                        "friend":  friendship.status,
                        "recived" : False,
                        "sent" : True
                    })
            except models.FriendShip.DoesNotExist:
                 return (
                    {
                        "friend":  False,
                        "recived" : False,
                        "sent" : False
                    })
    except models.CustomUser.DoesNotExist:
        return ({"message": "User not found"})



@api_view(["POST"])
@middleware.requires_authentication
def reject_friend_request(request, username):
    user1 = request.user
    user2 = models.CustomUser.objects.get(username=username)
    try:
        friendship = models.FriendShip.objects.get(user1=user1, user2=user2)
        friendship.delete()
        return Response({'success': True, "message": f"User : {user2.username} is rejected from your friend"}, status=200)
    except models.FriendShip.DoesNotExist:
        friendship = models.FriendShip.objects.get(user1=user2, user2=user1)
        friendship.delete()
        return Response({'success': True, "message": f"User : {user2.username} is rejected from your friend"}, status=200)


class login_view(APIView):
    def post(self,request):
        print("from loginView Fun")
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        print("username and ppasswordaa",username,password)
        if user is not None:
            response = remote_login.login(request, user)
            return response 
        return Response({'success': False, 'error': 'Invalid credentials'}, status=status.HTTP_200_OK)
        
        


class logout_view(APIView):
    @middleware.requires_authentication
    def post(self, request):
        state = request.user.online
        request.user.online = False
        request.user.save()
        user = models.CustomUser.objects.get(username=request.user.username)
        
        logout(request=request)
        response = Response({'message': f'Logged out successfully!  status = {user.online}  old state {state}'},status=status.HTTP_200_OK)
        response.delete_cookie('JWT_token')
        response.delete_cookie("X-CSRFToken")
        return response
    


class RegisterView(APIView):
    
    @middleware.not_authenticated
    def post(self, request):
        
        print("from reister_view Fun")
        print("request.data = ",request.data)
        serializer = serializers.RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user is not None:
                response = remote_login.login(request, user)
                return response  
        return Response({'success': False,'message': serializer.errors}, status=status.HTTP_200_OK)

class home_view(APIView):
    @middleware.requires_authentication
    def get(self,request):
        return Response("Home page",status=status.HTTP_200_OK)


def login_with_42(request):
    print("login_with_42 fucn")
    auth_url = "https://api.intra.42.fr/oauth/authorize"
    params = {
        "client_id": settings.UID,
        "redirect_uri": settings.REDIRECT_URI,
        "response_type": "code",
        "scope": "public"
    }
    string_params = ''
    for key ,value in params.items():
        if string_params:
            string_params += '&'
        string_params += f"{key}={value}"
    redirect_url = f"{auth_url}?{string_params}"
    print(" ouuuut redirect_url = ",redirect_url)
    return redirect(redirect_url)


class profile(APIView):
    def get(self,request):
        pass


@api_view(["GET", "POST"])
def matches(request,username):
    game = models.game
    if request.method == 'GET':
        try:
            user = models.CustomUser.objects.get(username=username)
            try:
                match = models.game.objects.get(player1=user)
                return Response({'success':True,'data':match},status=200)
            except models.game.DoesNotExist:
                return Response({'success':False,'data':"No match found"},status=404)
        except models.CustomUser.DoesNotExist:
            return Response({'success' : False,'error': f'User {username} not found!'}, status=404)
    
    if request.method == 'POST':
        data = request.data
        try:
            user = models.CustomUser.objects.get(username=username)
            try:
                game = models.game.objects.create(player1=user,player2=data['player2'],player1_score=data['player1_score'],player2_score=data['player2_score'])
                return Response({'success':True,'data':match},status=200)
            except models.game.DoesNotExist:
                return Response({'success':False,'data':"No match found"},status=404)
        except models.CustomUser.DoesNotExist:
            return Response({'success' : False,'error': f'User {username} not found!'}, status=404)







class users(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @middleware.requires_authentication
    def get(self, request, username):
        if username == "me":
            username = request.user_data['username']
        try:
            user = models.CustomUser.objects.get(username=username)
            data  = is_friend(request, username)
            img_url = user.profile_picture.url
            print("image url = ",img_url)
            profile_picture_url =  request.build_absolute_uri( "/backend"+ img_url) 
            profile_picture_url = profile_picture_url.replace("http://", "https://")
            print ("hada howa l url =?>>>>" + profile_picture_url)
            response = Response({'success':True ,'user': {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_id": user.id,
                "username":user.username,
                "email": user.email,
                "lastname": user.last_name,
                "status" : user.online,
                "profile_picture":profile_picture_url,
                "is2FAEnabled": user.auth_2fa,
                "friend":  data["friend"],
                "recived" : data["recived"],
                "sent" : data["sent"]
        
            }})
            return response
        except models.CustomUser.DoesNotExist:
            return Response({'success' : False,'error': f'User {username} not found!'}, status=404)
        
        
    @middleware.requires_authentication
    def post(self, request, username):
        response = Response()
        print("from post user,   request = ",request.data)
        
        if username == "me":
            username = request.user_data['username']
        responses = {} 
        if username == request.user_data['username']:
            user = request.user
            for field, value in request.data.items():
                partial_data = {field: value}
                handler = getattr(upload_handler, f"_handle_{field}", None)
                if handler:
                    print("field = ",field)
                    responses[field] = handler(request,partial_data)
                    print("responses = ",responses)
                    if field == 'username' and 'success' in responses['username']:
                        print("from username   COOKIES================")
                        response.set_cookie("JWT_token", remote_login.generate_jwt(user, tamp=180), httponly=False)

        response.data = responses
        response.status_code = status.HTTP_200_OK
        response.success = True
        return response           




@api_view(['POST',"GET"])
def forgot_passwd(request):
    print("from forgot fun ")       
    if request.method == 'POST':
        email = request.data['email']
        print("email = ",email)
        if email :
            try:
                print("from try  1")
                user = models.CustomUser.objects.get(email=email)
                remote_login.send_email(user)
                return Response({'success':True, 'data' : "check your Email" , '2FA' :user.auth_2fa },status=200)
            except models.CustomUser.DoesNotExist :
                try:
                    print("from try  1")
                    user = models.CustomUser.objects.get(username=email)
                    remote_login.send_email(user)
                    return Response({'success':True, 'data' : "check your Email ", '2FA' :user.auth_2fa},status=200)

                except models.CustomUser.DoesNotExist :
                    return Response({'success': False, 'error': f"user with email / username : '{email}'  NOT FOUND "},status=400)
        return Response({"error : no user found "},status=404)


@api_view(["POST"])
def reset_password(request,token):
    print("from reset fun  ")
    if  request.method == 'POST':
        new_password = request.data.get('password')
        if new_password:
            payload = middleware.JWTCheck(token)
            if payload:
                    user = models.CustomUser.objects.get(username=payload['username'])
                    serializer = serializers.UploadSerializer(user,data=request.data,context={'request': request}, partial=True)
                    if serializer.is_valid():
                        user = serializer.save()
                        return Response({"password changed successfully"},status=200)
                    else:
                        return Response({"Error : password is EMPTY or NOT VALID !!!"},status=404)
            else:
                return Response({"token Expired or not vaalid anymore"},status=404)
        return Response({"token expired or is not vaalid"},status=404)
    return Response({"Error : password is EMPTY or NOT VALID !!!"},status=404)



class generate_OTP(APIView):

    def get_user_from_request(self, request):
        if request.is_authenticated:
            return request.user
        token = request.GET.get('token')
        if not token:
            raise ValidationError("No authentication provided")
            
        try:
            payload = middleware.JWTCheck(token=token)
            return models.CustomUser.objects.get(username=payload['username'])
        except Exception as e:
            raise ValidationError("Invalid token")
        

    def generate_qr_code(self, secret, username):
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=username,
            issuer_name="Transcendence 42 :Baraka_3lia "
        )

        qr = qrcode.make(provisioning_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    def get(self, request):
        print("from generate_otp")
        user = self.get_user_from_request(request)
        print("user = ",user)
        if user.auth_2fa:
            print("user.auth_2fa = ",user.auth_2fa)
            return Response({'success': True, "is2FAEnabled": user.auth_2fa}, status=200)
        user.mfa_secret = pyotp.random_base32()
        user.save()
        totp = pyotp.TOTP(user.mfa_secret)
        qr_code_uri = totp.provisioning_uri(name=user.username, issuer_name="tryy")

        qr = qrcode.make(qr_code_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        print("qr_base64 = ",qr_base64)
        return Response({
            'sucess':True,
            "is2FAEnabled": user.auth_2fa,
            "qr_code": f"data:image/png;base64,{qr_base64}"}, status=200)

    def post(self, request):
        user=self.get_user_from_request(request) 
        token = request.GET.get('token')
        
        if not user:
            return Response({"message": "Invalid token"}, status=400)
        otp = request.data.get('otp')
        print("aaaaaaaaaa   otp = ",otp)
        if otp:
            # Verify the OTP
            print("verifying otp")
            totp = pyotp.TOTP(user.mfa_secret)
            if totp.verify(otp):
                    
                print("otp verified")
                if  user.auth_2fa :
                    print(" 2fa token = ",token)
                    if request.is_authenticated:
                        user.auth_2fa = False
                        user.save()
                        print("responsssssssse = ")
                        return Response({'succes':'true',"message": "2FA disabled"}, status=200)
                    user.online = True
                    response=remote_login.login(request,user)
                    user.save()
                    print("response = ",response.data)
                    return response
                else:
                    user.auth_2fa = True
                    user.save()
                    return Response({'success':'true',"message": "2FA enabled"}, status=200)
            else:
                print("Invalid OTP Ressssspomnse")
                return Response({ "message": "Invalid OTP"}, status=200)
        else:
            return Response({"message": "OTP is required"}, status=200)
