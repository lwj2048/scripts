#!/usr/bin/python3
import time, os,sys
import smtplib,subprocess,io
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


TABLE_TMPL = """ 
 <tr class='failClass warning' align="left">
        <td align="left">%(label)s</td>
        <td align="left"><pre>%(title)s</pre></td>
        <td align="left"><pre>%(sum)s</pre></td>
    </tr>
"""

def sendMail(title,emailto,emailcc):
    host = 'partner.outlook.cn'
    sender = 'research.platformci@xxxx.com'
    user = r'research.platformci@xxxx.com'
    password = 'CmWR$pdOstQNv6wloAAQ'
    to = [emailto]
    cc = [emailcc]
    subject = title

    sendObj = smtplib.SMTP(host, 587)
    sendObj.connect(host, 587)
    sendObj.set_debuglevel(1)  # 打印debug日志
    print(sendObj)  # ok 了
    # 2. 跟服务器建立连接
    sendObj.ehlo()

    sendObj.starttls()

    msg = MIMEMultipart('related')
    msg['Subject'] = Header(subject, 'utf-8').encode()
    msg['From'] = sender
    msg['To'] = to[0]
    msg['Cc'] = cc[0]

    # 读取html文件内容
    f = open('D:\python\/test\send_mail.html', 'r', encoding='utf-8')
    mail_body = f.read()
    f.close()
    # 01. 添加文本
    msgText = MIMEText(mail_body, _subtype='html', _charset='utf-8')
    msg.attach(msgText)

    #添加SenseParrots CI图片
    file = open("D:\python\/test\get_web_grafana\examplegrafana.png", "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'Grafana')
    msg.attach(img)
    #添加matebase 图片
    file = open("D:\python\/test\matebase1.png", "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'metabase')
    msg.attach(img)
    label = '研发需求'
    title = 'test'
    sum = 5
    table_td = TABLE_TMPL % dict(label=label, title=title, sum=sum)
    msg = msg % dict(table_tr = table_td)
    # output = html.HTML_TMPL % dict(table_tr=table_tr0, value=value)
    print('Logging with server...')


    sendObj.login(user, password)
    sendObj.sendmail(sender, to[0].split(",")+cc[0].split(","), msg.as_string())
    sendObj.quit()
    print('Email has been sent')

if __name__ == '__main__':
    # content,user=sys.argv[1:3]
    # emailto = user + "@xxxx.com"
    emailto="liwenjian.vendor@xxxx.com"
    emailcc="liwenjian.vendor@xxxx.com"
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    value="当前时间："+cur_time
    sendMail("运维月报",emailto,emailcc)
