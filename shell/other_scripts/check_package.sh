#!/bin/bash

#当前路径准备好require_package_pt2.0_dipu.txt文件
#source环境后直接执行此脚本
pip list --format=freeze  > local_env_package.txt
file1=require_package_pt2.0_dipu.txt
file2=local_env_package.txt
RED='\033[31m'
YELLOW='\033[33m'
NORMAL='\033[0m'

# 找出两个文件中版本不同的包
while IFS= read -r line; do
    package_name=$(echo "$line" | cut -d'=' -f1)
    version=$(echo "$line" | cut -d'=' -f3)

    # 使用grep -i进行不区分大小写的查找
    matched_line=$(grep -i "^$package_name==" "$file1")

    # 如果在第一个文件中找到相应的包名
    if [[ -n "$matched_line" ]]; then
        old_version=$(echo "$matched_line" | cut -d'=' -f3)
        # 如果版本号不同
        if [[ "$version" != "$old_version" ]]; then
            #echo "$package_name==$old_version"
            echo -e "${RED}Different version${NORMAL}: $package_name (file2: $version, file1: $old_version)"
        fi
    else
        # 打印第二个文件中比第一个文件多的包
        echo -e "${YELLOW}Package only in file2${NORMAL}: $line"
    fi
done < "$file2"
rm -rf $file2