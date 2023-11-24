#!/bin/bash
#获取经过eth 且访问主机8080端口的流量信息
eth='ens33'
while true
do
    # 获取当前日期
    current_date=$(date +%Y-%m-%d)

    # 定义日志文件名
    log_file="port_8080_traffic_$current_date.log"

    # 删除两天前的日志文件
    find . -type f -name "port_8080_traffic_*.log" -mtime +2 -exec rm {} \;

    # 开始监控端口 5700，并将日志保存到当前日期的日志文件中
    sudo tcpdump -i ${eth} -A 'port 8080' > $log_file &

    # 获取 tcpdump 的进程 ID
    tcpdump_pid=$!

    # 等待一天
    sleep 86400

    # 结束 tcpdump 进程
    kill $tcpdump_pid
done
