#!/bin/bash
echo "Init System For CentOS 8"

# 切换 YUM 源
mv /etc/yum.repos.d/CentOS-Linux-BaseOS.repo /etc/yum.repos.d/CentOS-Linux-BaseOS.repo.backup
curl -o /etc/yum.repos.d/CentOS-Linux-BaseOS.repo http://mirrors.aliyun.com/repo/Centos-8.repo
yum makecache

# 更新系统
yum update -y

# 安装 zip 相关操作 
yum install zip unzip -y
# 安装 Wget
yum install wget -y
# 安装 VIM
yum install vim -y
# 用 vim 替换 vi
echo "alias vi=vim" >> ~/.bashrc
# 安装 GIT
yum install git -y
# 安装 mysql 
yum install mysql mysql-server -y
# 开机启动 mysql
systemctl enable mysqld
# 安装 apache web 服务器 httpd 
yum install httpd -y
# 关闭欢迎页面
mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.bk
# 在 WEB 服务器 DocRoot 目录写入测试页面
echo "<?php " >> /var/www/html/index.php
echo "phpinfo();" >> /var/www/html/index.php
# 开机启动 httpd
systemctl enable httpd

# 安装 PHP 7.4
yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
yum -y install https://rpms.remirepo.net/enterprise/remi-release-8.rpm
dnf -y install dnf-utils
dnf module install php:remi-7.4 -y
dnf update -y
yum install php74 php74-php php74-php-bcmath php74-php-cli php74-php-common php74-php-devel php74-php-fpm php74-php-gd -y
yum install php74-php-intl php74-php-json php74-php-mbstring php74-php-mysqlnd php74-php-pdo php74-php-pecl-xdebug -y
yum install php74-php-xml php74-runtime php74-libzip php74-php-pecl-crypto php74-php-pecl-env php74-php-pecl-imagick -y
yum install php74-php-pecl-imagick-devel php74-php-pecl-mcrypt php74-php-pecl-mysql -y
mv /etc/php.ini /etc/php.ini.bk
ln -s /etc/opt/remi/php74/php.ini /etc/php.ini
mv /etc/php.d /etc/php.d.bk
ln -s /etc/opt/remi/php74/php.d /etc/php.d
mv /usr/lib64/php/modules /usr/lib64/php/modules.bk
ln -s /opt/remi/php74/root/usr/lib64/php/modules /usr/lib64/php/modules

# 安装 composer
wget https://install.phpcomposer.com/composer.phar
mv composer.phar composer
mv composer /usr/local/bin/
chmod u+x /usr/local/bin/composer
composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/

# 关闭防火墙并禁止开机自启动
systemctl stop firewalld.service
systemctl disable firewalld.service
# 关闭 SELINUX
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

# 初始化完成
echo "System Inited : system will be reboot in 5 secs"
sleep 5
reboot
