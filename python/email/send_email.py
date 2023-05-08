# smtp =>simple mail transfer protocol  简单邮件传输协议
import smtplib
import email  # 文件名不可以和引入的库同名
from email.mime.image import MIMEImage  # 图片类型邮件
from email.mime.text import MIMEText  # MIME 多用于邮件扩充协议
from email.mime.multipart import MIMEMultipart  # 创建附件类型
import re


HOST = 'smtp.qq.com'  # 调用的邮箱借借口
SUBJECT = '发送了一封测试邮件'  # 设置邮件标题
FROM = '6021xxxxx@qq.com'  # 发件人的邮箱需先设置开启smtp协议
TO = 'xiao21xxxx@qq.com'  # 设置收件人的邮箱（可以一次发给多个人,用逗号分隔）
message = MIMEMultipart('related')  # 邮件信息，内容为空  #相当于信封##related表示使用内嵌资源的形式，将邮件发送给对方

HTML_TOP = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>文档标题</title>
</head>
<body>
	<h1 align="center">运维月度信息统计</h1>
    <h2 align="center">date</h2>
  <table border="1">
  <tr>
    <td colspan="9" align="center" height="100px" ><strong>xxxParrots CI WorkFlow信息</strong></td>
  </tr>
  <tr>
    <td colspan="9">
      <img src="cid:small" alt="dns配置">
    </td>
  </tr>
  <tr>
    <td colspan="9" align="center" height="200px" ><strong>xxxParrots CI job 汇总</strong></td>
  </tr>
  <tr>
    <td colspan="9">
      <img src="cid:small" alt="dns配置">
    </td>
  </tr>
     <tr>
    <td colspan="9" align="center" height="200px" ><strong>运维任务统计</strong></td>
  </tr>


"""


TABLE_TMPL = """      
  <tr>
    <td >2023-2-1至2023-2-28</td>
    <td >新增</td>
    <td >1</td>
    <td >2</td>
    <td >3</td>
    <td >0</td>
    <td >2</td>
    <td >6</td>
    <td >8</td>
  </tr> 
  """
HTML_BOTTOM = """
</table>
</body>
</html>
"""


def sendmail(HOST, SUBJECT,FROM,TO,message):
    """
    发送邮件主体到对方邮箱
    :发送信息参数说明:
    1.内容必须是字符串
    2.内容形式，文本类型默认为plain
    3.内容编码使用utf-8
    :其他：
    图片和excel文件需要和本脚本一个目录下
    """

    # ===========发送信息内容=============
    #替换时间文本
    HTML1 = re.sub('date', '2023-2-1至2025-2-28',HTML_TOP)
    HTML = HTML1 + TABLE_TMPL + HTML_BOTTOM
    message_html = MIMEText(HTML, 'html', 'utf-8')
    message.attach(message_html)
    # ===========发送图片-=============
    #发送图片-预览信息
    image_data = open('../../../../monthly/get_web_matebase/examplemetabase.png', 'rb')
    message_image = MIMEImage(image_data.read())
    image_data.close()# 关闭刚才打开的文件
    message_image.add_header('Content-ID', 'small')
    message.attach(message_image)# 添加图片文件到邮件信息中去

    #发送图片-附件
    message_image = MIMEText(open('../../../../monthly/get_web_matebase/examplemetabase.png', 'rb').read(), 'base64', 'utf-8')
    message_image['Content-disposition'] = 'attachment;filename="1234.png"'# 设置图片在附件当中的名字
    message.attach(message_image)# 添加图片文件到邮件-附件中去
    # ===========发送excel-附件=============
    # message_xlsx = MIMEText(open('556677.xlsx', 'rb').read(), 'base64', 'utf-8')# 将xlsx文件作为内容发送到对方的邮箱读取excel，rb形式读取，对于MIMEText()来说默认的编码形式是base64 对于二进制文件来说没有设置base64，会出现乱码
    # message_xlsx['Content-Disposition'] = 'attachment;filename="email_demo_change.xlsx"'# 设置文件在附件当中的名字
    # message.attach(message_xlsx)# 添加excel文件到邮件-附件中去

    # ===========配置相关-=============
    message['From'] = FROM # 设置邮件发件人
    message['TO'] = TO # 设置邮件收件人
    message['Subject'] = SUBJECT # 设置邮件标题
    email_client = smtplib.SMTP_SSL(HOST)# 获取江建有奖传输协议证书
    email_client.connect(HOST, '465')# 设置发送域名，端口465
    result = email_client.login(FROM, 'czjmyqyluhwhbcfa')  # qq授权码
    print('登录结果', result)

    # ===========操作=============
    email_client.sendmail(from_addr=FROM, to_addrs=TO.split(','), msg=message.as_string()) #发送邮件指令
    email_client.close()# 关闭邮件发送客户端

if __name__ == '__main__':
    sendmail(HOST=HOST, SUBJECT=SUBJECT,FROM=FROM,TO=TO,message=message)