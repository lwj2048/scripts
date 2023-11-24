import os
import sys
import subprocess as sp
import time
import yaml
import multiprocessing


env_name = sys.argv[1]
device_type = sys.argv[2]
job_name = sys.argv[3]
gpu_requests = sys.argv[4].split()
slurm_par_arg = sys.argv[5:]
slurm_par = ' '.join(slurm_par_arg)
print("job_name:{},slurm_par:{},gpu_requests:{}".format(job_name, slurm_par, gpu_requests))
error_flag = multiprocessing.Value('i',0) #if encount error
print("now pid!!!!:",os.getpid(),os.getppid())
print("python path: {}".format(os.environ.get('PYTHONPATH', None)), flush = True)
train_batch_size = {
    'resnet': '32',
    'swin_transformer': '64',
    'vision_transformer':  '64',
    'efficientnet': '32',
    'mobilenetv3': '128',
    'mobilenetv2': '32',
    'convnext': '128',
    'detr':'2',
    'yolov3': '8',
    'ssd': '8',
    'fcos': '2',
    'retinanet': '2',
    'mask_rcnn': '2',
    'faster_rcnn': '2',
    'dyhead': '2',
    'hrnet': '64',
    'tsn': '32',
    'crnn': '64',
    'dbnet': '16',
    'deeplabv3': '2',
    'deeplabv3plus': '2',
    'unet': '4',
    'pspnet': '2',
    'yolov5': '2',
    'pointpillars': '6'
}

def run_cmd(cmd):
    cp = sp.run(cmd, shell = True, encoding = "utf-8")
    if cp.returncode != 0:
        error = "Some thing wrong has happened when running command [{}]:{}".format(cmd, cp.stderr)
        raise Exception(error)


def process_one_iter(model_info,gpu):
    begin_time = time.time()
    model_info_list = model_info['model_cfg'].split()
    if(len(model_info_list) < 3 or len(model_info_list) > 4):
        print("Wrong model info in  {}".format(model_info), flush = True)
        exit(1)

    p1 = model_info_list[0]
    p2 = model_info_list[1]
    p3 = model_info_list[2]
    p4 = model_info_list[3] if len(model_info_list) == 4 else ""
    if "_".join(p3.split("_")[1:]) in train_batch_size:
        batch_size_arg = "--cfg-options default_hooks.logger.interval=1 train_dataloader.batch_size={}".format(train_batch_size["_".join(p3.split("_")[1:])])
    else:
        batch_size_arg = "--cfg-options default_hooks.logger.interval=1"
    if("mm" in p1):
        train_path = p1 + "/tools/train.py"
        config_path = p1 + "/configs/" + p2
        work_dir = "--work-dir=./DIPU_benchmark/" + env_name + '/' + gpu + '/' + p3
        opt_arg = p4
        package_name = "mmlab"
    elif("DI" in p1):
        train_path = p1+"/"+p2
        config_path = ""
        work_dir = ""
        opt_arg = ""
        package_name = "diengine"
    else:
        print("Wrong model info in  {}".format(model_info), flush = True)
        exit(1)
    os.environ['ONE_ITER_TOOL_STORAGE_PATH'] = os.getcwd()+"/DIPU_benchmark/" + env_name + '/' + gpu + '/'  + p3
    if device_type == 'cuda':
        if(p2 == "stable_diffusion/stable-diffusion_ddim_denoisingunet_infer.py"):
            cmd_run_one_iter = "srun --job-name={} --partition={}  --gres=gpu:{} --cpus-per-task=5 --mem=16G --time=40 sh mmagic/configs/stable_diffusion/stable-diffusion_ddim_denoisingunet_one_iter.sh".format(job_name, slurm_par, gpu)
        else:
            print(job_name, slurm_par, gpu, train_path, config_path, work_dir, opt_arg, batch_size_arg)
            cmd_run_one_iter = "srun --job-name={} --partition={}  --gres=gpu:{} --cpus-per-task=5 --mem=16G --time=40 python -u  {} {} {} {} {}".format(job_name, slurm_par, gpu, train_path, config_path, work_dir, opt_arg, batch_size_arg)
    else:
        cmd_run_one_iter = "srun --job-name={} --partition={}  --gres=mlu:{} --time=40 python -u  {} {} {} {} {}".format(job_name, slurm_par, gpu, train_path, config_path, work_dir, opt_arg, batch_size_arg)

    print("============================begin train {} model==========================".format(p2), flush = True)
    print(job_name, slurm_par, gpu, train_path, config_path, work_dir, opt_arg)
    run_cmd(cmd_run_one_iter)

    end_time = time.time()
    run_time = round(end_time - begin_time)
    hour = run_time // 3600
    minute = (run_time - 3600 * hour) // 60
    second = run_time - 3600 * hour - 60 * minute
    print ("The running time of {} :{} hours {} mins {} secs".format(p2, hour, minute, second), flush = True)


if __name__=='__main__':
    curPath = os.path.dirname(os.path.realpath(__file__))
    yamlPath = os.path.join(curPath, "DIPU/scripts/ci/test_one_iter_model_list.yaml")
    original_list_f = open(yamlPath, 'r', encoding = 'utf-8')
    original_list_cfg = original_list_f.read()
    original_list_d = yaml.safe_load(original_list_cfg)
    try:
        original_list = original_list_d[device_type]
    except:
        print("The device is not supported!", flush = True)
        exit(1)

    #exclude_keywords = ['DI-engine', 'mmagic']
    #original_list = [item for item in original_list if not any(keyword in item['model_cfg'] for keyword in exclude_keywords)]  #排除模型
    choose_keywords = ['mobilenetv2', 'resnet', 'retinanet', 'faster_rcnn', 'yolov3', 'unet', 'pspnet', 'hrnet', 'tsn', 'pointpillars']
    original_list = [item for item in original_list if any('workdirs_' + keyword in item['model_cfg'] for keyword in choose_keywords)]  #选中模型
    length = len(original_list)

    print("model num:{}".format(length), flush = True)
    for gpu in gpu_requests:
        for i in original_list:
            process_one_iter(i,gpu)
