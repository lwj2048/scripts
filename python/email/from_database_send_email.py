import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pandas as pd
import mysql.connector

"""
数据库查询的数据，邮件发出。
"""
# 设置电子邮件的相关信息
host = 'partner.outlook.cn'
password = 'xxxxx'
from_address = "xxxxx.com"
to_address = "xxxxx@qq.com"
subject = "标题"
body = "Please see the attached table for a list of customer orders."

# 设置数据库连接信息
mydb = mysql.connector.connect(
    host="xxxxx.com",
    port="38152",
    user='github',
    password="GitHub123",
    database="GitHub",
    ssl_disabled=True
)

def get_table():
    # 从数据库中获取数据
    mycursor = mydb.cursor()
    mycursor.execute("SELECT num, time1, name FROM test")
    data = mycursor.fetchall()
    # 将数据转换为HTML表格
    df = pd.DataFrame(data, columns=["num", "time1", "name"])
    html_table = df.to_html(index=False)
    return html_table

def get_html(html_table):
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # 邮件的第一部分,即表格 就是 html_table

    # 添加邮件的第二部分，即本地图片
    with open('parrots.png', 'rb') as fp:
        img_data = fp.read()
    part2 = MIMEImage(img_data)
    part2.add_header('Content-ID', '<school.png>')
    msg.attach(part2)

    # 将图片嵌入HTML正文
    html = f"""
        <html>
          <head></head>
          <body>
            {html_table}
            <img src="cid:school.png">
          </body>
        </html>
    """
    #发送html
    # print(html)
    msg.attach(MIMEText(html, 'html'))
    print(msg)
    # 使用SMTP服务器发送电子邮件
    return msg

def send_email(msg):
    server = smtplib.SMTP(host, 587)
    server.starttls()
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()

if __name__ == "__main__":
    html_table = get_table()
    msg = get_html(html_table)
    send_email(msg)

