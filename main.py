import os

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ConfirmTemplate,DatetimePickerAction,MessageAction,PostbackEvent
)

from db import shift

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])
regi_num = '123456'
shift_data=[]


@app.route("/")
def main():
    
    return shift.into_xlsx()

@app.route("/callback", methods=['POST'])
def callback():
    # hederとbodyから署名の確認に必要な情報を取得
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    # 署名の確認
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def check_messege(event):
    if event.message.text == "シフトを提出":
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録番号を入力してください(6桁数字)'))
    elif event.message.text == regi_num:
        shift_data.append(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='シフトを入力しますか？',
                    actions=[
                        DatetimePickerAction(
                            label='日付',
                            mode='date',
                            data='date',
                        ),
                        MessageAction(
                            label='終了',
                            text='終了'
                        )
                    ]   
                )
            )
        )
    elif event.message.text == "終了":
        line_bot_api.reply_message(event.reply_token, TextSendMessage('thank you'))
        shift.insert(shift_data)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('もう一度「シフトを提出」と入力してください'))
    

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'end':
        shift_data.append(event.postback.params['time'])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='シフトを入力しますか？',
                    actions=[
                        DatetimePickerAction(
                            label='日付',
                            mode='date',
                            data='date',
                        ),
                        MessageAction(
                            label='終了',
                            text='終了'
                        )
                    ]   
                )
            )
        )
    elif event.postback.data == 'date':
        shift_data.append(event.postback.params['date'])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='開始時間を入力してください',
                    actions=[
                        DatetimePickerAction(
                            label='開始時間',
                            mode='time',
                            data='start',
                        ),
                        MessageAction(
                            label='終了',
                            text='終了'
                        )
                    ]   
                )
            )
        )
    elif event.postback.data == 'start':
        shift_data.append(event.postback.params['time'])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='終了を入力してください',
                    actions=[
                        DatetimePickerAction(
                            label='終了時間',
                            mode='time',
                            data='end',
                        ),
                        MessageAction(
                            label='終了',
                            text='終了'
                        )
                    ]   
                )
            )
        )     
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録に失敗しました'))



#herokuにおいてポートはランダムに環境変数PORTで決められる
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT'))