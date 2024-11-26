from django.db import models

class Room(models.Model):
    room_name = models.CharField(max_length=50, unique=True)
    # room_id = models.IntegerField(unique=True)
    user1 = models.CharField(max_length=50)
    user2 = models.CharField(max_length=50)

    def checkSorted(self, *args, **kwargs):
        if self.user1 > self.user2:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

class Meta:
    unique_together = ('user1', 'user2')

class Message(models.Model):
        room = models.ForeignKey(Room, on_delete=models.CASCADE)
        sender = models.CharField(max_length=50)
        message = models.TextField()
        # time_stamp = models.DateTimeField(auto_now_add=True)
        
        def __str__(self):
            return f"{str(self.room)} - {self.sender}"

