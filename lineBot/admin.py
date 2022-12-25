from django.contrib import admin

# Register your models here.
from .models import LineChat, PhotoAlbum, ChannelInfo

admin.site.register(LineChat)
admin.site.register(PhotoAlbum)
admin.site.register(ChannelInfo)