#-- coding:UTF-8 --
import os
import sys
import json
import importlib.util

def update_and_save_json_data(env, gpu, mode, time, memory, batch_size):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if env not in data:
        data[env] = {}
    if gpu not in data[env]:
        data[env][gpu] = {}
    if mode not in data[env][gpu]:
        data[env][gpu][mode] = {}

    data[env][gpu][mode]['time'] = time
    data[env][gpu][mode]['memory'] = memory
    data[env][gpu][mode]['batch_size'] = batch_size

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def average_time_memory(filename):
    with open(filename, 'r') as file:
        file_content = file.readlines()

    total_time = 0
    total_memory = 0
    valid_lines = 0
    all_lines = len(file_content)

    if count_lines > all_lines:
        print("统计的行数超出了iter数")
        return None, None
    for line in file_content[-count_lines:]:
        line_dict = eval(line)
        if "time" in line_dict and "memory" in line_dict:
            total_time += line_dict["time"]
            total_memory += line_dict["memory"]
            valid_lines += 1

    if valid_lines == 0:
        return None, None

    average_time = total_time / valid_lines
    average_memory = total_memory / valid_lines

    return average_time, average_memory

def process_directory(directory):
    for root, dirs, files in os.walk(directory): #dirs:环境名文件夹
        for gpudir in dirs:
            if gpudir.isdigit():  #检查子文件夹是否为数字，GPU文件夹
                gpudir_path = os.path.join(root, gpudir)
                for modeldir in os.listdir(gpudir_path): #模型文件夹
                    model_path = os.path.join(gpudir_path, modeldir)
                    for logdir in os.listdir(model_path):
                        if logdir.startswith("2023"):  # 检查子文件夹是否以"2023"开头,日志文件夹
                            logdir_path = os.path.join(model_path, logdir)
                            vis_data_path  = os.path.join(logdir_path, 'vis_data') 
                            if os.path.exists(vis_data_path):
                                for subsubfile in os.listdir(vis_data_path):
                                    if subsubfile.startswith("2023") and subsubfile.endswith(".json"):  # 检查文件是否以".json"结尾
                                        logfile_path = os.path.join(vis_data_path, subsubfile)
                                        average_time, average_memory = average_time_memory(logfile_path)
                                        config_path  = os.path.join(vis_data_path, 'config.py')
                                        if os.path.exists(config_path):
                                            spec = importlib.util.spec_from_file_location("config", config_path) #读取配置
                                            config = importlib.util.module_from_spec(spec)
                                            spec.loader.exec_module(config)
                                            batch_size = config.train_dataloader["batch_size"]
                                        else:
                                            batch_size = None
                                        update_and_save_json_data(root.split("/")[-1], str(gpudir), "_".join(modeldir.split("_")[1:]),\
                                                                  str("{:.4f}".format(average_time)), str(average_memory), str(batch_size))
                                        print(root.split("/")[-1] + '#' + str(gpudir) + '#' + "_".join(modeldir.split("_")[1:]) + '#' + \
                                              str("{:.4f}".format(average_time)) + '#' + str(average_memory) + '#' + str(batch_size))

if __name__ == "__main__":
    filename = sys.argv[1]
    benchmark_dir = sys.argv[2]
    if len(sys.argv) == 4:
        count_lines = int(sys.argv[3])
    else:
        count_lines = 2
    start_directory = "mmlab_pack/DIPU_benchmark"
    process_directory(benchmark_dir)

