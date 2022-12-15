from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from lineBot.models import LineChat

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage
import json

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def hello_world(request):
    return HttpResponse("Hello World!")

# 忽略CSRF檢查
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)  # 傳入的事件
            print(events)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            #如果事件為訊息
            if isinstance(event, MessageEvent):
                if event.message.type=='text':
                    add_chat_logs(event)
                    if event.message.text == '給我一張圖片':
                        #寫死圖片供測試
                        give_me_a_picture(event.reply_token, 'uLlpYnm')

                    # message關鍵字邏輯
                    else:
                        line_bot_api.reply_message(  # 回復傳入的訊息文字
                            event.reply_token,
                            TextSendMessage(text=str(event))
                        )
                elif event.message.type=='image':
                    imgage = line_bot_api.get_message_content(event.message.id)
                    #TODO: ..... 上傳到imgur

                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage('得到一張圖片\r\n' + str(event))
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


#獨立function處理, 程式會比較容易閱讀
def give_me_a_picture(token, alias):
    line_bot_api.reply_message(  # 回復傳入的訊息文字
        token,
        ImageSendMessage(
            original_content_url='https://i.imgur.com/' + alias + '.jpg',
            preview_image_url='https://i.imgur.com/' + alias + 't.jpg',
        )
    )

def add_chat_logs(event):
    groupId = event.source.group_id if event.source.type == 'group' else event.source.user_id
    text = event.message.text if event.message.type == 'text' else ''
    photoId =  event.message.id if event.message.type == 'image' else ''

    LineChat.objects.create(
        groupId = groupId,
        userId = event.source.user_id,
        type = event.message.type,
        text = text,
        photoid = photoId,
    )

def album(request):
    return render(request, "index.html")
