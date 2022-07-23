#!/bin/bash

#进入对应的conda环境，并提前准备好要校验的require_package.txt 文件

pip freeze  |grep -v @ >localpackage.txt

while read line

do
new_package="$line="
localpackage=`cat localpackage.txt`
if [[ ! $localpackage =~ $new_package ]];then
#if [[ $new_package not in  $localpackage ]];then
    echo $line
fi

done < require_package.txt
