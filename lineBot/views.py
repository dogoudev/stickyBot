from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from lineBot.models import LineChat, PhotoAlbum, ChannelInfo

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage,  ImageSendMessage
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import tempfile, os

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
client = ImgurClient(settings.IMGUR_CLIENT_ID, settings.IMGUR_CLIENT_SECRET, settings.IMGUR_ACCESS_TOKEN, settings.IMGUR_REFRESH_TOKEN)

def album(request, id):
    return render(request, "index.html", {'album': id})

def hello_world(request):
    return HttpResponse("Hello World!")

# 忽略CSRF檢查
@csrf_exempt
# LineBot webhook
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)  # 傳入的事件
            print(events)
        except InvalidSignatureError as err:
            print(f"InvalidSignatureError {err=}, {type(err)=}")
            print(err)
            return HttpResponseForbidden()
        except LineBotApiError as err:
            print(f"LineBotApiError {err=}, {type(err)=}")
            print(err)
            return HttpResponseBadRequest()
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            print(err)

        for event in events:
            #如果事件為訊息
            if isinstance(event, MessageEvent):
                add_chat_logs(event)
                if event.message.type=='text':
                    text_logic(event)
                elif event.message.type=='image':
                    upload_to_imgur(event)      
                elif event.message.type=='file':
                    upload_to_googledrive(event)              
                # elif event.message.type=='location':
                #     line_bot_api.reply_message(  # 回復傳入的訊息文字
                #         event.reply_token,
                #         TextSendMessage(text=str(event))
                #     )
                # elif event.message.type=='video':
                #     line_bot_api.reply_message(  # 回復傳入的訊息文字
                #         event.reply_token,
                #         TextSendMessage(text=str(event))
                #     )
                # elif event.message.type=='sticker':
                #     line_bot_api.reply_message(  # 回復傳入的訊息文字
                #         event.reply_token,
                #         TextSendMessage(text=str(event))
                #     )
                # elif event.message.type=='audio':
                #     line_bot_api.reply_message(  # 回復傳入的訊息文字
                #         event.reply_token,
                #         TextSendMessage(text=str(event))
                #     )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# GET EVNT INFO
def get_event_info(event):
    groupId = event.source.group_id if event.source.type == 'group' else event.source.user_id
    userId = event.source.user_id
    text = event.message.text if event.message.type == 'text' else ''
    fileId =  event.message.id
    return groupId, userId, text, fileId
    
# 將事件寫入CHAT LOG, 每天刪除昨日資料(TODO)    
def add_chat_logs(event):
    groupId, userId, text, fileId = get_event_info(event)
    LineChat.objects.create(
        groupId = groupId,
        userId = userId,
        type = event.message.type,
        text = text,
        fileId = fileId,
    )

# 取得頻道資料
def get_channel(groupId):
    channel = ChannelInfo.objects.get_or_create(
        groupId= groupId,
    )[0]
    return channel

# 更新頻道資料
def update_channel(groupId, imgurAlbum, albumAlias, googleDriveId, googleDriveUrl):
    channel = ChannelInfo.objects.get_or_create(
        groupId= groupId,
    )[0]
    if imgurAlbum:
        channel.imgurAlbum = imgurAlbum
    if albumAlias:
        channel.albumAlias = albumAlias
    if googleDriveId:
        channel.googleDriveId = googleDriveId
    if googleDriveUrl:
        channel.googleDriveUrl = googleDriveUrl
    channel.save()
    return channel

# 刪除頻道資料, 但IMGUR與GOOGLE DRIVE檔案保留, 重新建立頻道後IMGUR會設定新的相簿, GOOGLE DRIVE則沿用
def del_channel(groupId):
    ChannelInfo.objects.filter(groupId=groupId).delete()

# 建立IMBUG相簿
def create_album(albumAlias, ids):    
    try:
        album = client.create_album({'ids': ids, 'title': albumAlias })
        return album['id']
    except ImgurClientError as e:
        print(e.error_message)
        print(e.status_code)
        return ''

def getGoogleDrive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile() 
    if gauth.access_token_expired:
        # Refresh them if expired
        try:
            gauth.Refresh()
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            print(err)
    else:
        # Initialize the saved creds
        gauth.Authorize()
    return GoogleDrive(gauth)

# MESSAGE 文字處理邏輯
def text_logic(event):
    groupId, userId, text, photoId = get_event_info(event)
    if text[:8] == '貼貼 我的相簿叫':
        channel = get_channel(groupId)
        albumAlias = text[8:]
        if channel.imgurAlbum:
            client.update_album(
                channel.imgurAlbum,
                { 'ids': None, 'title': albumAlias, } )
        channel = update_channel(groupId, None, albumAlias, '', '')
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='好喔, 幫你把群組相簿改名為' + channel.albumAlias)
        )
    elif text[:7] == '貼貼 刪掉資料':
        del_channel(groupId)
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(text='Channel資料刪掉囉')
        )
    elif text[:7] == '貼貼 搜尋檔案':
        search_key = text[8:]
        search_file(event, search_key)
    elif text[:9] == '貼貼 給我相簿網址':
        channel = get_channel(groupId)
        if channel.imgurAlbum:
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                TextSendMessage(text='https://sticky.fly.dev/album/' + channel.imgurAlbum)
            )
        else:
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                TextSendMessage(text='先上傳個圖片來啊')
            )
    elif text[:19] == '貼貼 給我google drive網址':
        channel = get_channel(groupId)
        if channel.googleDriveUrl:
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                TextSendMessage(text=channel.googleDriveUrl)
            )
        else:
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                TextSendMessage(text='先上傳個檔案來啊')
            )
    else:
        return
        
# 收到IMAGE MESSAGE時上傳IMGUR        
def upload_to_imgur(event):
    groupId, userId, text, photoId = get_event_info(event)
    message_content = line_bot_api.get_message_content(photoId)
    channel = get_channel(groupId)
    ext = 'jpg'
    # 把LINE MESSAGE的圖片存到暫存檔
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name
    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    try:
        config = {
            'album': channel.imgurAlbum,
            'name': None,
            'title': None,
            'description': None
        }
        path = os.path.join('lineBot', 'static', 'tmp', dist_name)
        # 上傳圖片到IMGUR
        image = client.upload_from_path(path, config=config, anon=False)
        os.remove(path)

        # 初次上傳建立相簿
        if channel.imgurAlbum == '':
            albumAlias = channel.albumAlias if channel.albumAlias > '' else groupId
            imgurAlbum = create_album(albumAlias, image['id'])
            update_channel(groupId, imgurAlbum, albumAlias, '', '')

        # 儲存圖片資訊資料庫至
        PhotoAlbum.objects.create(
            groupId = groupId,
            userId = userId,
            imageUrl = 'https://i.imgur.com/' + image['id'] + '.jpg',
            width = image['width'],
            height = image['height']
        )

        line_bot_api.reply_message(
            event.reply_token,
                TextSendMessage(text='上傳成功'))
    except ImgurClientError as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='上傳失敗'))
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print(err)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='上傳失敗'))

# 收到FILE MESSAGE時上傳DOC, 已有相同檔名則無法上傳
def upload_to_googledrive(event):
    groupId, userId, text, fileId = get_event_info(event)
    channel = get_channel(groupId)

    # gauth = GoogleAuth()
    # gauth.CommandLineAuth() #透過授權碼認證
    # drive = GoogleDrive(gauth)
    drive = getGoogleDrive()
    fileName = event.message.file_name
    message_content = line_bot_api.get_message_content(fileId)
    # 把LINE MESSAGE的檔案存到暫存檔
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=fileName + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name
    os.rename(tempfile_path, os.path.join('lineBot', 'static', 'tmp', fileName))
    path = os.path.join('lineBot', 'static', 'tmp', fileName)
    try:
        if not channel.googleDriveId or not channel.googleDriveUrl:
            file_list = drive.ListFile({'q': 'mimeType = "application/vnd.google-apps.folder" and trashed=false'}).GetList()
            folder = [f for f in file_list  if f['title']==groupId ]
            if not folder:
                file_metadata = {
                    'title': groupId,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'shared': True
                }
                folder = drive.CreateFile(file_metadata)            
                folder.Upload()
                folder.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'})
                file_list = drive.ListFile({'q': 'mimeType = "application/vnd.google-apps.folder" and trashed=false'}).GetList()
                folder = [f for f in file_list  if f['title']==groupId ]
            channel = update_channel(groupId, '', '', folder[0]['id'], folder[0]['alternateLink'])
        file_list = drive.ListFile({'q': '"' + channel.googleDriveId + '" in parents and trashed=false'}).GetList()
        file_exist = [f for f in file_list  if f['title']==fileName ]
        if file_exist:
            line_bot_api.reply_message(
                event.reply_token,
                    TextSendMessage(text='檔名重複'))
            return 
        
        file1 = drive.CreateFile({
                'parents': [{'id': channel.googleDriveId}],
                'title': fileName,
        })  # 建立檔案
        file1.SetContentFile(path) # 編輯檔案內容
        file1.Upload() #檔案上傳
        file1.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'})
        os.remove(path)
        line_bot_api.reply_message(
            event.reply_token,
                TextSendMessage(text=file1['alternateLink']))
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print(err)
        os.remove(path)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='上傳失敗'))

# 搜尋GOOGLE DRIVE檔案
def search_file(event, key):
    groupId, userId, text, fileId = get_event_info(event)
    channel = get_channel(groupId)
    drive = getGoogleDrive()

    if not key:
        line_bot_api.reply_message(
            event.reply_token,
                TextSendMessage(text='請直接輸入搜尋檔案名稱關鍵字\r\n如: 貼貼 搜尋檔案PDF'))
        return

    file_list = drive.ListFile({'q': '"' + channel.googleDriveId + '" in parents and trashed=false'}).GetList()
    match_list = []
    for f in file_list:
        if key in f['title'].lower():
            match_list.append(f['title'])     
            match_list.append(f['alternateLink'])    
    if match_list:
        line_bot_api.reply_message(
            event.reply_token,
                TextSendMessage(text='\r\n'.join(match_list)))
    else:
        line_bot_api.reply_message(
            event.reply_token,
                TextSendMessage(text='查無檔案'))
