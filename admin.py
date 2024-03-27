from django.contrib import admin
from .models import Room, Community, RoomMessage, User

# Register your models here.
admin.site.register(User)
admin.site.register(Room)
admin.site.register(Community)
admin.site.register(RoomMessage)

