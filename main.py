import os

from flask import Flask, request, abort, render_template, request, redirect, send_from_directory
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ConfirmTemplate,DatetimePickerAction,MessageAction,PostbackEvent
)
import psycopg2
import xlsxwriter

            

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])
get_connection = psycopg2.connect(os.environ.get('DATABASE_URL'))
regi_num = '123456'
shift_data=[]


@app.route("/")
def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM member_tb', ('foo',))
            rows = cur.fetchall()

    tmp = []
    data = []
    for item in rows:
        tmp.append(item)
        for item in tmp:
            data.append(tmp)

    rowNum = 0
    workbook = xlsxwriter.Workbook('fileName' + '.xlsx')
    worksheet = workbook.add_worksheet('issues')
    rowNum = 0
    for tmp in rows:
        j = 0
        for item in tmp:
            worksheet.write(rowNum, j, item)
            j += 1
        rowNum += 1
    workbook.close()

    DOWNLOAD_DIR_PATH = "."
    downloadFileName = "test.xlsx"
    downloadFile = "fileName.xlsx"

    return send_from_directory(DOWNLOAD_DIR_PATH, downloadFile, \
        as_attachment = True, attachment_filename = downloadFileName, \
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

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
        enter=[]
        for i in range(1,len(shift_data)):
            enter.append([shift_data[0],shift_data[i+1],shift_data[i+2],shift_data[i+3]])
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO shift_table (id,date,start,last) VALUES (%s, %s, %s, %s)',enter)
            conn.commit()
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