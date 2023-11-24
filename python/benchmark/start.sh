#!/bin/bash
set -e
start_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "开始时间: $start_time"
[ $# -eq 0 ] && { echo "请传入drive参数 cuda 或 camb"; exit 1; }
drive=$1
#配置信息，根据需求更改
export max_iters=10  #每个模型跑多少iter
count_line=10      #计算最后多少行的平均值，应小于iter数量
if [ $max_iters -lt $count_line ];then echo "计算行数 应小于iter数量" && exit 1 ;fi
if [ $drive = 'cuda' ];then
    job_name='DIPU_benchmark'  #job名称
    gpu_num="1 2"  #分别使用多少gpu或mlu训练
    env_name='dipu_dailybuild dipu20230822'  #环境名,多个环境空格隔开
    slurm_par='pat_rd'  #使用的分区
    env_path=/mnt/cache/share/platform/env
elif [[ $drive = 'camb' ]]; then
    job_name='DIPU_benchmark'  #job名称
    gpu_num="1 2"  #分别使用多少gpu或mlu训练
    env_name='dipu20230817'  #环境名，多个环境空格隔开
    slurm_par='camb_mlu370_m8'  #使用的分区
    env_path=/mnt/cache/share/platform/env
fi

function PROXY() {
    export http_proxy=http://172.16.1.135:3128/
    export https_proxy=http://172.16.1.135:3128/
    export HTTP_PROXY=http://172.16.1.135:3128/
    export HTTPS_PROXY=http://172.16.1.135:3128/
}

DATE=$(date +'%Y-%m-%d')
pwd=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd ${pwd} && echo ${pwd}


#开始训练
train(){
    PROXY
    rm -rf DIPU && git clone https://github.com/DeepLink-org/DIPU.git
    sed -i '/build_needed_repo_camb()/b;/build_needed_repo_camb/d' DIPU/scripts/ci/ci_one_iter.sh #不需要编译mmcv，使用环境内的
    sed -i '/build_needed_repo_cuda()/b;/build_needed_repo_cuda/d' DIPU/scripts/ci/ci_one_iter.sh
    sed -i '/PYTHONPATH.*mmcv/d'  DIPU/scripts/ci/ci_one_iter.sh #不添加mmcv的PYTHONPATH

    #clone模型代码，如果已clone可以注释掉。默认删除重新clone
    rm -rf ${pwd}/DIPU/mmlab_pack && mkdir -p ${pwd}/DIPU/mmlab_pack && cd ${pwd}/DIPU/mmlab_pack && sh ../scripts/ci/ci_one_iter.sh clone

    rm -rf ${pwd}/DIPU/mmlab_pack/SMART && rm -rf ${pwd}/DIPU/mmlab_pack/DIPU_benchmark
    for env in $env_name;do
        if [ ! -f ${env_path}/${env} ];then
            echo "${env} not exist" && exit 1
        fi
        cd ${pwd}/DIPU/mmlab_pack
        source ${env_path}/${env}
        export PYTHONPATH=${pwd}:$PYTHONPATH
        which python
        if [ $drive = 'cuda' ];then
            sh ../scripts/ci/ci_one_iter.sh build_cuda      #数据集软链接
            source ../scripts/ci/ci_one_iter.sh export_pythonpath_cuda ${pwd}/DIPU/mmlab_pack  #添加模型仓库PYTHONPATH
        elif [[ $drive = 'camb' ]]; then
            sh ../scripts/ci/ci_one_iter.sh build_camb
            source ../scripts/ci/ci_one_iter.sh export_pythonpath_camb ${pwd}/DIPU/mmlab_pack
        fi
        cd ${pwd}/DIPU/mmlab_pack && python ${pwd}/benchmark.py ${env}  ${drive} ${job_name} "${gpu_num}" ${slurm_par}
        source ${env_path}/pat_deactivate
    done
}

#统计训练数据
report(){
    element_count=$(echo $env_name | wc -w)
    cd ${pwd}
    rm -rf report && mkdir report && cp benchmark_template.md report/benchmark_${DATE}.md
    for env in $env_name;do
        source ${env_path}/${env}
        if [ $drive = 'cuda' ];then
            GPU_MODEL=`srun -p ${slurm_par} nvidia-smi --query-gpu=gpu_name --format=csv,noheader|head -n1`
            SYSTEM=`srun -p ${slurm_par} cat /etc/centos-release`
            python ${pwd}/report_deps.py ${pwd}/report/benchmark_${DATE}.md ${env} #获取环境使用的依赖版本
        elif [[ $drive = 'camb' ]]; then
            echo "camb"
            GPU_MODEL=`srun -p ${slurm_par} cnmon info |grep 'Product Name'|head -n1|awk -F ':' '{print $2}'`
            SYSTEM=`srun -p ${slurm_par} cat /etc/centos-release`
            python ${pwd}/report_deps.py ${pwd}/report/benchmark_${DATE}.md ${env} #获取环境使用的依赖版本
        fi
        if [ $element_count -eq 1 ]; then #循环到最后一个环境时修改Markdown文件，及统计训练数据
            sed -i "s/{SYSTEM}/${SYSTEM}/g" ${pwd}/report/benchmark_${DATE}.md
            sed -i "s/{GPU_MODEL}/${GPU_MODEL}/g" ${pwd}/report/benchmark_${DATE}.md
            sed -i "s/{GPU_LIST}/${gpu_num}/g" ${pwd}/report/benchmark_${DATE}.md
            sed -i "s/{DIPU_ENV}/${env_name}/g" ${pwd}/report/benchmark_${DATE}.md
            sed -i "s/{DATE}/${DATE}/g" ${pwd}/report/benchmark_${DATE}.md
            python ${pwd}/report_batchsize.py ${pwd}/report/benchmark_${DATE}.md ${pwd}/DIPU/mmlab_pack/DIPU_benchmark
            python ${pwd}/report_json.py ${pwd}/report/report_json.json ${pwd}/DIPU/mmlab_pack/DIPU_benchmark ${count_line}
            python ${pwd}/report_img.py ${pwd}/report/image ${pwd}/report/report_json.json ${pwd}/report/benchmark_${DATE}.md $drive
        fi
        source ${env_path}/pat_deactivate
        ((element_count--))
    done
}

train
report
end_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "开始时间: $start_time"
echo "结束时间: $end_time"
