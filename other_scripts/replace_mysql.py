#该文件主要实现将txt文件传入mysql数据库
import pymysql
import re
"""
test.txt文件内容示例如下：
1,1,1,1
1,1,1,2
1,1,2,1
1,1,2,2
"""
#变量初始化
con=pymysql.connect(
    host='192.168.0.3',
    port=3306,
    user='root',
    password='XXXX',
    db='test',
    charset="utf8"
    )
def delete(con):
    cue = con.cursor()
    cue.execute(
        "truncate table id"
        #清空表语句
    )
def insert(con,id,name,number,build_time):
    #数据库游标！
    cue = con.cursor()
    # print("mysql connect succes")  # 测试语句，这在程序执行时非常有效的理解程序是否执行到这一步
    #try-except捕获执行异常
    try:
        cue.execute(
            #"insert into id (id,name,number,build_time) values(%s,%s,%s,%s)",
            "REPLACE INTO id (id,name,number,build_time) values(%s,%s,%s,%s)",
        [id,name,number,build_time,])
        #执行sql语句
        # print("insert success")  # 测试语句
    except Exception as e:
        print('Insert error:', e)
        con.rollback()
        #报错反馈
    else:
        con.commit()
        #真正的执行语句
def read():
    #delete(con) 可清空表后重新写入
    filename=r'test.txt'
    #按行读取txt文本文档
    with open(filename, 'r') as f:
        datas = f.readlines()
    #遍历文件
    for data in datas:
        txt=re.split(r'[;,\s]',data)
        id=txt[0]
        name=txt[1]
        number=txt[2]
        build_time=txt[3]
        #exist=cue.execute("select * from id where id = %s",[id])
        insert(con, id, name, number, build_time)
        #调用insert方法
    print("数据插入完成！")
read()
#执行read函数
con.close()
#关闭连接