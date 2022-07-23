#!/bin/bash
# usage: curl -s https://git.oschina.net/haide1014/linux-script-init/raw/master/main.sh | bash -

# user: pengll
# mail: ...


# 脚本初始化
dir_init=/tmp/haide1014_init
[[ ! -d $dir_init ]] && mkdir $dir_init
time_Y=$(date +%Y)
time_m=$(date +%m)
time_d=$(date +%d)
time_H=$(date +%H)
time_M=$(date +%M)
time_S=$(date +%S)
time_full=$time_Y-$time_m$time_d-$time_H$time_M$time_S
# echo 当前时间: $time_full

# 判断当前路径
function get_current_path(){
    path1=$(dirname $0)
    first_char=$(echo ${path1:0:1})
    if [[ $first_char == '/' ]]; then
        CURRENT_PATH=$PATH1
    elif [[ $path1 == '.' ]]; then              # 省略了后面的代码,可能比较难理解,但为了代码的整洁,所以省略掉elif [[ $first_char == '.' ]]; then
        CURRENT_PATH=$PWD
    else
        CURRENT_PATH=${PWD}${path1:1}           # 去除掉多余的 .
    fi
}
get_current_path
# 严格分析,应该有三种情况
# 1. 绝对路径
# 2. 相对路径,脚本就在当前目录
# 3. 相对路径,脚本在当前目录的上一级目录






# 一个下载示例
# https://git.oschina.net/haide1014/linux-script-init/raw/master/resources/pypi/install.sh
url_project='https://git.oschina.net/haide1014/linux-script-init'
url_project_master="$url_project/raw/master"
url_resource="$url_project_master/resources"

# 加载依赖脚本
# source $CURRENT_PATH/main/get_facts/get_system.sh
# curl -s $url_project_master/main/get_facts/get_system.sh | bash -
# 获取发行版信息
function get_dist(){
    ls /etc | grep 'centos-release' >/dev/null 2>&1
    result=$(echo $?)
    if [[ $result == 0 ]]; then
        dist='CentOS'
    else
        dist='Unknow'
    fi
}
get_dist

# 获取CentOS版本信息
function get_centos_version(){
    centos_version=$(cat /etc/centos-release | grep -oP "\d{1,2}\.\d{1,2}")         # 获取详细版本，例如: 6.6   7.3
    centos_version_main=$(echo $centos_version | awk -F . '{print $1}')             # 获取主版本，例如: 6   7
    # echo $centos_version $centos_version_main
}


case $dist in
CentOS)
    get_centos_version
    dist_version=$centos_version
    ;;
*)
esac

# 获取架构信息  暂时不区分 amd64 ia64之类的
function get_arch(){
    getconf LONG_BIT | grep '64' >/dev/null 2>&1
    result=$(echo $?)
    if [[ $result == 0 ]]; then
        arch='64'
    else
        arch='32'
    fi    
}
get_arch


# 留作备份
function set_hostname(){
    var_hostname='xxx-ip-xxx'
    hostname $var_hostname      # 临时生效，退出会话再登陆有效，一重启就失效。
    if  [[ $centos_version_main == "7" ]]; then
        echo $var_hostname > /etc/hostname
    elif  [[ $centos_version_main == "6" ]]; then
        sed -i "/^HOSTNAME=/ c\HOSTNAME=$var_hostname" /etc/sysconfig/network  # centos6
    fi
}



# 设置主源(Base源 + epel源 + docker源 + mysql源)
function set_source_centos(){
    if  [[ $centos_version_main == "7" ]]; then
        # Base源
        # curl -s -o /etc/yum.repos.d/CentOS-Base.repo $url_resource/repos/centos/7/CentOS-Base_ustc.repo
        curl -s -o /etc/yum.repos.d/CentOS-Base.repo $url_resource/repos/centos/7/CentOS-Base_tuna.repo
        # curl -s -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
        # epel源
        yum install -y epel-release
        curl -s -o /etc/yum.repos.d/epel.repo $url_resource/repos/epel/7/epel_tuna.repo
        # curl -s -o /etc/yum.repos.d/epel.repo $url_resource/repos/epel/7/epel_aliyun.repo
        # 以下为科大源
        # sed -e 's!^mirrorlist=!#mirrorlist=!g' \
        #     -e 's!^#baseurl=!baseurl=!g' \
        #     -e 's!//download\.fedoraproject\.org/pub!//mirrors.ustc.edu.cn!g' \
        #     -e 's!http://mirrors\.ustc!https://mirrors.ustc!g' \
        #     -i /etc/yum.repos.d/epel.repo /etc/yum.repos.d/epel-testing.repo 
        # 阿里云源
        # curl -s -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
        # docker源
        # curl -s -o /etc/yum.repos.d/docker.repo $url_resource/repos/docker/7/docker_ustc.repo
        # mysql源，临时屏蔽，科大源又出问题了。
        # rpm -Uvh https://mirrors.ustc.edu.cn/mysql-repo/yum/mysql-5.7-community/el/7/x86_64/mysql-community-release-el7-7.noarch.rpm
        # curl -s -o /etc/yum.repos.d/mysql-community.repo $url_resource/repos/mysql/mysql-community_ustc_tmp1.repo
        # postgresql源
        # 改成从清华站下载安装
        rpm -Uvh https://mirrors.tuna.tsinghua.edu.cn/postgresql/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
        curl -s -o /etc/yum.repos.d/pgdg-96-centos.repo $url_resource/repos/postgresql/pgdg-96-centos_tuna.repo
        # zabbix源，临时屏蔽，阿里源也出问题了。
        # rpm -Uvh https://mirrors.aliyun.com/zabbix/zabbix/3.2/rhel/7/x86_64/zabbix-release-3.2-1.el7.noarch.rpm
        # curl -s -o /etc/yum.repos.d/zabbix.repo $url_resource/repos/zabbix/7/3.2/zabbix_aliyun.repo
    elif [[ $centos_version_main == "6" ]]; then
        # base
        curl -s -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-6.repo
        # epel
        yum install -y epel-release
        curl -s -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-6.repo
    else 
        echo "暂不支持CentOS5及以下的版本, 请手动退出脚本..."
        sleep 1000000000
    fi

    # 至少同时支持6,7的
}

function set_source(){
    if [[ $dist == "CentOS" ]]; then
        set_source_centos
    fi
}



# 设置python源
function set_source_pypi(){
    [ ! -d /root/.pip ] && mkdir /root/.pip
    curl -s -o /root/.pip/pip.conf $url_resource/pypi/pip_ustc.conf
    yum install -y python-pip
} 

# 安装软件
function install_basic_software(){
    yum makecache
    yum install -y \
        net-tools \
        sysstat \
        gcc gcc-c++ \
        expect \
        ntp ntpdate crontabs \
        wget lrzsz tree vim telnet wget openssh-clients unzip zip pigz \
        tomcat-native apr \
        nc net-snmp-utils \
        subversion git \
        bind-utils psmisc
}

# 设置selinux, 完成后需要重启服务器
function set_selinux(){
    getenforce | grep -i 'enforcing' && setenforce 0
    sed -i '/^SELINUX=/ c\SELINUX=disabled' /etc/selinux/config
    sed -i '/^SELINUX=/ c\SELINUX=disabled' /etc/sysconfig/selinux
}

# set_sudoers
function set_sudoers(){
    sed -i '/^Defaults    requiretty/ c\#Defaults    requiretty' /etc/sudoers
    sed -i '/^Defaults   !visiblepw/ c\Defaults   visiblepw' /etc/sudoers 
}

function set_firewall(){
    if [[ $dist == "CentOS" ]]; then
        # 备份防火墙规则表
        iptables -vnL > $dir_init/firewall@bak$time_full
        if [[ $centos_version_main == "7" ]]; then
            systemctl stop firewalld
            systemctl disable firewalld
        elif [[ $centos_version_main == "6" ]]; then
            service iptables stop
            chkconfig iptables off
        fi        
    fi
}


##获取IP功能
function get_lanIp(){
    # CentOS7
    # 检测网卡的那里，egrep -A1 'ens[0-9]{1,3}: |eth[0-9]{1,3}: |em[0-9]{1,3}: |bond[0-9]{1,3}: '，可以示单引号，也可以是双引号。centos6 7都支持两种引号
    # enp2s0 是极夜迷你主机的有线网卡设备名
    # 兼容centos6  eth[0-9]{1,3}:{0,1}
    if [[ $centos_version_main == "7" ]]; then
        lanIpALL=$(/sbin/ifconfig | egrep -A1 'ens[0-9]{1,3}: |ens[0-9]{1,3}: |eth[0-9]{1,3}: |eno[0-9]{1,3}: |em[0-9]{1,3}: |bond[0-9]{1,3}: ' | sed '/^--/ d' | awk '/inet / {print $2}'| egrep '^10\.|^172\.1[6-9]\.|^172\.2[0-9]\.|^172.3[0-1]\.|^192\.168')
    # CentOS6
    elif [[ $centos_version_main == "6" ]]; then
        lanIpALL=$(/sbin/ifconfig | sed -e '/bond[0-9]:/,/^$/ d' -e '/eth[0-9]:/,/^$/ d' -e '/em[0-9]:/,/^$/ d' | awk '/inet addr:/ {print $2}' | awk -F: '{print $2}' | egrep '^10\.|^172\.1[6-9]\.|^172\.2[0-9]\.|^172.3[0-1]\.|^192\.168')
    fi      

    num_lanIpALL=$(echo $lanIpALL | wc -w)
    if [ "$num_lanIpALL" -eq 1 ] ; then
        lanIp=$lanIpALL
    elif [ "$num_lanIpALL" -eq 0 ] ; then
        echo "未找到内网IP，请检查脚本是否不正确..."
        sleep 1000000000
    else
        echo "Warning! The number of lanIp is not 1(>=2), please choose one and input(IP_LAN1):" # 大于1
        sleep 1000000000
        echo $lanIpALL
        read lanIp
    fi
    # 把获取到的第一个IP写入进去
    echo "export IP_LAN1=$lanIp" > /etc/profile.d/ip_lan1.sh
}


# 设置语言，自定义命令提示符，和histroy日志格式,取消。不运行这个函数
# 里面有  $(pwd) 只能用文本来保存那段内容
function set_bash_prompt(){
    curl -s -o /etc/profile.d/bash-prompt.sh $url_resource/other/profile.d/bash-prompt.sh
}
# set_bash_prompt


function set_hosts(){
    local_hosts="$lanIp $HOSTNAME"
    grep "$local_hosts" /etc/hosts >/dev/null || echo "$local_hosts" >> /etc/hosts
    # 查看是否成功
    grep "$local_hosts" /etc/hosts
}



# 设置时区为 +8
function set_timezone(){
    cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
}

# ntpd
function set_ntpd(){
    if [[ $dist == "CentOS" ]]; then
        if [[ $centos_version_main == "7" ]]; then
            systemctl start ntpd
            systemctl enable ntpd
        elif [[ $centos_version_main == "6" ]]; then
            service ntpd start
            chkconfig ntpd on
        fi
    fi    
}

# crond
function set_crond(){
    if [[ $dist == "CentOS" ]]; then
        if [[ $centos_version_main == "7" ]]; then
            systemctl start crond
            systemctl enable crond
        elif [[ $centos_version_main == "6" ]]; then
            service crond start
            chkconfig crond on
        fi            
    fi    
}

# auto_start
function set_auto_start(){
    if [[ $dist == "CentOS" ]]; then
        if [[ $centos_version_main == "7" ]]
        then
            chmod +x /etc/rc.local
        fi            
    fi    
}


# 设置DNS,以追加模式
function set_dns(){
for dnsserver in "\
nameserver 8.8.8.8
nameserver 114.114.114.114\
"
do 
grep "$dnsserver" /etc/resolv.conf >/dev/null || echo "$dnsserver" >> /etc/resolv.conf
done
}

function set_sshd(){
    # sshd_config
    # 1. 关闭远程连接时 DNS 的IP反向解析请求
    # 2. 远程会话时,保持连接
    cfg_file_sshd='/etc/ssh/sshd_config'
    cfg_cmd_nodns='UseDNS no'
    # 主替换命令
    sed -i '/UseDNS/ c\UseDNS no' $cfg_file_sshd
    # 备用替换命令
    # 配置文件,只检索 'UseDNS' 而不是'UseDNS no' , 因为UseDNS 和no可以不止一个空格
    grep "UseDNS" $cfg_file_sshd >/dev/null || echo "$cfg_cmd_nodns" >> $cfg_sshd
    # ssh客户端保持连接
    sed -i "/^#ClientAliveInterval 0/ c\ClientAliveInterval 60" $cfg_file_sshd
    sed -i "/^#ClientAliveCountMax 3/ c\ClientAliveCountMax 3" $cfg_file_sshd
    
    # 6 7 都通用的
    service sshd reload
    # if [[ $centos_version_main == "7" ]]; then
    #     systemctl reload sshd
    # elif [[ $centos_version_main == "6" ]]; then
    #     service sshd reload
    # fi  
}

function set_dir(){
    # 新建目录
    [ ! -d /application ] && mkdir /application
    [ ! -d /data ] && mkdir /data
    [ ! -d /scripts ] && mkdir /scripts
    
}

function set_limits(){
    # 阿里云 和 本地机房 都要优化
echo "\
# Default limit for number of user's processes to prevent
# accidental fork bombs.
# See rhbz #432903 for reasoning.

*          soft    nofile    65535
root       soft    nofile    unlimited
*          hard    nofile    100000
*          soft    nproc     65535
root       soft    nproc     unlimited
*          hard    nproc     200000\
" > /etc/security/limits.d/20-nproc.conf

    # CentOS6 的默认是 90-nproc.conf
    # CentOS7 的默认是 20-nproc.conf
}

function set_docker(){
# 仅在centos7上安装docker
if [[ $centos_version_main == "7" ]]; then
# 安装docker-compose
pip install docker-compose

# 安装docker，此处可以加以判断，安装合适的docker版本
yum install -y docker-engine-1.12.6-1.el7.centos.x86_64

# 设置配置文件
# 驱动，镜像加速器，内核
[ ! -d "/etc/docker" ] && mkdir -p /etc/docker
echo '{
  "registry-mirrors": ["https://zahdqyo7.mirror.aliyuncs.com"],    
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}' > /etc/docker/daemon.json

# 最下面才启动docker，此处不用
# systemctl daemon-reload
# systemctl restart docker

# 设置内核参数
echo "\
net.ipv4.ip_forward=1
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
" > /etc/sysctl.d/docker.conf
sysctl -p /etc/sysctl.d/docker.conf

# 有报错，以后解决
# sysctl: cannot stat /proc/sys/net/bridge/bridge-nf-call-ip6tables: No such file or directory
# sysctl: cannot stat /proc/sys/net/bridge/bridge-nf-call-iptables: No such file or directory

# # 新增用户
# groupadd docker
# for USER in $(echo -e "opsadmin\ndevadmin")
# do
# usermod -aG docker $USER  
# done

# 设置开机自启动
systemctl enable docker
systemctl start docker
fi
}

# 在后面，暂时取消了这个
function set_ipv6(){
    echo "\
    alias net-pf-10 off
    options ipv6 disable=1\
    " > /etc/modprobe.d/ipv6.conf

# 设置内核参数
# 禁止后， kubelet 无法正常启动
echo "\
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
" > /etc/sysctl.d/disable_ipv6.conf
sysctl -p /etc/sysctl.d/disable_ipv6.conf    
}

# 检查是否已经执行过初始化脚本
function check_init_status(){
    if [[ $INIT_STATUS -ne 1 ]]; then
        echo "该系统已经执行过初始化脚本, 请使用 Ctrl+C 退出脚本..."
        sleep 1000000000
    else
        echo "该系统尚未执行过初始化脚本，请等待进一步检测..."
    fi
}

# 设置初始化状态，执行完毕之后，状态为1
function set_init_status(){
    echo "export INIT_STATUS=1" > /etc/profile.d/init_statu.sh
}

# 主函数
function main(){
    # check_init_status

    # 系统信息展示
    echo "本机系统为: ${dist}${dist_version} , 系统架构为: ${arch}位!"
    sleep 1

    # 检查此脚本是否兼容被初始化的系统
    support_dist="CentOS"
    echo $support_dist | grep $dist
    if [[ $? -ne 0 ]]; then
        echo "该初始化脚本暂不支持此发行版, 请使用 Ctrl+C 退出脚本..."
        sleep 1000000000
    else
        echo "系统兼容性检测通过, 开始执行初始化脚本..."
    fi
    
    # echo "\
    # +---------------------------------------+
    # |   your system is CentOS 6 x86_64      |
    # |        start optimizing.......        |
    # +---------------------------------------+
    # "

    set_source          # 阿里云需要注释掉
    set_source_pypi     # 阿里云需要注释掉
    install_basic_software
    get_lanIp           # 在安装好 net-tools后， 在获取局域网ip
    set_selinux
    set_sudoers
    set_firewall
    #set_bash_prompt    #注释掉，不需要自定义bash环境
    set_hosts
    set_timezone
    set_ntpd
    set_crond
    set_auto_start
    #set_dns     #这个看情况, 网关可以强制DNS代理
    set_sshd
    set_dir
    set_limits
    set_docker
    set_ipv6      # 取消禁止ipv6
    set_init_status

    echo "\
    +-------------------------------------------------+
    |               optimizer is done                 |
    |   it's recommond to restart this server !       |
    +-------------------------------------------------+
    "
}
main
