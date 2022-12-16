# lineBot_site
## 透過lineBot串接imgur api自動將圖片上傳, 並至網頁展示

Install Django 3.2.16

    pip install "django==3.2.16"

Install line-bot-sdk

    pip install line-bot-sdk

Install imgur python

    pip install imgurpython

Modify settings.py

    LINE_CHANNEL_ACCESS_TOKEN = 'Messaging API的Channel access token'
    LINE_CHANNEL_SECRET = 'Basic settings的Channel Secret'

Create DB

    python manage.py migrate

Run Server

    python manage.py runserver
