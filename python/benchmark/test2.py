import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO



# 用于为每个模型绘图的函数
def plot_model(env, type):
    if type == "throughput":
        ylabel = 'Throughput (img/s)'
        # 计算吞吐量数据
        data_info = [
            [(float(data[env][gpu_count][model_name]["batch_size"]) * int(gpu_count)) / float(data[env][gpu_count][model_name]["time"]) for model_name in model_names] for gpu_count in gpu_counts
        ]
    print(data_info[1])

    num_model_name = len(model_names)
    num_gpu_configs = len(data_info)
    bar_width = 0.8 / num_gpu_configs
    index = np.arange(num_model_name)
    bars = []
    for i in range(num_gpu_configs):
        bars.append(plt.bar(index + i * bar_width, data_info[i], width=bar_width, label=f'{gpu_counts[i]} GPU(s)'))
    plt.title(f'Average {type} ({env})')
    plt.xlabel('model')
    plt.ylabel(ylabel)
    plt.xticks(index + (bar_width * num_gpu_configs) / 2 - bar_width / 2, model_names)
    #
    plt.ylim(0, max([max(times) for times in data_info]) * 1.3)  # 增加 y 轴高度
    plt.legend()

    # 添加 数值 标签
    def add_labels(bars_group, offset=0):
        for bars_subset in bars_group:
            for bar in bars_subset:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, height + offset, f'{height:.4f}', ha='center', va='bottom')

    add_labels(bars)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')  # 将图像保存到内存
    buf.seek(0)
    im = Image.open(buf)
    plt.clf()

    im_resized = im.resize((400, 300), Image.LANCZOS)  # 调整图像大小

    im_resized.save(f'{type}_{env}.png', 'PNG')  # 保存调整后的图像
    buf.close()


# 遍历文件夹
def traverse_folder(folder_path):
    #获取路径中report后面的子路径，用于添加到Markdown文件中为相对路径
    path_parts = folder_path.split("/")
    latest_path = path_parts.index("report")
    relative_path = "/".join(path_parts[latest_path + 1:])

    for root, dirs, files in os.walk(folder_path):
        images = {"time": [], "memory": [], "throughput": []}
        for file in files:
            if file.endswith(".png"):
                file_path = os.path.join(relative_path, file)
                process_image(file_path, images)
        print(images)
        insert_images(images)

# 处理图片
def process_image(file_path, images):
    file_name = os.path.basename(file_path)
    if file_name.startswith("time"):
        images["time"].append(file_path)
    elif file_name.startswith("memory"):
        images["memory"].append(file_path)
    elif file_name.startswith("throughput"):
        images["throughput"].append(file_path)

# 插入图片
def insert_images(images):
    with open(md_file, "a", encoding="UTF-8") as f:
        for category, image_list in images.items():
            print(category,image_list)
            if image_list:
                insert_title(f"性能测试{category}结果可视化", f)
                insert_image(image_list,f)

# 插入标题
def insert_title(title, file):
    file.write(f"\n## {title}\n")

# 插入图片
def insert_image(file_path,file):
    for item in file_path:
        file.writelines(f"![avatar]({item})")




if __name__ == "__main__":
    # imgdir = sys.argv[1]  #保存图片路径
    # filename = sys.argv[2]  #读取的json文件
    # md_file = sys.argv[3]   #输出报告的Markdown文件
    with open('test2.json', 'r') as file:
        data = json.load(file)        # 加载文件内容到一个 Python 对象（在这里是一个字典）
    environments = list(data.keys())    # 提取所有环境
    gpu_counts = sorted(list(set(k for v in data.values() for k in v.keys())))    # 提取所有 GPU 数量
    model_names = sorted(set(k for v in data.values() for models in v.values() for k in models.keys()))     # 提取所有模型名字
    # 为每个模型绘制图
    for model_name in model_names:
        plot_model(model_name, 'time')   #保存平均时间图像
        plot_model(model_name, 'memory')  #保存平均内存图像
        plot_model(model_name, 'throughput')  #保存吞吐量图像
    # last_directory = os.path.basename(imgdir) #获取相对Markdown的文件路径
    # traverse_folder(imgdir) #写入Markdown文件
    # for env in environments:

