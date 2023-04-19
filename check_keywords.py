import os
import sys

KEYWORDS = ["SecretKey0123456789", "SecretKey"]  # 需要检查的关键字列表


def is_text_file(file_path):
    """
    判断文件是否为文本文件
    """
    try:
        with open(file_path, 'rb') as f:
            f.read(1024)
        return True
    except:
        return False


def search_keyword(file_path, keywords):
    """
    在指定文件中搜索关键字
    """
    try:
        with open(file_path, "r") as f:
            print(file_path)
            content = f.read()
        for keyword in keywords:
            if keyword in content:
                print(f"文件 {file_path} 中包含关键字：{keyword}")
                sys.exit(1)
    except UnicodeDecodeError:
        pass


def search_directory(directory, keywords):
    """
    在指定目录及其子目录下搜索关键字
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.basename(file_path) == 'check_keywords.py' and is_text_file(file_path):
                search_keyword(file_path, keywords)


if __name__ == "__main__":
    search_directory(".", KEYWORDS)  # 搜索当前目录下所有文件中的关键字

