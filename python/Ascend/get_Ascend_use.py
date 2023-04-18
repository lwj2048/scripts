#!/usr/bin/python
import time
import json
import requests
import pymysql

def webhook(info):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d21ecf50-e0ba-4a9f-b445-98f1f749347e'
    data = {
        'msgtype': 'text',
        'text': {'content': info,
        }
    }
    requests.post(url, json=data)

def queryUsage(address, expr):
    url = address + '/api/v1/query?query=' + expr
    try:

        return json.loads(requests.get(url=url).content.decode('utf8', 'ignore'))
    except Exception as e:
        print(e)
        return {}


def insert_Mysql(npu_name,gather_time,gather_use_time):
    #数据库字段 DATE(date),NPU_NAME(varchar),USE_TIME(int)
    gather_time = gather_time.split('_')[0]
    print(gather_time)
    db = pymysql.connect(host='数据库地址', user='kkcycanr', password='zwikygxd', charset='utf8',
                          db='parrots_env', port=38152)

    SELECT_sql = "SELECT USE_TIME  FROM  Ascend_npu_use_time WHERE DATE = '%s' " % (gather_time,)
    INSERT_sql = "INSERT INTO Ascend_npu_use_time(DATE,NPU_NAME,USE_TIME) VALUES ('%s', '%s', %s)" %(gather_time,npu_name,gather_use_time)
    cursor = db.cursor()
    try:
        cursor.execute(SELECT_sql)
        print(gather_use_time)
        gather_use_time_source = cursor.fetchone()[0]
        gather_use_time = gather_use_time + gather_use_time_source
        print(gather_use_time)
        UPDATE_sql = "UPDATE Ascend_npu_use_time SET USE_TIME = '%s' WHERE DATE = '%s' " % (gather_use_time,gather_time)
        cursor.execute(UPDATE_sql)
    except Exception as e:
        cursor.execute(INSERT_sql)
    db.commit()

def getCurrentUsageGreater(address, record ,gather_use_time):

    expr = record
    usage = queryUsage(address=address, expr=expr)
    for i in usage['data']['result']:
        print(i)
        # if i['metric']['job'] == 'kmaster':
        #     print(i['metric'],i['value'])
        # for item in i:
        #     print(item)
            # if 'kmaster' in str(item):
            #     print(item)
         #print(i)
        # if i['value'][1] == '0':
        #     gather_use_time += 1
    return gather_use_time



if __name__ == '__main__':
    # 定义采集时间间隔 s
    monitorInterval = 10
    # 定义Prometheus地址
    address = "http://ci.parrots.xxxx.com:8002"
    #address = "http://10.118.253.11:30003"
    #初次运行时间
    gather_time = time.strftime('%Y-%m-%d_%H', time.localtime())
    #gather_time = '2023-01-09_10'
    #初始化npu使用时间为0
    gather_use_time = 0
    while True:
        # 判断时间是否改变
        if gather_time == time.strftime('%Y-%m-%d_%H', time.localtime()):
            # 时间不变，继续累增
            try:
                gather_use_time = getCurrentUsageGreater(address, 'npu_chip_info_utilization', gather_use_time)
            except Exception as e:
                print(e)
            time.sleep(monitorInterval)
        else:
            # 时间改变，插入数据库操作
            try:
                #insert_Mysql("Ascend",gather_time,gather_use_time)
                gather_time = time.strftime('%Y-%m-%d_%H', time.localtime())
                gather_use_time = 0
            except Exception as e:
                print(e)
