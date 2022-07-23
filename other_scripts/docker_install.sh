#!/bin/bash

# 先判断Docker服务是否启动
dockerStatusResult=$(service docker status)
statusName="running"
if [[ ! $dockerStatusResult =~ $statusName ]]; then
  echo "请先启动Docker服务..."
  exit 0
fi
# 判断是否有static这个网络，没有的话创建网络
dockerNetworkResult=$(docker network ls)
networkName="static"
if [[ ! "$dockerNetworkResult" =~ $networkName ]]; then
  echo "没有static自定义网络，将自动创建static网络！"
  docker network create --subnet 172.18.0.0/24 $networkName
  if [ "$?" -eq 0 ]; then
    echo "static 自定义网络创建成功"
  else
    echo "static 自定义网络创建失败，请检查相关配置！"
    exit 0
  fi
fi

funPrintK() {
  echo ''
}
funPrintX() {
  for ((i = 0; i < $1; i++)); do
    printf '*'
  done
  funPrintK
}
funPrintJ() {
  for ((i = 0; i < $1; i++)); do
    printf '+'
  done
  if [ "$2" -eq 1 ]; then
    funPrintK
  fi
}

funPrintK
funPrintX 81
printf "*%-28sDocker 容器快捷安装脚本%-28s*"
funPrintK
printf "*%-28s@Author: hyd%-39s*"
funPrintK
printf "*%-28sVersion: 1.1.2%-37s*"
funPrintK
funPrintX 81
funPrintK

funPrintJ 36 0
printf '开始安装'
funPrintJ 37 1
printf "+%-32s请输入你的选择:%-32s+"
funPrintK
printf "+%-32s[1]: Nacos%-37s+"
funPrintK
printf "+%-32s[2]: Redis%-37s+"
funPrintK
printf "+%-32s[3]: MySql%-37s+"
funPrintK
printf "+%-32s[4]: Nginx%-37s+"
funPrintK
printf "+%-32s[5]: Minio%-37s+"
funPrintK
printf "+%-32s[*]: 任意字符退出%-30s+"
funPrintK
funPrintJ 81 1
funPrintK

BASE_PATH="/opt/docker"
NACOS_NAME="nacos/nacos-server"
MYSQL_NAME="mysql:5.7"
REDIS="redis"
NGINX="nginx"
MINIO="minio/minio:RELEASE.2021-06-17T00-10-46Z.fips"

externalPort() {
  funPrintK
  read -p "请输入""$APPLICATION_NAME""外部端口：" EXTERNAL_PORT
  if echo "$EXTERNAL_PORT" | grep -q '[^0-9]'; then
    echo "请输入正整数..."
    externalPort
  fi
  netstat -antp | grep "$EXTERNAL_PORT"
  funPrintK
  read -p "查看端口是否被占用,端口占用可能导致安装失败！继续下一步请输入(yes/y),重来请输入(no/n);退出直接回车：" port
  case "$port" in
  y | yes | Y | YES)
    internalPort
    ;;
  n | no | N | NO)
    externalPort
    ;;
  *)
    exit 0
    ;;
  esac

}

internalPort() {
  read -p "请输入""$APPLICATION_NAME""内部端口：" INTERNAL_PORT
  if echo "$INTERNAL_PORT" | grep -q '[^0-9]'; then
    echo "请输入正整数..."
    internalPort
  fi
}

funPassword() {
  read -s -p "请输入""$APPLICATION_NAME""的密码：" PASSWORD
  funPrintK
}

funMinioName() {
  read -p "请输入""$APPLICATION_NAME""的账号：" MINIO_NAME
  if [ ! ${#MINIO_NAME} -ge 3 ]; then
    echo "$APPLICATION_NAME""账号长度必须大于3"
    funMinioName
  fi
}

funMinioPwd() {
  read -s -p "请输入""$APPLICATION_NAME""的密码：" MINIO_PWD
  if [ ! ${#MINIO_PWD} -ge 8 ]; then
    echo "$APPLICATION_NAME""密码长度必须大于8"
    funMinioPwd
  fi
  echo
}

basePath() {
  sleep 1
  if [ ! -x "$BASE_PATH" ]; then
    sudo mkdir "$BASE_PATH"
    sudo chown -R "$USER" "$BASE_PATH"
  fi
  if [ ! -x "$BASE_PATH/$APPLICATION_NAME" ]; then
    mkdir -p "$BASE_PATH/$APPLICATION_NAME"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""路径创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""路径创建成功"
    fi
  fi
}

logPath() {
  if [ ! -x "$BASE_PATH/$APPLICATION_NAME""/logs" ]; then
    mkdir -p "$BASE_PATH/$APPLICATION_NAME""/logs"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/logs路径创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/logs路径创建成功"
    fi
  fi
}
confPath() {
  if [ ! -x "$BASE_PATH/$APPLICATION_NAME""/conf" ]; then
    mkdir -p "$BASE_PATH/$APPLICATION_NAME""/conf"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/conf路径创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/conf路径创建成功"
    fi
  fi
}
dataPath() {
  if [ ! -x "$BASE_PATH/$APPLICATION_NAME""/data" ]; then
    mkdir -p "$BASE_PATH/$APPLICATION_NAME""/data"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/data路径创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/data路径创建成功"
    fi
  fi
}
nginxConf() {
  if [ ! -x "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d" ]; then
    mkdir -p "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d路径创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d路径创建成功"
    fi
  fi
}

nginxHtml() {
  if [ ! -x "$BASE_PATH/$APPLICATION_NAME""/html" ]; then
    mkdir -p "$BASE_PATH/$APPLICATION_NAME""/html"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/html路径创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/html路径创建成功"
    fi
  fi
}

funCheckApplication() {
  if [ ! -f "$BASE_PATH/$APPLICATION_NAME""/conf""/application.properties" ]; then
    touch "$BASE_PATH/$APPLICATION_NAME""/conf""/application.properties"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/conf""/application.properties创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/conf""/application.properties创建成功"
    fi
    echo "server.servlet.contextPath=/nacos" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "spring.datasource.platform=mysql" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "db.num=1" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "db.url.0=jdbc:mysql://172.18.0.2:3306/nacos?characterEncoding=utf8 &
    connectTimeout=1000 &
    socketTimeout=3000 &
    autoReconnect=true &
    useUnicode=true &
    useSSL=false &
    serverTimezone=UTC" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "db.user.0=root" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "db.password.0=2020" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.naming.empty-service.auto-clean=true" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.naming.empty-service.clean.initial-delay-ms=50000" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.naming.empty-service.clean.period-time-ms=30000" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "management.endpoints.web.exposure.include=*" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "management.metrics.export.elastic.enabled=false" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "management.metrics.export.influx.enabled=false" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "server.tomcat.accesslog.pattern=%h %l %u %t '%r' %s %b %D %{User-Agent}i %{Request-Source}i" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "server.tomcat.basedir=" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.security.ignore.urls=/,/error,/**/*.css,/**/*.js,/**/*.html,/**/*.map,/**/*.svg,/**/*.png,/**/*.ico,/console-ui/public/**,/v1/auth/**,/v1/console/health/**,/actuator/**,/v1/console/server/**" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.system.type=nacos" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.enabled=false" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.default.token.expire.seconds=18000" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.default.token.secret.key=SecretKey012345678901234567890123456789012345678901234567890123456789" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.enable.userAgentAuthWhite=false" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.server.identity.key=serverIdentity" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.core.auth.server.identity.value=security" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
    echo "nacos.istio.mcp.server.enabled=false" >>"$BASE_PATH/$APPLICATION_NAME""/conf/application.properties"
  fi
}

funCheckRedisConf() {
  if [ ! -f "$BASE_PATH/$APPLICATION_NAME""/conf/redis.conf" ]; then
    touch "$BASE_PATH/$APPLICATION_NAME""/conf/redis.conf"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/redis.conf创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/redis.conf创建成功"
    fi
    echo " " >>"$BASE_PATH/$APPLICATION_NAME""/conf/redis.conf"
  fi
}

funCheckNginxConf() {
  if [ ! -f "$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf" ]; then
    touch "$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf创建成功"
    fi
    funPrintK
    echo "user  nginx;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "worker_processes  auto;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    funPrintK
    echo "error_log  /var/log/nginx/error.log notice;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "pid        /var/run/nginx.pid;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    funPrintK
    funPrintK
    echo "events {" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    worker_connections  1024;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "}" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    funPrintK
    funPrintK
    echo "http {" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    include       /etc/nginx/mime.types;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    default_type  application/octet-stream;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    funPrintK
    echo "     log_format  main" '$remote_addr - $remote_user [$time_local] "$request" ' >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "                      "'$status $body_bytes_sent "$http_referer" ' >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "                       "'"$http_user_agent" "$http_x_forwarded_for"'';' >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    funPrintK
    echo "    access_log  /var/log/nginx/access.log  main;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    sendfile        on;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    #tcp_nopush     on;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    keepalive_timeout  65;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    #gzip  on;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "    include /etc/nginx/conf.d/*.conf;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
    echo "}" >>"$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf"
  fi
}

funCheckNginxDef() {
  if [ ! -f "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf" ]; then
    touch "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf创建成功"
    fi
    echo "server {" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "listen       80;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "listen  [::]:80;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "server_name  localhost;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo " #access_log  /var/log/nginx/host.access.log  main;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "location / {" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "root   /usr/share/nginx/html;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "index  index.html index.htm;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "}" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "#error_page  404              /404.html;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "# redirect server error pages to the static page /50x.html" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "#" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "error_page   500 502 503 504  /50x.html;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "location = /50x.html {" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo " root   /usr/share/nginx/html;" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "}" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
    echo "}" >>"$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf"
  fi
}

funCheckNginxIndex() {
  if [ ! -f "$BASE_PATH/$APPLICATION_NAME""/html/index.html" ]; then
    touch "$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/html/index.html创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/html/index.html创建成功"
    fi
    echo "<!DOCTYPE html>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<meta charset="UTF-8">" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<html lang="zh">" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<head>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "    <title>欢迎来到 Nginx !</title>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "    <style>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "        body {" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "            width: 35em;" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "            margin: 0 auto;" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "            font-family: Tahoma, Verdana, Arial, sans-serif;" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "        }" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "        h1 {" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "            color: #26e32f;" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "        }" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "    </style>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "</head>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<body>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<h1>欢迎来到 Nginx !</h1>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<p>如果您看到此页面，则 nginx Web 服务器已成功安装并正常工作。需要进一步配置。</p>" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo "<p>有关在线文档和支持，请参阅" >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo '    <a href="http://nginx.org/">nginx.org</a>.<br/>' >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo '    商业支持可在' >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo '    <a href="http://nginx.com/">nginx.com</a>.</p>' >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo '<p><em>感谢您使用 nginx。</em></p>' >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo '</body>' >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
    echo '</html>' >>"$BASE_PATH/$APPLICATION_NAME""/html/index.html"
  fi
}

funCheckNginx50() {
  if [ ! -f "$BASE_PATH/$APPLICATION_NAME""/html/50.html" ]; then
    touch "$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    if [ "$?" -ne 0 ]; then
      echo "$BASE_PATH/$APPLICATION_NAME""/html/50.html创建失败"
      exit 0
    else
      echo "$BASE_PATH/$APPLICATION_NAME""/html/50.html创建成功"
    fi
    echo "<!DOCTYPE html>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<meta charset="UTF-8">" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<html lang="zh">" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<head>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "    <title>欢迎来到 Nginx !</title>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "    <style>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "        body {" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "            width: 35em;" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "            margin: 0 auto;" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "            font-family: Tahoma, Verdana, Arial, sans-serif;" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "        }" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "        h1 {" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "            color: #d03535;" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "        }" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "    </style>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "</head>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<body>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<h1>发生错误。</h1>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<p>抱歉，您要查找的页面当前不可用。<br>请稍后再试。</p>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<p>如果您是该资源的系统管理员，那么您应该检查错误日志以获取详细信息</p>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "<p><em>忠实于你的，nginx。</em></p>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "</body>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"
    echo "</html>" >>"$BASE_PATH/$APPLICATION_NAME""/html/50.html"

  fi
}

funDocker() {
  echo "开始停止""$APPLICATION_NAME"" 容器..."
  docker stop "$APPLICATION_NAME"
  funPrintK

  echo "开始删除""$APPLICATION_NAME""容器..."
  docker rm "$APPLICATION_NAME"
  funPrintK
}

funStart() {
  funPrintK
  echo "开始安装""$APPLICATION_NAME""..."
  funPrintK
}
funSuccess() {
  if [ "$?" -ne 0 ]; then
    echo "$APPLICATION_NAME""安装失败！"
  else
    echo "$APPLICATION_NAME""安装成功！"
    funPrintK
    docker ps | grep "$APPLICATION_NAME"
  fi
  exit 0
}

funNacos() {
  APPLICATION_NAME="nacos"
  externalPort
  basePath
  logPath
  confPath
  funCheckApplication
  funStart
  funDocker
  docker run -itd --name "$APPLICATION_NAME" --restart always -p "$EXTERNAL_PORT":"$INTERNAL_PORT" \
    --net static --ip 172.18.0.3 \
    -v "$BASE_PATH/$APPLICATION_NAME""/conf/application.properties":/home/nacos/conf/application.properties \
    -v "$BASE_PATH/$APPLICATION_NAME/logs":/home/nacos/logs \
    -e MODE=standalone \
    "$NACOS_NAME"
  funSuccess
}

funRedis() {
  APPLICATION_NAME="redis"
  externalPort
  funPassword
  basePath
  confPath
  dataPath
  funCheckRedisConf
  funStart
  funDocker
  docker run -itd --name "$APPLICATION_NAME" --restart always -p "$EXTERNAL_PORT":"$INTERNAL_PORT" \
    -v "$BASE_PATH/$APPLICATION_NAME""/conf/redis.conf":/etc/redis/redis.conf \
    -v "$BASE_PATH/$APPLICATION_NAME""/data":/etc/redis/data \
    "$REDIS" \
    --appendonly yes --requirepass "$PASSWORD"
  funSuccess
}

funMysql() {
  APPLICATION_NAME="mysql"
  externalPort
  funPassword
  basePath
  dataPath
  confPath
  funStart
  funDocker
  docker run -itd --name "$APPLICATION_NAME" --net static --ip 172.18.0.2 --restart always -p "$EXTERNAL_PORT":"$INTERNAL_PORT" \
    -e MYSQL_ROOT_PASSWORD="$PASSWORD" \
    -v "$BASE_PATH/$APPLICATION_NAME""/data/":/var/lib/mysql \
    -v "$BASE_PATH/$APPLICATION_NAME""/conf":/etc/mysql/conf.d \
    "$MYSQL_NAME"
  funSuccess
}

funNginx() {
  APPLICATION_NAME="nginx"
  externalPort
  basePath
  confPath
  logPath
  nginxConf
  nginxHtml
  funCheckNginxConf
  funCheckNginxDef
  funCheckNginxIndex
  funCheckNginx50
  funStart
  funDocker
  docker run -d --name "$APPLICATION_NAME" -p "$EXTERNAL_PORT":"$INTERNAL_PORT" \
    -v "$BASE_PATH/$APPLICATION_NAME""/html":/usr/share/nginx/html/ \
    -v "$BASE_PATH/$APPLICATION_NAME""/conf/nginx.conf":/etc/nginx/nginx.conf \
    -v "$BASE_PATH/$APPLICATION_NAME""/conf/conf.d/default.conf":/etc/nginx/conf.d/default.conf \
    -v "$BASE_PATH/$APPLICATION_NAME""/logs/":/var/log/nginx \
    "$NGINX"
  funSuccess
}

funMinIo() {
  APPLICATION_NAME="minio"
  externalPort
  funMinioName
  funMinioPwd
  basePath
  dataPath
  confPath
  funStart
  funDocker
  docker run -itd --name "$APPLICATION_NAME" --restart always -p "$EXTERNAL_PORT":"$INTERNAL_PORT" \
    -e "MINIO_ACCESS_KEY=""$MINIO_NAME" \
    -e "MINIO_SECRET_KEY=""$MINIO_PWD" \
    -v "$BASE_PATH/$APPLICATION_NAME""/data":/data \
    -v "$BASE_PATH/$APPLICATION_NAME""/conf":/root/.minio \
    "$MINIO" server /data
  funSuccess
}

read -p "请输入对应的序号：" input
case $input in
1)
  funNacos
  ;;
2)
  funRedis
  ;;
3)
  funMysql
  ;;

4)
  funNginx
  ;;
5)
  funMinIo
  ;;
*)
  echo "退出安装程序"
  exit 0
  ;;
esac
