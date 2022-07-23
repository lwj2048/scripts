#!/bin/bash

<<'COMMENT'
CREATE TABLE `GetJobStatus` (
  `id` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `note` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `url` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `last_time` datetime DEFAULT NULL,
  `time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
COMMENT

#数据库信息
export MYSQL_PWD=Figure@321
username="root"
sql_Host=192.168.254.141
sql_Port=3306
database="test"
tableone="GetJobStatus"




usage()
{
  cat <<EOF
  -h,--help          Show help
  -s,--status        工具执行的结果success或fail
  -i,--id            工具名称
  -n,--note          频率及说明
  -u,--url           工具位置，例如：http://10.10.36.34:8080/job/test/


使用示例：
bash $0 -i test_job -n 每个工作日，获取集群使用信息 -u http://10.10.36.34:8080/job/test/ -s success


EOF
}

while true; do
  case $1 in
    -h|--help)
        usage
        exit 1
      ;;
    -s|--status)
        status="${2}"
        shift 2
      ;;
    -n|--note)
        note="${2}"
        shift 2
      ;;
    -i|--id)
        id="${2}"
        shift 2
      ;;
    -u|--url)
        url="${2}"
        shift 2
      ;;

    --)
        shift
        break
      ;;
    *)
        break
      ;;
    esac
done


select_sql=`mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "select * from $tableone WHERE id='$id'  "`

if [ ! -n "$select_sql" ];then
   echo "插入数据"
   mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "INSERT INTO $tableone  (id,status,note,url,time)VALUES('$id','$status','$note','$url','$(date "+%Y-%m-%d %H:%M:%S")')"
else
   echo "修改数据"
   time_last_date=`mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "select time from $tableone WHERE id='$id'  "`
   last_time=`echo ${time_last_date:5:19}`
   mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "UPDATE $tableone SET id='$id' ,note='$note' ,status='$status' ,url='$url' ,last_time='$last_time',time='$(date "+%Y-%m-%d %H:%M:%S")'  WHERE id='$id'"

fi



