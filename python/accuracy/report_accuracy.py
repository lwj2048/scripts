import os
import sys, re
import importlib.util


def get_batchsize(model_path):
    batch_size = ''
    for logdir in os.listdir(model_path):
        if logdir.startswith("2023"):  # 检查子文件夹是否以"2023"开头,日志文件夹
            logdir_path = os.path.join(model_path, logdir)
            config_path = os.path.join(logdir_path, 'vis_data/config.py')
            if os.path.exists(config_path):
                spec = importlib.util.spec_from_file_location("config", config_path)  # 读取配置
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                batch_size = config.train_dataloader["batch_size"]
    return batch_size


def get_checkpoint(model_path):
    # 列出目录中的文件
    for logdir in os.listdir(model_path):
        if logdir.startswith("2023"):
            logdir_path = os.path.join(model_path, logdir)
            file_list = os.listdir(logdir_path)
    # 筛选以"2023"开头的log文件
    logfile = [filename for filename in file_list if filename.startswith('2023') and filename.endswith('.log')]
    # 打印符合条件的文件名
    print(logfile)
    log_path = os.path.join(logdir_path, logfile[-1])
    with open(log_path, 'r') as file:
        lines = file.readlines()
    last_match_index = -1  # 初始化变量来存储最后一个匹配行的索引
    for i, line in enumerate(lines):  # 最后一个匹配行的索引
        if 'The best checkpoint with' in line:
            last_match_index = i
    if last_match_index != -1:
        last_match_line = lines[last_match_index]
        match = re.search(r'\b\d+\.\d+\b', last_match_line)
        if match:
            value = match.group()
            accuracy_info = "\n在 {} 环境下 {} GPU跑 {} 模型,精度为 {} batch_size为 {}".format(env, gpu, model, value, batch_size)
            with open(md_file, 'r+') as file:
                content = file.read()
                content = content.replace('{MODEL}', model)
                content = content.replace('{BATCH_SIZE}', str(batch_size))
                content = content.replace('{ACCURACY}', value)
                file.seek(0)  # 移动文件指针到文件开头
                file.truncate()  # 清空文件内容
                file.write(content)

        else:
            print("通过 'The best checkpoint with' 未找到匹配的精度值")
    else:
        print("模型暂未跑完，未能获取到精度信息")


if __name__ == "__main__":
    md_file = sys.argv[1]
    modeldir = sys.argv[2]
    env = sys.argv[3]
    gpu = sys.argv[4]
    model = sys.argv[5]
    batch_size = get_batchsize(modeldir)
    get_checkpoint(modeldir)



