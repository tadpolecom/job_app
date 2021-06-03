import os

from flask import Flask, request, abort, send_from_directory
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
regi_num = ['123456','abcdef']
shift_data=[]
regi_flag = False
enter_flag = False


@app.route("/")
def main():
    with get_connection as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM shift_table', ('foo',))
            data = cur.fetchall()

    workbook = xlsxwriter.Workbook('fileName' + '.xlsx')
    worksheet = workbook.add_worksheet('issues')
    row = 0
    col = 0
    for i in data:
        for j in i:
            worksheet.write(row, col, j)
            col =+ 1
        row =+ 1
    workbook.close()

    DOWNLOAD_DIR_PATH = "."
    downloadFileName = "test.xlsx"
    downloadFile = "fileName.xlsx"

    return send_from_directory(DOWNLOAD_DIR_PATH, downloadFile, \
        as_attachment = True, attachment_filename = downloadFileName, \
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "ok"


@handler.add(MessageEvent, message=TextMessage)
def check_messege(event):
    if event.message.text == "シフトを提出":
        line_bot_api.reply_message(event.reply_token, TextSendMessage('登録番号を入力してください(6桁数字)'))
        regi_flag = True
    elif event.message.text in regi_num and regi_flag == True:
        enter_flag = True
        shift_data.append(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度「シフトを提出」と入力してください',
                template=ConfirmTemplate(
                    text='日付を入力してください',
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
    elif event.message.text == "終了" and regi_flag and enter_flag == True:
        if ((len(shift_data) - 1) % 3) == 0:
            enter = []
            for i in range(round((len(shift_data) - 1) / 3)):
                enter.append([shift_data[0], shift_data[3*i + 1], shift_data[3*i + 2], shift_data[3*i + 3]])
 
            with get_connection as conn:
                with conn.cursor() as cur:
                    cur.executemany('INSERT INTO shift_table (id,date,start,last) VALUES (%s, %s, %s, %s)',enter)
                conn.commit()
            line_bot_api.reply_message(event.reply_token, TextSendMessage('提出が完了しました。'))
            regi_flag = False
            enter_flag = False
        else:
            handle_error('途中で終了しました。「シフトを提出」と入力し、もう一度始めからお願いします。',event.reply_token)
    elif regi_flag == True:
        handle_error('登録番号が間違っています。',event.reply_token)
    elif enter_flag == True:
        handle_error('先ほど送信されたボタンのどちらかを押してください。送信されていない場合は「シフトを提出」と入力し、もう一度始めからお願いします。',event.reply_token)
    else:
        handle_error('シフトを提出するためには「シフトを提出」と入力してください。',event.reply_token)

def handle_error(messege,reply):
    line_bot_api.reply_message(reply, TextSendMessage(messege))
    regi_flag = False
    enter_flag = False

        

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'date':
        shift_data.append(event.postback.params['date'])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='出勤時間を入力してください',
                    actions=[
                        DatetimePickerAction(
                            label='出勤時間',
                            mode='time',
                            data='start',
                        ),
                        MessageAction(
                            label='提出をやめる',
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
                    text='退勤時間を入力してください',
                    actions=[
                        DatetimePickerAction(
                            label='退勤時間',
                            mode='time',
                            data='end',
                        ),
                        MessageAction(
                            label='提出をやめる',
                            text='終了'
                        )
                    ]   
                )
            )
        )
    elif event.postback.data == 'end':
        shift_data.append(event.postback.params['time'])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='もう一度お試しください',
                template=ConfirmTemplate(
                    text='続けてシフトを入力しますか？',
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
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('入力に失敗しました。「シフトを提出」と入力し、もう一度始めからお願いします。'))


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT'))