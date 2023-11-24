import os
import sys
import importlib.util


def add_row_to_table(model_name,batch_size): #batch_size信息写入Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    table_start = None
    table_end = None
    new_content = []

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith(f"| {table_name}"):
            table_start = i
        if table_start is not None and line.startswith("| ----------"):
            table_end = i
            break

    if table_start is None or table_end is None:
        return content

    new_content.extend(lines[:table_end + 1])
    new_content.append(f"| {model_name} | {batch_size} |")
    new_content.extend(lines[table_end + 1:])

    updated_content = '\n'.join(new_content)
    if updated_content != content:
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Markdown table batch_size updated successfully!")

def check_string_in_file(model_name,batch_size): #判断文件中是否已经存在此batch_size信息
    check_model_name = "| " + str(model_name)
    with open(md_file, 'r',encoding='utf-8') as file:
        file_content = file.read()
        if check_model_name not in file_content:
            add_row_to_table(model_name,batch_size)


def process_directory(directory):
    for root, dirs, files in os.walk(directory): #当前正在遍历的文件夹的路径,第一次遍历是dire
        for env in dirs: #subdir是directory下的文件夹，第一次遍历为环境名,每个环境文件夹下都会遍历一边
            subdir_path = os.path.join(root, env)
            digit_subdirs = [num for num in os.listdir(subdir_path) if num.isdigit()] #遍历env下文件夹，过滤出GPU文件夹
            digit_subdirs.sort(key=int) #数字文件夹排序
            if digit_subdirs:
                smallest_subdir = digit_subdirs[0] #取最小数值文件夹
                gpu_path = os.path.join(subdir_path, smallest_subdir) #GPU数量文件夹
                for modeldir in os.listdir(gpu_path): #遍历模型文件夹
                    model_path = os.path.join(gpu_path, modeldir)
                    for logdir in os.listdir(model_path):
                        if logdir.startswith("2023"): #获取以2023开头的日志文件夹
                            logdir_path = os.path.join(model_path, logdir)
                            vis_data_path  = os.path.join(logdir_path, 'vis_data')
                            config_path = os.path.join(vis_data_path, 'config.py')
                            if os.path.exists(config_path):  #判断配置文件 vis_data/config.py是否存在
                               spec = importlib.util.spec_from_file_location("config", config_path) #读取配置
                               config = importlib.util.module_from_spec(spec)
                               spec.loader.exec_module(config)
                               batch_size = config.train_dataloader["batch_size"]
                               #print("_".join(modeldir.split("_")[1:]), batch_size)
                               check_string_in_file("_".join(modeldir.split("_")[1:]), batch_size)



if __name__ == "__main__":
    md_file = sys.argv[1]
    benchmark_dir = sys.argv[2]
    table_name = "model_name"
    process_directory(benchmark_dir)

