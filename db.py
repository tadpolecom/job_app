from flask import Flask, render_template, request, redirect, send_from_directory
import psycopg2
import os
import xlsxwriter


class shift:
    def __init__(self):
        self.get_connection = psycopg2.connect(os.environ.get('DATABASE_URL'))

    def insert(self, data):
        enter=[]
        for i in range(1,len(data)):
            enter.append([data[0],data[i+1],data[i+2],data[i+3]])

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO shift_table (id,date,start,last) VALUES (%s, %s, %s, %s)',data)
            conn.commit()

    def into_xlsx(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM member_tb', ('foo',))
                rows = cur.fetchall()
        print(rows)

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
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')