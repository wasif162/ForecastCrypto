from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    About = models.TextField(null=True)
    picture = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Community(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Room(models.Model):
    buddy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) #host
    subject = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True) #topic
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)#null True means it can have an empty value in the database. Blank True means if we are creating a form then it can remain empty aswell
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updateTime = models.DateTimeField(auto_now=True) #auto_Now takes a snapshot at every time we save the room item. This value will change everytime
    creation = models.DateTimeField(auto_now_add=True) #auto_now_add only saves the time when we FIRST created this instance/room.This value will never change, it will remain as the initial time

    class Meta:
        ordering = ['-updateTime', '-creation'] #Newest Room will show on top with the negative sign put in the syntax

    def __str__(self):
        return self.name

class RoomMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #One to Many, user can have many msgs but a msg can have only one use
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #One to Many relationship
    body = models.TextField()
    updateTime = models.DateTimeField(auto_now=True)
    creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updateTime', '-creation']

    def __str__(self):
        return self.body[0:50] #only the first 50 msgs
    

