from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from . import media

class CustomUser(AbstractUser):
    username = models.CharField(max_length = 100, unique = True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to="",default="default.jpg",)
    mfa_secret = models.CharField(max_length=100, null=True)
    auth_2fa=models.BooleanField(default= False,null=True)
    last_request_time = models.DateTimeField(auto_now=True)
    online = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    

class   FriendShip(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name="user2")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    @classmethod
    def get_friends(cls, user):
        """Get all friends for a user."""
        friendships = cls.objects.filter(
            (Q(user1=user) | Q(user2=user)) & Q(status=True)
        )
        friends = [f.user2 if f.user1 == user else f.user1 for f in friendships]
        return friends
    
    
    
    
    
    @classmethod
    def get_friend_requests(cls, user):
        """Get all friends for a user."""
        friendships = cls.objects.filter(
            Q(user2=user) & Q(status=False)
        )
        friends = [f.user2 if f.user1 == user else f.user1 for f in friendships]
        return friends





class  game(models.Model):
    player1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name="player2")
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    @classmethod
    def get_matches(cls, user):
        """Get all friends for a user."""
        friends = cls.objects.filter(
            (Q(user1=user) | Q(user2=user)))
        return friends
    