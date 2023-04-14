import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mysql.connector

"""
可以实现html模板发送邮件，只需要替换掉模板里的占位符即可
可文本，可图片
"""

host = 'partner.outlook.cn'
password = 'xxxxx'
from_address = "xxxxx.com"
to_address = "xxxxx@qq.com"
subject = "标题"
body = "Please see the attached table for a list of customer orders."

# 从数据库中查询数值
mydb = mysql.connector.connect(
    host="xxxxx.com",
    port="38152",
    user='github',
    password="GitHub123",
    database="GitHub",
    ssl_disabled=True
)

def get_info():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT COUNT(*) FROM test")
    result = mycursor.fetchone()
    num_students = result[0]
    return num_students

def replace_html(name_value,age_value,grade_value):
    # 打开HTML模板文件，并将数据库查询到的数据替换掉占位符，所有的占位符需要一次替换掉
    html = html_template.format(name=name_value, age=age_value, grade=grade_value)
    print(html)
    return html

def get_msg(html):
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # 将HTML正文添加到邮件中
    part = MIMEText(html, 'html')
    msg.attach(part)

    #替换占位符图片
    with open('parrots.png', 'rb') as fp:
        img_data = fp.read()
    part2 = MIMEImage(img_data)
    part2.add_header('Content-ID', '<parrots.png>')
    msg.attach(part2)
    return msg

def send_email(msg):
    server = smtplib.SMTP(host, 587)
    server.starttls()
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()



if __name__ == "__main__":
    with open('replace_html_send_email.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
    name_value = 'li'
    grade_value = '男'
    age_value = get_info()
    html = replace_html(name_value,age_value,grade_value)
    msg = get_msg(html)
    send_email(msg)
