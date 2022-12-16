from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from lineBot.models import PhotoAlbum


@csrf_exempt
def post(request: WSGIRequest):
    if request.method == "GET":
        return JsonResponse(
            {
                "status": "Get photos succeed",
                "photos": _get_all_photos(int(request.GET["startindex"])),
            }
        )


def _get_all_photos(startindex):
    elem_per_page = 5
    # all posts
    all_photos = PhotoAlbum.objects.order_by("-id")[
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
