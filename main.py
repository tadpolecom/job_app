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

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])
regi_num = '123456'
shift_data=[]


@app.route("/")
def main():
     return "hello world"

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
                            label='日時を選択',
                            mode='datetime',
                            data='time',
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
        print(event.postback.params['datetime'])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('もう一度「シフトを提出」と入力してください'))
    

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'time':
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='登録完了。続けますか？',
                    actions=[
                        DatetimePickerAction(
                            label='日時を選択',
                            mode='datetime',
                            data='time',
                        ),
                        MessageAction(
                            label='終了',
                            text='終了'
                        )
                    ]   
                )
            )
        )
        shift_data.append(event.postback.params['datetime'])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録に失敗しました'))


#herokuにおいてポートはランダムに環境変数PORTで決められる
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT'))