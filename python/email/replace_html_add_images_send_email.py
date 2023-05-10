import asyncio
from PIL import Image
from pyppeteer import launch
import shutil,time
import smtplib,requests
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime
import calendar

#邮件发出如replace_html_add_images_send_email.png示例

def webhook(status):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx'
    if status == 'success':
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": "<font color=#008000>test 月度信息发送成功</font>"
            }
        }
    else:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": "<font color='warning'>test 月度信息发送失败</font>"
            }
        }
    requests.post(url, json=data)
def cutimages(img_path):
    imgs = Image.open(img_path)
    width, height = imgs.size
    # 按比例缩小
    imgs.thumbnail((width / 3 * 2 , height / 3 * 2))
    imgs.save(img_path, 'png')
async def grafana():
    url = 'http://grafana.parrots.xxxx.com/d/K6u5DqJ4z/6L-Q57u05pyI5bqm5L-h5oGv57uf6K6h?orgId=1'
    userDataDir = '/home/platform_ci/Monthly/get_web_grafana'
    img_path = '/home/platform_ci/Monthly/get_web_grafana/grafana_1.png'
    img_path2 = '/home/platform_ci/Monthly/get_web_grafana/grafana_2.png'
    browser = await launch({'args': ['--no-sandbox'],'userDataDir':userDataDir})
    try:
        shutil.rmtree(userDataDir)
        page = await browser.newPage()  # 创建一个新的空白窗口
        # 设置网页显示尺寸
        await page.setViewport({'width': 1920, 'height': 1470})  # 设置内部窗口大小
        await page.goto(url, {"timeout": 14 * 60000})
        await page.waitFor(500)
        await page.type('input[name=user]', 'viewer')
        await page.waitFor(300)
        await page.type('input[name=password]', 'viewer')
        await page.waitFor(300)
        await page.click('button[class=css-8csoim-button]')
        await page.waitFor(15000)
        await page.screenshot({'path': img_path, 'clip': {'x': 78, 'y': 60, 'width': 1830, 'height': 683}})
        await page.screenshot({'path': img_path2, 'clip': {'x': 78, 'y': 743, 'width': 1830, 'height': 683}})
        await page.waitFor(300)
        cutimages(img_path)
        cutimages(img_path2)
    finally:
        await browser.close()

async def metabase():
    url = "http://dashboard.parrots.xxx.com/dashboard/56"
    userDataDir = '/home/platform_ci/Monthly/get_web_matebase'
    img_path = "/home/platform_ci/Monthly/get_web_matebase/examplemetabase.png"
    browser = await launch({'args': ['--no-sandbox'], 'userDataDir': userDataDir})
    user_name = 'xxx'
    pass_word = 'xxx'
    try:
        shutil.rmtree(userDataDir)
        page = await browser.newPage()  # 创建一个新的空白窗口
        # 设置网页显示尺寸
        await page.setViewport({'width': 1920, 'height': 1170})  # 设置内部窗口大小
        await page.goto(url, {"timeout": 14 * 60000})
        await page.waitFor(500)
        await page.type('input[name=username]', user_name)
        await page.waitFor(300)
        await page.type('input[name=password]', pass_word)
        await page.waitFor(300)
        await page.click('div.layout-centered')
        await page.waitFor(10000)
        await page.screenshot({'path': img_path, 'clip': {'x': 30, 'y': 207, 'width': 1860, 'height': 509}})
        cutimages(img_path)
    finally:
        await browser.close()

def sendMail(title,emailto,emailcc,date):
    host = 'partner.outlook.cn'
    sender = 'xxx.com'
    user = 'xxx.com'
    password = 'xxxxxxx'
    to = [emailto]
    cc = [emailcc]
    subject = title

    sendObj = smtplib.SMTP(host, 587)
    sendObj.connect(host, 587)
    #sendObj.set_debuglevel(1)  # 打印debug日志
    #print(sendObj)  # ok 了
    # 2. 跟服务器建立连接
    sendObj.ehlo()
    sendObj.starttls()
    msg = MIMEMultipart('related')
    msg['Subject'] = Header(subject, 'utf-8').encode()
    msg['From'] = sender
    msg['To'] = to[0]
    msg['Cc'] = cc[0]
    # 读取html文件内容
    f = open('replace_html_add_images_send_email.html', 'r', encoding='utf-8')
    mail_body = f.read()
    f.close()

    #替换HTML中头部时间文本
    date_to_replace = '${date}'
    mail_body = mail_body.replace(date_to_replace, date)

    # 01. 添加文本
    msgText = MIMEText(mail_body, _subtype='html', _charset='utf-8')
    msg.attach(msgText)

    #添加 CI图片
    file = open("get_web_grafana/grafana_1.png", "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'DeeplinkGrafana')
    msg.attach(img)
    file = open("get_web_grafana/grafana_2.png", "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'Grafana')
    msg.attach(img)
    #添加matebase 图片
    file = open("get_web_matebase/examplemetabase.png", "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'metabase')
    msg.attach(img)

    print('Logging with server...')


    sendObj.login(user, password)
    sendObj.sendmail(sender, to[0].split(",")+cc[0].split(","), msg.as_string())
    sendObj.quit()
    print('Email has been sent')

def get_date():
    today = datetime.date.today()
    # 获取上个月的年份和月份
    last_month = today.replace(day=1) - datetime.timedelta(days=1)
    year = last_month.year
    month = last_month.month
    # 获取上个月的最后一天的日期
    _, last_day = calendar.monthrange(year, month)
    begin_day = datetime.date(year, month, 1)
    end_day = datetime.date(year, month, last_day)
    date = str(begin_day) + ' 至 ' + str(end_day)
    return date


if __name__ == '__main__':
    try:
        loop_grafana = asyncio.get_event_loop()
        loop_grafana.run_until_complete(grafana())

        loop_metabase = asyncio.get_event_loop()
        loop_metabase.run_until_complete(metabase())
        emailto = "xxxx@qq.com"
        emailcc = "xxx@qq.com,xxx2@qq.com"
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = "当前时间：" + cur_time
        date = get_date()
        sendMail("运维月报", emailto, emailcc, date)
        webhook('success')
    except Exception as e:
        webhook('fail')
        print(e)