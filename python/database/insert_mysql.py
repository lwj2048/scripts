# -*- coding: UTF-8 -*-
import pymysql
import source as source
"""
source.py文件内容示例如下：
data_info = [(2, 'HZ', '2018-09-19 14:55:21', u'2520.64'),
             (6, 'HZ', '2018-09-19 14:55:21', u'2694.92'),
             (9, 'HZ', '2018-09-19 14:55:21', u'2745.38')]
"""


mysql_host = '192.168.0.3'
port = 3306
mysql_user = 'root'
mysql_pwd = 'XXXX'
encoding = 'utf8'


#建立 连接mysql服务端

conn = pymysql.connect(
    host=mysql_host,  # mysql服务端ip
    port=port,  # mysql端口
    user=mysql_user,  # mysql 账号
    password=mysql_pwd,  # mysql服务端密码
    db='test',  # 操作的库
    charset=encoding  # 读取字符串编码

)

# 拿到游标对象
cursor = conn.cursor()

'''
游标是给mysql提交命令的接口
mysql>
把sql语句传递到这里
'''


# 前提最少有一个主键，记录在表中不存在则进行插入，如果存在则进行更新后面的name、number、build_time
sql = "INSERT INTO `id` VALUES (%s, %s, %s, %s) " \
          "ON DUPLICATE KEY UPDATE `name` = VALUES(`name`) ,`number` = VALUES(`number`) ,`build_time` = VALUES(`build_time`) "

#数据格式如下：
#添加的数据的格式必须为list[tuple(),tuple(),tuple()]或者tuple(tuple(),tuple(),tuple())



#批量插入使用executement
print(source.data_info)
cursor.executemany(sql, source.data_info)

# 想让insert 语句 插入数据库里面去需要加上这个
conn.commit()

# 执行完sql语句要关闭游标和mysql连接
cursor.close()
conn.close()