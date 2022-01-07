#!/bin/bash
set -e
 
repository=(mmdetection mmclassification mmsegmentation)
 
 
for i in ${repository[@]}
do
 
if [ "$i" == "mmdetection" ];then
gitlab_dir=/home/platform_ci/auto_deploy/github2gitlab
gitlab_user=platform_ci
gitlab_token=YvbvTBUAUexrkELciHEh
gitlab_branch=master-opensource
#http clone地址去掉前面的 https://
gitlab_url=gitlab.sz.sensetime.com/parrotsDL-sz/mmdetection.git
github_url=https://github.com/open-mmlab/mmdetection.git
github_project=mmdetection
remote_gitlab=https://${gitlab_user}:${gitlab_token}@${gitlab_url}
 
elif [ "$i" == "mmclassification" ];then
gitlab_dir=/home/platform_ci/auto_deploy/github2gitlab
gitlab_user=platform_ci
gitlab_token=YvbvTBUAUexrkELciHEh
gitlab_branch=master-opensource
gitlab_url=gitlab.sz.sensetime.com/parrotsDL-sz/mmclassification.git
github_url=https://github.com/open-mmlab/mmclassification.git
github_project=mmclassification
remote_gitlab=https://${gitlab_user}:${gitlab_token}@${gitlab_url}
 
elif [ "$i" == "mmsegmentation" ];then
gitlab_dir=/home/platform_ci/auto_deploy/github2gitlab
gitlab_user=platform_ci
gitlab_token=YvbvTBUAUexrkELciHEh
gitlab_branch=master-opensource
gitlab_url=gitlab.sz.sensetime.com/parrotsDL-sz/mmsegmentation.git
github_url=https://github.com/open-mmlab/mmsegmentation.git
github_project=mmsegmentation
remote_gitlab=https://${gitlab_user}:${gitlab_token}@${gitlab_url}
fi
 
 
export http_proxy=http://172.16.1.135:3128/
export https_proxy=http://172.16.1.135:3128/
export HTTP_PROXY=http://172.16.1.135:3128/
export HTTPS_PROXY=http://172.16.1.135:3128/
cd $gitlab_dir
if [ ! -d $github_project ];then
    echo "not have project"
    git clone $github_url
    cd $github_project
    git checkout -b $gitlab_branch
    git remote add gitlab $remote_gitlab
    git push gitlab $gitlab_branch
else
    cd $gitlab_dir/$github_project
    git checkout master
    git pull
    git checkout  $gitlab_branch
    git merge master
    git push gitlab $gitlab_branch
fi
 
done
