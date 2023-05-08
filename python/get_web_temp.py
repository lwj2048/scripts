import os
import asyncio
from pyppeteer import launch


async def save_image(url, img_path):
    """
    导出图片
    :param url: 在线网页的url
    :param img_path: 图片存放位置
    :return:
    """
    browser = await launch()
    page = await browser.newPage()
    # 加载指定的网页url
    await page.goto(url)
    # 设置网页显示尺寸
    await page.setViewport({'width': 1920, 'height': 1080})
    '''
    path: 图片存放位置
    clip: 位置与图片尺寸信息
        x: 网页截图的x坐标
        y: 网页截图的y坐标
        width: 图片宽度
        height: 图片高度
    '''
    await page.screenshot({'path': img_path, 'clip': {'x': 20, 'y': 700, 'width': 730, 'height': 2600}})
    await browser.close()


if __name__ == '__main__':
    url = "https://blog.csdn.net/Longyu_wlz/article/details/108550528"
    img_path = os.path.join(os.getcwd(), "../../../monthly/get_web_matebase/examplemetabase.png")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(save_image(url, img_path))
