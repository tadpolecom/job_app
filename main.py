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
                            label='message',
                            text='終了'
                        )
                    ]   
                )
            )
        )
    elif event.message.text == "終了":
        line_bot_api.reply_message(event.reply_token, TextSendMessage('thank you'))
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
                            label='message',
                            text='終了'
                        )
                    ]   
                )
            )
        )
        print(event.postback.params['datetime'])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録に失敗しました'))


#herokuにおいてポートはランダムに環境変数PORTで決められる
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT'))
    


"""
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='Are you sure?',
                actions=[
                    DatetimePickerAction(
                        label='日時を選択',
                        mode='datetime',
                        data='time',
                    ),
                    MessageAction(
                        label='message',
                        text='message text'
                    )
                ]   
            )
        )
    )
"""

"""import os

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ConfirmTemplate,DatetimePickerAction,MessageAction,PostbackEvent

app = Flask(__name__)


line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

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
    return "ok"

class hanble_message():
    shit_data = []
    def __init__(self, id):
        self.id = id
        self.shift_flag = False
        self.number_flag = False
        self.desire_flag = False


    def shift(self):
        if event.message.text == "シフトを提出":
            line_bot_api.reply_message(event.reply_token, TextSendMessage('登録番号を入力してください(6桁数字)'))
            self.shift_flag = True
    def number(self):
        hanble_message.shit_data.insert(0,event.message.text)
        if len(shit_data[0]) != 6:
                line_bot_api.reply_message(event.reply_token, TextSendMessage('登録番号が間違っています(6桁数字)'))
        elif len(shit_data[0]) == 6:
                self.number_flag = True
    def desire(self):
        if event.message.text == "終了":
            self.desire_flag = True
        else:
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
                                label='message',
                                text='終了'
                            )
                        ]   
                    )
                )
            )


@handler.add(MessageEvent, message=TextMessage)
def get_message(event):
    if session == None:
        session = hanble_message(event.source.user_id)  
    elif session.shift_flag + session.number_falg + session.enter_flag == False:
        session.shift()  
    elif session.shift_flag == True:
        session.number()
    elif session.number_falg == True:
        session.desire()
    elif session.enter_flag == True:
        pass

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'time':
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録完了'))
        hanble_message.shit_data.append(event.postback.params['datetime'])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録に失敗しました'))

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0',port=os.environ.get('PORT'))

def check_message(event):
    if event.message.text == "シフトを提出":
        while True:
            line_bot_api.reply_message(event.reply_token, TextSendmessage('登録番号を入力してください(6桁数字)'))
            if len(RegiNum=event.message.text) != 6:
                break
                line_bot_api.reply_message(event.reply_token, TextSendmessage('登録番号が間違っています(6桁数字)'))
            elif len(RegiNum=event.message.text) == 6:
                while True:
                    if event.message.text == "終了":
                        break
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
                                    messageAction(
                                        label='message',
                                        text='終了'
                                    )
                                ]   
                            )
                        )
                    )
"""

