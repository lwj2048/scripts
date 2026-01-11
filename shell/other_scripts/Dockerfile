FROM jlesage/firefox:latest

USER root

# 安装中文输入法 + 中文字体（Alpine Linux 使用 apk）
RUN apk add --no-cache \
        ibus \
        ibus-libpinyin \
        ibus-gtk2 \
        ibus-gtk3 \
        font-noto-cjk \
        font-wqy-zenhei

# 配置输入法环境变量（对 GTK / Qt / X11 都生效）
ENV GTK_IM_MODULE=ibus \
    QT_IM_MODULE=ibus \
    XMODIFIERS=@im=ibus \
    LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    ENABLE_CJK_FONT=1

# 启动时自动拉起 ibus-daemon 并配置输入法
# jlesage 镜像使用 /etc/cont-init.d/ 目录运行初始化脚本
# 使用 99- 前缀确保在最后执行，此时 X 服务器应该已经启动
RUN mkdir -p /etc/cont-init.d && \
    printf '#!/bin/sh\n\
# 等待 X 服务器启动（最多等待 10 秒）\n\
for i in $(seq 1 10); do\n\
    if [ -S /tmp/.X11-unix/X0 ] || [ -f /tmp/.X11-unix/X0 ]; then\n\
        break\n\
    fi\n\
    sleep 1\n\
done\n\
# 额外等待确保 X 服务器完全就绪\n\
sleep 2\n\
# 设置环境变量\n\
export DISPLAY=:0\n\
export HOME=/home/abc\n\
export XDG_CONFIG_HOME=/home/abc/.config\n\
# 创建配置目录\n\
mkdir -p /home/abc/.config/ibus\n\
# 启动 ibus daemon（如果还没启动）\n\
if ! pgrep -x ibus-daemon > /dev/null; then\n\
    ibus-daemon -drx || true\n\
    sleep 3\n\
fi\n\
# 设置默认输入法引擎为 libpinyin（中文拼音）\n\
# 使用重试机制，因为 ibus 可能需要更多时间初始化\n\
for i in $(seq 1 5); do\n\
    if ibus engine libpinyin 2>/dev/null; then\n\
        break\n\
    fi\n\
    sleep 1\n\
done\n\
' > /etc/cont-init.d/99-ibus && \
    chmod +x /etc/cont-init.d/99-ibus

# jlesage 镜像会在最后自动切回 abc 用户，不用手动 USER
