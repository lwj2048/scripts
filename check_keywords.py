import sys
import os

KEYWORDS = ["phantomjs.exe", "another_keyword"]


def check_file(file_path):
    _, filename = os.path.split(file_path)
    if filename == 'check_keywords.py':
        return
    if filename.endswith('.py'):
        print(filename)
        # 如果是 Python 文件，则使用 Python 解释器执行文件以检查关键字
        with open(file_path, "r") as f:
            file_contents = f.read()
        for keyword in KEYWORDS:
            if keyword in file_contents:
                print(f"{file_path}: {keyword} found!")
    else:
        # 如果不是 Python 文件，则直接使用 grep 命令检查关键字
        cmd = f"grep -q {'|'.join(KEYWORDS)} {file_path}"
        return_code = os.system(cmd)
        if return_code == 0:
            print(f"{file_path}: {' or '.join(KEYWORDS)} found!")


if __name__ == "__main__":
    file_path = sys.argv[1]
    check_file(file_path)
