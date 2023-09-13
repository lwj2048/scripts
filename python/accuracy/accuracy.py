import os
import sys
import subprocess as sp
import time
import multiprocessing

if len(sys.argv) != 10:
    print("传入参数数量不对")
    sys.exit(1)

env_name = sys.argv[1]
device_type = sys.argv[2]
job_name = sys.argv[3]
gpu_requests = sys.argv[4].split()
slurm_par = sys.argv[5]
repo_name = sys.argv[6]
model_config = sys.argv[7]
model_worldir = sys.argv[8]
epoch = sys.argv[9]

print("job_name:{},slurm_par:{},gpu_requests:{}".format(job_name, slurm_par, gpu_requests))
error_flag = multiprocessing.Value('i',0) #if encount error
print("now pid!!!!:",os.getpid(),os.getppid())
print("python path: {}".format(os.environ.get('PYTHONPATH', None)), flush = True)


def run_cmd(cmd):
    cp = sp.run(cmd, shell = True, encoding = "utf-8")
    if cp.returncode != 0:
        error = "Some thing wrong has happened when running command [{}]:{}".format(cmd, cp.stderr)
        raise Exception(error)


def process_one_iter(gpu, repo_name, model_config, model_worldir):
    begin_time = time.time()
    if("mm" in repo_name):
        train_path = repo_name + "/tools/train.py"
        config_path = repo_name + "/configs/" + model_config
        work_dir = "--work-dir=./DIPU_accuracy/" + env_name + '/' + gpu + '/' + model_worldir
    elif("DI" in repo_name):
        train_path = repo_name+"/"+model_config
        config_path = ""
        work_dir = ""
    else:
        print("Wrong model info in  {}".format(repo_name), flush = True)
        exit(1)
    #判断是否有已经生成的权重文件，可以继续跑
    resume = ''
    if os.path.exists('./DIPU_accuracy/' + env_name + '/' + gpu + '/' + model_worldir):
        pth_files = [filename for filename in os.listdir('./DIPU_accuracy/' + env_name + '/' + gpu + '/' + model_worldir) if filename.endswith('.pth')]
        last_checkpoint_file = 'last_checkpoint' in os.listdir('./DIPU_accuracy/' + env_name + '/' + gpu + '/' + model_worldir)
        if pth_files or last_checkpoint_file:
            resume = '--resume'
    # 打印日志频率 保存权重数量
    other_arg = '--cfg-options default_hooks.logger.interval=100  default_hooks.checkpoint.max_keep_ckpts=3 default_hooks.checkpoint.save_best=auto '
    if device_type == 'cuda':
        if(model_config == "stable_diffusion/stable-diffusion_ddim_denoisingunet_infer.py"):
            cmd_train = "srun --job-name={} --partition={}  --gres=gpu:{} --cpus-per-task=5 --mem=16G --time=40 sh mmagic/configs/stable_diffusion/stable-diffusion_ddim_denoisingunet_one_iter.sh".format(job_name, slurm_par, gpu)
        else:
            cmd_train = "srun --job-name={} --partition={}  --gres=gpu:{} --cpus-per-task=5 --mem=16G  python -u  {} {} {} {} {}".format(job_name, slurm_par, gpu, train_path, config_path, work_dir, other_arg,  resume)
    else:
        cmd_train = "srun --job-name={} --partition={}  --gres=mlu:{}  python -u  {} {} {} {} {}".format(job_name, slurm_par, gpu, train_path, config_path, work_dir, other_arg, resume)

    print("============================begin train {} model==========================".format(model_config), flush = True)
    print(job_name, slurm_par, gpu, train_path, config_path, work_dir, other_arg, resume)
    run_cmd(cmd_train)

    end_time = time.time()
    run_time = round(end_time - begin_time)
    hour = run_time // 3600
    minute = (run_time - 3600 * hour) // 60
    second = run_time - 3600 * hour - 60 * minute
    print ("The running time of {} :{} hours {} mins {} secs".format(model_config, hour, minute, second), flush = True)


if __name__=='__main__':
    for gpu in gpu_requests:
        process_one_iter(gpu, repo_name, model_config, model_worldir)

