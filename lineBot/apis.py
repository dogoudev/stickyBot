from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from lineBot.models import PhotoAlbum, ChannelInfo


@csrf_exempt
def post(request: WSGIRequest):
    if request.method == "GET":
        return JsonResponse(
            {
                "status": "Get photos succeed",
                "photos": _get_all_photos(int(request.GET["startindex"]), request.GET["albumId"]),
                "albumName": _get_album_name(request.GET["albumId"])
            }
        )

def _get_album_name(albumId):
    channel = ChannelInfo.objects.filter(imgurAlbum=albumId).first()
    if not bool(channel):
        return '請先上傳照片'
    return channel.albumAlias

def _get_all_photos(startindex, albumId):
    elem_per_page = 10
    channel = ChannelInfo.objects.filter(imgurAlbum=albumId).first()

    # 偷懶寫死一下
    if not bool(channel):
        photo_data = {
            "groupId": '',
            "userId": '',
            "imageUrl": 'https://i.imgur.com/6Xs6yB2.jpg',
            "width": 1,
            "height": 1,
            "photoDate": None,
        }
        return [photo_data, photo_data, photo_data]

    # all posts
    all_photos = PhotoAlbum.objects.filter(groupId=channel.groupId).order_by("-created_at")[
        elem_per_page * startindex : elem_per_page * (startindex + 1)
    ]
    photos = []

    for _photo in all_photos:
        photo_data = {
            "groupId": _photo.groupId,
            "userId": _photo.userId,
            "imageUrl": _photo.imageUrl,
            "width": _photo.width,
            "height": _photo.height,
            "photoDate": _photo.created_at,
        }
        photos.append(photo_data)

    return photos
