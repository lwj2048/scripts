#!/bin/bash

usage()
{
  cat <<EOF
  -h,--help          Show help
  -r,--result        *工具执行的结果success 或 fail
  -j,--job           *job名称 目前支持 ALL_GML、All_Parrots_RC、ALL_parrots_week、more_GML、parrots、parrots_new、deploy_mmcv、deploy_pytorch
  -c,--cluster       集群信息
  -e,--env           *环境名
  -m,--mmcv_version  mmcv版本(仅用于deploy_mmcv)
  -D,--DEPLOYTYPE    mmcvn部署位置(仅用于deploy_mmcv)
  -U,--USERNAME      部署人

回写job执行结果
使用示例：
 $0 -j ALL_GML -e pat20220428
 $0 -j All_Parrots_RC -e pat20220428
 $0 -j ALL_parrots_week -e pat20220428
 $0 -j more_GML -r success -c BJ15 -e pat20220428 -U liwenjian
 $0 -j parrots -r success -c BJ15 -e pat20220428 -U liwenjian
 $0 -j parrots_new -r success -c BJ15 -e pat20220428 -U liwenjian
 $0 -j deploy_mmcv -r success -c BJ15 -e pat20220428 -m 1.4.6 -D out_env
 $0 -j deploy_pytorch -r success -c BJ15 -e v1.7.0 -U liwenjian
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
    -U|--USERNAME)
        USERNAME="${2}"
        shift 2
      ;;
    *)
        break
      ;;
    esac
done


conf="/var/lib/jenkins/wgs-shell/deploy_cluster.conf"
update_database_result="/home/platform_ci/auto_deploy/pboot/update_database_result.sh"
GML_emailcontent="
GML 部署
部署版本：${env}
部署用户：${USERNAME}
部署结果：已完成
"
parrots_emailcontent="
parrots 部署
部署版本: ${env}
部署用户：${USERNAME}
部署结果：已完成
"
pytorch_emailcontent="
pytorch 部署
部署版本: ${env}
部署集群: ${cluster}
部署用户：${USERNAME}
部署结果：已完成
"

parrots_week_cluster_info_tmp=`cat /var/lib/jenkins/wgs-shell/weekpatdeps_envname.config |sed '1d' |sed 's/:"pat[0-9].*//g'| xargs`
parrots_week_cluster_info="(${parrots_week_cluster_info_tmp})"



if [ $job == 'ALL_GML' ];then
    sh $update_database_result -j more_GML -r "runing" -e $env


elif [ $job == 'All_Parrots_RC' ];then
    sh $update_database_result -j parrots -r "runing" -e $env

elif [ $job == 'ALL_parrots_week' ];then
    sed -i '/parrots_week_cluster/d' $conf
    echo parrots_week_cluster=$parrots_week_cluster_info >>$conf
    sh $update_database_result -j parrots_new -r "runing" -e $env

elif [ $job == 'more_GML' ];then
#    if [ $result == 'fail' ];then
#        sh $update_database_result -j more_GML -r fail -e $env

#    elif [ $result == 'success' ];then
    if [ $result == 'success' ];then
        line=`awk '/gml_cluster/{print NR}'  $conf `
        sed -i " ${line}s/${cluster}//g" $conf
        source $conf
        if [ ! -n "$gml_cluster" ];then
            sh $update_database_result -j more_GML -r success -e $env
            /usr/bin/python3.6 /var/lib/jenkins/wgs-shell/email_notice.py "${GML_emailcontent}" "${USERNAME}"
        fi
    fi

elif [ $job == 'parrots' ];then
#    if [ $result == 'fail' ];then
#        sh $update_database_result -j parrots -r fail -e $env

#    elif [ $result == 'success' ];then
    if [ $result == 'success' ];then
        line=`awk '/parrots_rc_cluster/{print NR}'  $conf `
        sed -i " ${line}s/${cluster}//g" $conf
        source $conf
        if [ ! -n "$parrots_rc_cluster" ];then
            sh $update_database_result -j parrots -r success -e $env
            /usr/bin/python3.6 /var/lib/jenkins/wgs-shell/email_notice.py "${parrots_emailcontent}" "${USERNAME}"
        fi
    fi
elif [ $job == 'parrots_new' ];then
#    if [ $result == 'fail' ];then
#        sh $update_database_result -j parrots_new -r fail -e $env

#    elif [ $result == 'success' ];then
    if [ $result == 'success' ];then
        line=`awk '/parrots_week_cluster/{print NR}'  $conf `
        sed -i " ${line}s/${cluster}//g" $conf
        source $conf
        if [ ! -n "$parrots_week_cluster" ];then
            sh $update_database_result -j parrots_new -r success -e $env
            /usr/bin/python3.6 /var/lib/jenkins/wgs-shell/email_notice.py "${parrots_emailcontent}" "${USERNAME}"
        fi
    fi

elif [ $job == 'deploy_mmcv' ];then
    sh $update_database_result -j deploy_mmcv -r success -c $cluster -e $env -m $mmcv_version -D $DEPLOYTYPE
#mmcv邮件由job触发
elif [ $job == 'deploy_pytorch' ];then
    sh $update_database_result -j deploy_pytorch -r success -c $cluster -e $env
    /usr/bin/python3.6 /var/lib/jenkins/wgs-shell/email_notice.py "${pytorch_emailcontent}" "${USERNAME}"
fi