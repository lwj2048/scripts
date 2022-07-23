#!/bin/bash




usage()
{
  cat <<EOF
  -h,--help          Show help
  -r,--result        工具执行的结果success或fail或runing
  -j,--job           工具名称
  -e,--env           环境名
  -c,--cluster       集群信息
  -m,--mmcv_version  mmcv版本(仅用于deploy_mmcv)
  -D,--DEPLOYTYPE    mmcvn部署位置(仅用于deploy_mmcv)

使用示例：
$0 -j ALL_GML -r success -e pat20220428
$0 -j deploy_mmcv -r success -c BJ15 -e pat20220428 -m 1.4.6 -D out_env
$0 -j deploy_pytorch -r success -c BJ15 -e v1.7.0
EOF
}

while true; do
  case $1 in
    -h|--help)
        usage
        exit 1
      ;;
    -r|--result)
        result="${2}"
        shift 2
      ;;
    -c|--cluster)
        cluster="${2}"
        shift 2
      ;;
    -j|--job)
        job="${2}"
        shift 2
      ;;
    -e|--env)
        env="${2}"
        shift 2
      ;;
    -m|--mmcv_version)
        mmcv_version="${2}"
        shift 2
      ;;
    -D|--DEPLOYTYPE)
        DEPLOYTYPE="${2}"
        shift 2
      ;;
    *)
        break
      ;;
    esac
done

if [ $job == 'ALL_GML' ] || [ $job == 'more_GML' ];then
   tableone="auto001_deploygml"
   envname="gmltag"
elif [ $job == 'All_Parrots_RC' ] || [ $job == 'parrots' ] || [ $job == 'ALL_parrots_week' ] || [ $job == 'parrots_new' ];then
   tableone="auto001_deployparrots"
   envname="parrotstag"
elif [ $job == 'deploy_mmcv' ];then
   tableone="auto001_deploymmcv"
   envname="envname"
elif [ $job == 'deploy_pytorch' ];then
   tableone="auto001_deploypytorch"
   envname="pytorchtag"
else
   echo "未能识别此job ${job}"
fi

#数据库信息
export MYSQL_PWD=`dc -e 252230791858610079356682P`
username="wugeshui"
sql_Host="sh.paas.sensetime.com"
sql_Port=38152
database="opsauto"


if [ $job == 'deploy_mmcv' ];then

     mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "UPDATE $tableone SET result='$result',updatetime='$(date "+%Y-%m-%d %H:%M:%S")'  WHERE mmcvtag like '$mmcv_version' and cluster='$cluster' and $envname='$env' and deploytype='$DEPLOYTYPE' and result='触发成功'"
elif [ $job == 'deploy_pytorch' ];then

     mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "UPDATE $tableone SET result='$result',updatetime='$(date "+%Y-%m-%d %H:%M:%S")'  WHERE $envname='$env' and cluster='$cluster' "
else
     select_sql=`mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "select * from $tableone WHERE $envname='$env'  "`

    if [ ! -n "$select_sql" ];then
       echo "${database} 数据库 ${tableone} 表中没有 ${env}环境信息"
    else
       echo "修改部署结果"
       mysql -P$sql_Port -h$sql_Host -u$username  --local-infile  $database -e "UPDATE $tableone SET result='$result',updatetime='$(date "+%Y-%m-%d %H:%M:%S")' WHERE $envname='$env' "

    fi

fi
