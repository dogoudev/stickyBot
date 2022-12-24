from django.db import models

# Create your models here.

class LineChat(models.Model):
    groupId = models.CharField(max_length=100)
    userId = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    text = models.TextField(blank=True)
    fileId = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class ChannelInfo(models.Model):
    groupId = models.CharField(max_length=100)
    imgurAlbum = models.CharField(max_length=20, default='')
    albumAlias = models.CharField(max_length=20, default='')
    googleDriveId=models.CharField(max_length=100, default='')
    googleDriveUrl=models.CharField(max_length=150, default='')

class PhotoAlbum(models.Model):
    groupId = models.CharField(max_length=100)
    userId = models.CharField(max_length=100)
    imageUrl = models.CharField(max_length=100)
    width =  models.IntegerField()
    height = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)