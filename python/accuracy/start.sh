#!/bin/bash
set -e
start_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "开始时间: $start_time"
[ $# -eq 0 ] && { echo "请传入drive参数 cuda 或 camb"; exit 1; }
drive=$1

#配置信息，根据需求更改。虽然多环境多模型会遍历训练，但因为训练时间较长，推荐变量只设置一个
if [ $drive = 'cuda' ];then
    job_name='DIPU_accuracy'  #job名称
    gpu_num="1"      #使用多少gpu或mlu训练
    env_name='dipu0.3.0'  #环境名
    slurm_par='pat_rd'  #使用的分区
    model="resnet"  #测试的模型
    env_path=/mnt/cache/share/platform/env
    epoch=100
elif [[ $drive = 'camb' ]]; then
    job_name='DIPU_accuracy'  #job名称
    gpu_num="1"      #使用多少gpu或mlu训练
    env_name='dipu0.3.0'  #环境名
    slurm_par='camb_mlu370_m8'  #使用的分区
    model="resnet"  #测试的模型
    env_path=/mnt/cache/share/platform/env
    epoch=100
fi

function PROXY() {
    export http_proxy=http://172.16.1.135:3128/
    export https_proxy=http://172.16.1.135:3128/
    export HTTP_PROXY=http://172.16.1.135:3128/
    export HTTPS_PROXY=http://172.16.1.135:3128/
}
#模型配置
declare -A model_configs
model_configs=(
    ["resnet"]="mmpretrain resnet/resnet50_8xb32_in1k.py workdirs_resnet"
    ["swin_transformer"]="mmpretrain swin_transformer/swin-large_16xb64_in1k.py workdirs_swin_transformer"
    ["vision_transformer"]="mmpretrain vision_transformer/vit-base-p16_64xb64_in1k-384px.py workdirs_vision_transformer"
    ["efficientnet"]="mmpretrain efficientnet/efficientnet-b2_8xb32_in1k.py workdirs_efficientnet"
    ["mobilenetv3"]="mmpretrain mobilenet_v3/mobilenet-v3-large_8xb128_in1k.py workdirs_mobilenetv3"
    ["mobilenetv2"]="mmpretrain mobilenet_v2/mobilenet-v2_8xb32_in1k.py workdirs_mobilenetv2"
    ["convnext"]="mmpretrain convnext/convnext-small_32xb128_in1k.py workdirs_convnext"
    # 官方无训练配置信息，为自己创建的
    # ["shufflenetv2"]="mmpretrain shufflenet_v2/shufflenet-v2-1x_16xb64_in1k_256.py workdirs_shufflenetv2"
    ["detr"]="mmdetection detr/detr_r50_8xb2-150e_coco.py workdirs_detr"
    ["yolov3"]="mmdetection yolo/yolov3_d53_8xb8-320-273e_coco.py workdirs_yolov3"
    ["ssd"]="mmdetection ssd/ssd300_coco.py workdirs_ssd"
    ["fcos"]="mmdetection fcos/fcos_r50-dcn-caffe_fpn_gn-head-center-normbbox-centeronreg-giou_1x_coco.py workdirs_fcos"
    ["retinanet"]="mmdetection retinanet/retinanet_r50_fpn_1x_coco.py workdirs_retinanet"
    ["mask_rcnn"]="mmdetection mask_rcnn/mask-rcnn_r50_fpn_1x_coco.py workdirs_mask_rcnn"
    ["faster_rcnn"]="mmdetection faster_rcnn/faster-rcnn_r101_fpn_1x_coco.py workdirs_faster_rcnn"
    ["dyhead"]="mmdetection dyhead/atss_swin-l-p4-w12_fpn_dyhead_ms-2x_coco.py workdirs_dyhead"
    ["hrnet"]="mmpose body_2d_keypoint/topdown_heatmap/coco/td-hm_hrnet-w32_udp-8xb64-210e_coco-256x192.py workdirs_hrnet"
    ["tsn"]="mmaction2 recognition/tsn/tsn_imagenet-pretrained-r50_8xb32-1x1x3-100e_kinetics400-rgb.py workdirs_tsn"
    # 模型跑不过，待排查
    # ["crnn"]="mmocr textrecog/crnn/crnn_mini-vgg_5e_mj.py workdirs_crnn"
    # ["dbnet"]="mmocr textdet/dbnet/dbnet_resnet50-dcnv2_fpnc_1200e_icdar2015.py workdirs_dbnet"
    ["deeplabv3"]="mmsegmentation deeplabv3/deeplabv3_r50-d8_4xb2-40k_cityscapes-512x1024.py workdirs_deeplabv3"
    ["deeplabv3plus"]="mmsegmentation deeplabv3plus/deeplabv3plus_r50-d8_4xb2-40k_cityscapes-512x1024.py workdirs_deeplabv3plus"
    ["unet"]="mmsegmentation unet/unet-s5-d16_fcn_4xb4-160k_cityscapes-512x1024.py workdirs_unet"
    ["pspnet"]="mmsegmentation pspnet/pspnet_r50-d8_4xb2-40k_cityscapes-512x1024.py workdirs_pspnet"
    ["yolov5"]="mmyolo yolov5/yolov5_s-v61_syncbn_8xb16-300e_coco.py workdirs_yolov5"
    ["pointpillars"]="mmdetection3d pointpillars/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-3class.py workdirs_pointpillars"
    # 强化学习模型没有精度信息
    # ["ppo"]="DI-engine ding/example/ppo.py workdirs_ppo"
    # ["sac"]="DI-engine ding/example/sac.py workdirs_sac"
    # 仅适配one_iter跑的,需要ONE_ITER_TOOL_STORAGE_PATH环境变量
    # ["stable_diffusion"]="mmagic stable_diffusion/stable-diffusion_ddim_denoisingunet_infer.py workdirs_stable_diffusion"
)

function clone(){
    #clone模型仓库
    repo=$1
    PROXY
    if [[ ${repo} == "mmocr" ]];then
       url="https://github.com/open-mmlab"
    else
       url="https://github.com/DeepLink-org"
    fi
    if [[ -d ${repo} ]];then
      cd ${repo} && git stash&&git checkout main
    else
      git clone ${url}/${repo}.git
      cd ${repo} && git checkout main  && git pull
    fi
    cd ${pwd}/accuracy
}
function build_dataset(){
    # link dataset
    if [ "$1" = "cuda" ]; then
        echo "Executing CUDA operation in build dataset..."
        rm -rf data
        mkdir data
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/dataset/data_for_ln/imagenet data/imagenet
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/dataset/data_for_ln/coco  data/coco
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/dataset/data_for_ln/cityscapes data/cityscapes
        ln -s /mnt/lustre/share_data/openmmlab/datasets/action/Kinetics400 data/kinetics400
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/dataset/data_for_ln/icdar2015 data/icdar2015
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/dataset/data_for_ln/mjsynth data/mjsynth
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/dataset/data_for_ln/kitti data/kitti
        ln -s /mnt/lustre/share_data/shenliancheng/swin_large_patch4_window12_384_22k.pth data/swin_large_patch4_window12_384_22k.pth
        ln -s /mnt/lustre/share_data/parrots.tester.s.03/models_code/mmagic/stable-diffusion-v1-5 data/stable-diffusion-v1-5

    elif [ "$1" = "camb" ]; then
        echo "Executing CAMB operation in build dataset..."
        rm -rf data
        mkdir data
        ln -s /mnt/lustre/share_data/PAT/datasets/Imagenet data/imagenet
        ln -s /mnt/lustre/share_data/PAT/datasets/mscoco2017  data/coco
        ln -s /mnt/lustre/share_data/PAT/datasets/mmseg/cityscapes data/cityscapes
        ln -s /mnt/lustre/share_data/slc/mmdet3d/mmdet3d data/kitti
        ln -s /mnt/lustre/share_data/PAT/datasets/mmaction/Kinetics400 data/kinetics400
        ln -s /mnt/lustre/share_data/PAT/datasets/mmocr/icdar2015 data/icdar2015
        ln -s /mnt/lustre/share_data/PAT/datasets/mmocr/mjsynth data/mjsynth
        ln -s /mnt/lustre/share_data/PAT/datasets/mmdet/checkpoint/swin_large_patch4_window12_384_22k.pth data/swin_large_patch4_window12_384_22k.pth
        ln -s /mnt/lustre/share_data/PAT/datasets/pretrain/torchvision/resnet50-0676ba61.pth data/resnet50-0676ba61.pth
        ln -s /mnt/lustre/share_data/PAT/datasets/mmdet/pretrain/vgg16_caffe-292e1171.pth data/vgg16_caffe-292e1171.pth
        ln -s /mnt/lustre/share_data/PAT/datasets/mmdet/pretrain/darknet53-a628ea1b.pth data/darknet53-a628ea1b.pth
        ln -s /mnt/lustre/share_data/PAT/datasets/mmpose/pretrain/hrnet_w32-36af842e.pth data/hrnet_w32-36af842e.pth
        ln -s /mnt/lustre/share_data/PAT/datasets/pretrain/mmcv/resnet50_v1c-2cccc1ad.pth data/resnet50_v1c-2cccc1ad.pth

    else
        echo "Invalid parameter. Please specify 'cuda' or 'camb'."
        exit 1
    fi
}


DATE=$(date +'%Y-%m-%d')
pwd=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd ${pwd} && echo ${pwd}


if [[ -v model_configs["$model"] ]]; then
    IFS=" " read -ra config_values <<< "${model_configs["$model"]}"
    repo_name="${config_values[0]}"
    model_config="${config_values[1]}"
    model_worldir="${config_values[2]}"
else
    echo " '$model' 不存在于模型列表中"
    exit 1
fi

#开始训练
train(){
    cd ${pwd} && mkdir accuracy || echo "dir exists"
    cd accuracy
    clone ${repo_name}   #clone模型仓库，如果已存在则会checkout到main
    if [[ ${repo_name} == "mmdetection3d" ]] || [[ ${repo_name} == "mmyolo" ]];then clone mmdetection && export PYTHONPATH=${pwd}/accuracy/mmdetection:$PYTHONPATH && echo $PYTHONPATH;fi
    cd ${pwd}/accuracy && build_dataset ${drive}  #创建数据集软链接
    echo $PYTHONPATH
    for env in $env_name;do
        if [ ! -f ${env_path}/${env} ];then
            echo "${env} not exist" && exit 1
        fi
        source ${env_path}/${env}
        export PYTHONPATH=${pwd}/accuracy/${repo_name}:$PYTHONPATH
        which python
        echo $PYTHONPATH
        cd ${pwd}/accuracy && python ${pwd}/accuracy.py ${env} ${drive} ${job_name} "${gpu_num}" ${slurm_par} ${repo_name} ${model_config} ${model_worldir} ${epoch}
        source ${env_path}/pat_deactivate
    done
}

#统计训练数据
report(){
    element_count=$(echo $env_name | wc -w)
    cd ${pwd}
    rm -rf report && mkdir report && cp accuracy_template.md report/accuracy_${DATE}.md
    for env in $env_name;do
        source ${env_path}/${env}
        if [ $drive = 'cuda' ];then
            GPU_MODEL=`srun -p ${slurm_par} nvidia-smi --query-gpu=gpu_name --format=csv,noheader|head -n1`
            SYSTEM=`srun -p ${slurm_par} cat /etc/centos-release`
            python ${pwd}/report_deps.py ${pwd}/report/accuracy_${DATE}.md ${env} #获取环境使用的依赖版本
        elif [[ $drive = 'camb' ]]; then
            GPU_MODEL=`srun -p ${slurm_par} cnmon info |grep 'Product Name'|head -n1|awk -F ':' '{print $2}'`
            SYSTEM=`srun -p ${slurm_par} cat /etc/centos-release`
            python ${pwd}/report_deps.py ${pwd}/report/accuracy_${DATE}.md ${env} #获取环境使用的依赖版本
        fi
        if [ $element_count -eq 1 ]; then #循环到最后一个环境时修改Markdown文件，及统计训练数据
            sed -i "s/{SYSTEM}/${SYSTEM}/g" ${pwd}/report/accuracy_${DATE}.md
            sed -i "s/{GPU_MODEL}/${GPU_MODEL}/g" ${pwd}/report/accuracy_${DATE}.md
            sed -i "s/{GPU_LIST}/${gpu_num}/g" ${pwd}/report/accuracy_${DATE}.md
            sed -i "s/{DIPU_ENV}/${env_name}/g" ${pwd}/report/accuracy_${DATE}.md
            sed -i "s/{DATE}/${DATE}/g" ${pwd}/report/accuracy_${DATE}.md
            echo $GPU_MODEL $SYSTEM
            python ${pwd}/report_accuracy.py ${pwd}/report/accuracy_${DATE}.md ${pwd}/accuracy/DIPU_accuracy/${env}/${gpu_num}/${model_worldir} ${env} ${gpu_num} ${model}
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