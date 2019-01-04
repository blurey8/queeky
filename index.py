from flask import Flask, request, abort
from dotenv import load_dotenv, find_dotenv
import os
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
load_dotenv(find_dotenv())

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: {}'.format(body)) # Debug
    # app.logger.info(os.environ.get('CHANNEL_ACCESS_TOKEN'))

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    query = event.message.text.split()

    # Returning user profile detail
    if (query[0] == '.profile'):
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Name: {}\nUser ID: {}\nPicture URL: {}\
                \nStatus: {}'.format(
                    profile.display_name,
                    profile.user_id,
                    profile.picture_url,
                    profile.status_message
                )
            )
        )

    elif (query[0] == '.movie'):
        title = ' '.join(query[1:])
        url = 'http://www.omdbapi.com/?t={}&apikey=e943aca8'.format(title)
        # printx # error
        response = requests.get(url)

        # profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=response.json()
                )
            )
        )

    else:
        # Echo
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )


if __name__ == "__main__":
    app.run()
