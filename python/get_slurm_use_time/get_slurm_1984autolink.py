#该文件主要实现将txt文件传入mysql数据库
import pymysql
import requests
import time
#import re
#变量初始化
con=pymysql.connect(
    host='sh.paas.sensetime.com',
    port=38152,
    user='kkcycanr',
    password='zwikygxd',
    db='parrots_env',
    charset="utf8"
    )
def webhook(status):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d21ecf50-e0ba-4a9f-b445-98f1f749347e'
    if status == 'success':
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": "<font color=#008000>集群获取autolink用户分区使用信息成功</font>"
            }
        }
    else:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": "<font color='warning'>集群获取autolink用户分区使用信息失败</font>"
            }
        }
    requests.post(url, json=data)
def insert(con,jobid,Reserved,RunGpuTime,State,Start,Partition,JobName,WorkID,modelzoo):
    #数据库游标！
    cue = con.cursor()
    # print("mysql connect succes")  # 测试语句，这在程序执行时非常有效的理解程序是否执行到这一步
    #try-except捕获执行异常
    try:
        cue.execute(
            "REPLACE INTO getSlurm_waittime_autolink (JobID,ReservedTime,RunGpuTime,State,Start,`Partition`,JobName,WorkID,modelzoo) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        [jobid,Reserved,RunGpuTime,State,Start,Partition,JobName,WorkID,modelzoo])
        #执行sql语句
        # print("insert success")  # 测试语句
    except Exception as e:
        print('Insert error:', e)
        con.rollback()
        #报错反馈
    else:
        con.commit()
        #真正的执行语句
def read(filename):
    #按行读取txt文本文档
    with open(filename, 'r') as f:
        datas = f.readlines()
    #遍历文件
    for data in datas:
        txt=data.split()
        #数据不全不统计
        if len(txt) != 7:
            continue
        jobid=txt[0]
        #jobid非全数字不统计
        if not jobid.isnumeric():
            continue
        day = 0
        Reserved=txt[1]
        if '-' in Reserved:
            day = Reserved.strip().split("-")[0]
            Reserved = Reserved.strip().split("-")[1]
        H, M, S = Reserved.strip().split(":")
        Reserved = int(day) * 86400 + int(H) * 3600 + int(M) * 60 + int(S)
        GPUTime=txt[2]
        AllocGPUS=txt[3]
        State=txt[4]
        #只统计成功任务
        if State != 'COMPLETED':
            continue
        Start=txt[5]
        JobName=txt[6]
        modelzoo = 0
        if 'modelzoo-one-iter' in JobName:
            modelzoo = jobid
        # print(jobid, Reserved, GPUTime, State, AllocGPUS,JobName )
        d = 0
        if '-' in GPUTime:
            d = GPUTime.strip().split("-")[0]
            GPUTime = GPUTime.strip().split("-")[1]
        h, m, s = GPUTime.strip().split(":")
        RunGpuTime = int(d) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
        Partition = 'GPU'
        if ':' in AllocGPUS:
            Partition = AllocGPUS.strip().split(":")[0]
            Partition_GRES = AllocGPUS.strip().split(":")[1]
            RunGpuTime = RunGpuTime * int(Partition_GRES)
        #nv集群GPUTime 是总时间，不需要再乘以gpu数量 ；mlu dcu 需要乘以gres数量
        # print(RunGpuTime)
        #没WorkID不统计
        if JobName[0].isdigit():
            WorkID = JobName.rsplit('_')[0]
            JobName = JobName.rsplit('_')[1]
        else:
            continue
        #exist=cue.execute("select * from id where id = %s",[id])
        #print(jobid, Reserved, RunGpuTime, State, JobName, WorkID)
        insert(con, jobid, Reserved, RunGpuTime, State, Start, Partition, JobName, WorkID, modelzoo)
        #调用insert方法
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(cur_time)
    print("date数据插入完成！")
if __name__ == '__main__':
    try:
        read("getSlurm_waittime_autolink.txt")
        read("getSlurm_waittime_autolink_mlu.txt")
        read("getSlurm_waittime_autolink_dcu.txt")
        con.close()
        webhook('success')
        #关闭连接
    except Exception as e:
        webhook('fail')
        print(e)

