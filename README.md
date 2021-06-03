# DATETIME data via LINE API to locacl(.xlsx) 

アルバイトなどのシフト希望調査に利用することを想定して制作しました。
利用者はラインのBOTアカウントに、事前に登録されたIDと日時情報を送信します。
管理者はWebサイトを訪問することで、それらのデータをエクセルでダウンロードできます。(ログイン機能は未実装)


# Requirement

* python-3.9.5
* Flask　2.0.1
* line-bot-sdk　1.19.0
* psycopg2　2.8.6
* XlsxWriter　1.4.3

database

shift_table
| num | id | date | start | last |
|:---|:---|:-----|:-----|:-----------|
| オートインクリメントのid | 社員番号などの入力されたID | 入力された日付 | 入力された出勤時間 | 入力された退勤時間 |


# Getting started
```
$ export　YOUR_CHANNEL_ACCESS_TOKEN　= LINE_CHANNEL_SECRET
$ export　YOUR_CHANNEL_SECRET = LINE_CHANNEL_ACCESS_TOKEN
$ export　DATABASE_URL =  YOUR_DATABASE_URL

$ pip install -r requirements.txt
```
and deploy

* https:// hoge＿url /callback  
をWebhook URLとして登録。

# Usage
環境変数として登録したLINEBOTアカウントに対し「シフトを提出」と入力すると、IDの入力、時間の入力が開始される。

* https:// hoge_url /  
にアクセスすることでエクセルファイルのダウンロードが開始される。
入力されたデータすべてが出力されるが、SQLを書き換えることで変更できる。


# Note
On the last sentence `app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT'))`  
`port=os.environ.get('PORT')` is not necessary if deploy by yourself.

It is only needed for heroku(PaaS).

# Reference
- flask: https://github.com/pallets/flask
- line messaging api reference: https://developers.line.biz/ja/docs/messaging-api/
- line bot sdk python: https://github.com/line/line-bot-sdk-python