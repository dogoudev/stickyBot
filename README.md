# stickyBot
## 透過lineBot串接imgur api自動將圖片上傳, 並提供相簿展示, 也可上傳檔案至GOOGLE DRIVE

Install Django 3.2.16

    pip install "django==3.2.16"

Install line-bot-sdk

    pip install line-bot-sdk

Install imgur python

    pip install imgurpython

Install pydrive

    pip install pydrive

Add lineBot_site/local_settings.py(LINE & IMGUR TOKEN)

    LINE_CHANNEL_ACCESS_TOKEN = 'Messaging API的Channel access token'
    LINE_CHANNEL_SECRET = 'Basic settings的Channel Secret'    
    IMGUR_CLIENT_ID = 'IMGUR CLIENT ID'
    IMGUR_CLIENT_SECRET = 'IMGUR CLIENT SECRET'
    IMGUR_ACCESS_TOKEN = 'IMGUR ACCEES TOKEN'
    IMGUR_REFRESH_TOKEN = 'IMGUR REFRESH TOKEN'

Add client_secrets.json & settings.yaml(google drive auth)
    
    REF: https://jackkuo.org/post/pydrive%E5%82%99%E4%BB%BD%E6%95%99%E5%AD%B8/
    

Create DB

    python manage.py migrate

Run Server

    python manage.py runserver
